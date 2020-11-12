import os
import pandas as pd
import geopandas as gpd
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def read_geojson(obsFile, modelFile, noOilFile, modelType, valType, crs):
    #  Function to read in geojson files, perform validity checks and return
    #  the data as geopandas geodataframes ready for further processing.
    #
    #   Input arguments are:
    #
    #   obsFile   - absolute/relative path to oil observation file
    #   modelFile - absolute/relative path to model prediction file
    #   noOilFile - absolute/relative path to observation file that defines the region where no oil was detected (enter 'None' if not available)
    #   modelType - Model output type. Either 'BE' for best estimate, or 'Prob' for probabilistic
    #   valType   - Type of obs data to validate against, either 'Satellite' or 'Coastal'
    #   crs       - Integer specifying the coordinate reference system to convert the data to.
    #
    #   Output arguments are:
    #
    #   oil      - geodataframe containing the oil observations
    #   model    - geodataframe containing the model prediction
    #   no_oil   - geodataframe defining the observation region where no oil was detected
    #   casename - Name of case study, as determined from dataframe header
    #   time     - Validity time of case study, determined from dataframe header
    #   plevs    - Contour/probability levels, used to create colorbar label when plotting
    #
    #  C. Dearden, March 2020

    ##### CHECK VALIDITY OF THE INPUT ARGUMENTS

    assert os.path.exists(obsFile), "obsFile does not exist"
    assert os.path.exists(modelFile), "modelFile does not exist"
    assert modelType == "BE" or modelType == "Prob", "Invalid modelType argument"
    assert valType == "Satellite" or valType == "Coastal", "Invalid valType argument"

    if crs is not 3857:
        assert type(crs) == int, "crs is not an integer: %r" % crs

    if noOilFile is not None:
        assert os.path.exists(noOilFile), "noOilFile does not exist"

    #####

    ##### READ IN THE INPUT GEOJSON FILES AND CHECK CONTENTS

    #  Read the oil obs file first
    oil = gpd.read_file(obsFile, driver="geojson")
    print("obsFile has been read in as ", type(oil))

    #  Now read model geojson file
    model = gpd.read_file(modelFile, driver="geojson")
    print("modelFile has been read in as ", type(model))

    #  Read the no oil file, if specified
    if noOilFile is not None:
        no_oil = gpd.read_file(noOilFile, driver="geojson")
        print("noOilFile has been read in as ", type(no_oil))
    else:
        no_oil = None

    #  Check geometries contain correct data types
    check_geom_types(oil, valType)
    check_geom_types(model, valType)
    if noOilFile is not None:
        check_geom_types(no_oil, valType)

    if modelType == "BE":
        #  BE output should have no more than 5 thickness levels based on the Bonn agreement oil appearance code
        #  See https://odnature.naturalsciences.be/mumm/en/national/ba-oil-appearance-code
        assert len(model["geometry"]) <= 5, (
            "Model geodataframe contains unexpected number of levels ("
            + str(len(model["geometry"]))
            + ")"
        )

    #  Find out how many rows of data there are in the geodataframes
    print("Number of levels in obsFile : ", len(oil["geometry"]))
    print("Number of levels in modelFile : ", len(model["geometry"]))
    if noOilFile is not None:
        print("Number of levels in noOilFile : ", len(no_oil["geometry"]))

    #  Obtain test case name and validity time (used later for plot labelling)
    if "test-case" in model.columns:
        casename = model["test-case"][0]
        print("Test case is : ", casename)
    else:
        casename = None

    if "time" in model.columns:
        time = model["time"][0]
        print("Model validity time is : ", time)
    else:
        time = None

    #  Sort model data by concentraton/probability level
    model = model.sort_values(by="level")
    model.rename(columns={"level": "contourlev"}, inplace=True)
    plevs = (model.contourlev).to_numpy()

    #####

    return oil, model, no_oil, casename, time, plevs


def calc_poly_overlap(
    oil, model, no_oil, casename, time, noOilFile, modelType, valType, crs
):
    #  Function to read in geodataframes and update them to include new geoseries representing the observed oil
    #  spill area, the predicted oil spill area, and the overlap area. Note this function assumes
    #  that the model contours are passed in as cut-outs, i.e. hollowed out so that they do
    #  not overlap with contours of a higher level
    #
    #   Input arguments:
    #
    #   oil       - geodataframe containing the oil observations
    #   model     - geodataframe containing the model prediction
    #   no_oil    - geodataframe defining the observation region where no oil was detected (enter 'None' if not available)
    #   casename  - Name of case study, as determined from dataframe header
    #   time      - Validity time of case study, as determined from dataframe header
    #   noOilFile - absolute/relative path to observation file that defines the region where no oil was detected (enter 'None' if not available)
    #   modelType - Model output type. Either 'BE' for best estimate, or 'Prob' for probabilistic
    #   valType   - Type of obs data to validate against, either 'Satellite' or 'Coastal'
    #   crs       - Integer specifying the coordinate reference system to convert the data to.
    #
    #   Output arguments:
    #
    #   oil         - updated oil geodataframe to include polygon area (in km^2)
    #   model_known - updated model geodataframe to include polygon area (in km^2)
    #   overlap     - new geodataframe containing the overlap area between observed oil and model prediction (in km^2)
    #   plevs       - Contour/probability levels, used to create colorbar label when plotting
    #
    #  C. Dearden, March 2020

    #  Convert coordinate reference system according to value of crs
    oil = oil.to_crs({"init": "epsg:" + str(crs)})
    model = model.to_crs({"init": "epsg:" + str(crs)})
    if noOilFile is not None:
        no_oil = no_oil.to_crs({"init": "epsg:" + str(crs)})

    if modelType == "BE":
        #  Dissolve contour levels for BE case into a single geometry
        #  This is only necessary for the BE case, since for Prob we want to keep the
        #  contour levels as separate geometries
        if "name" in model.columns:
            model = model.dissolve(by="name")
        elif "test-case" in model.columns:
            model = model.dissolve(by="test-case")
        else:
            model[
                "dummy"
            ] = "dummy"  #  Last resort; introduce dummy column to dissolve geometries
            model = model.dissolve(by="dummy")

    #  Do the same for observations for completeness
    oil = oil.dissolve(by="test-case")

    #  And again for the no_oil obs (if specified)
    if noOilFile is not None:
        no_oil = no_oil.dissolve(by="test-case")

    if valType == "Coastal":
        #  To calculate the overlap between predicted and observed coastlines, first the linestrings
        #  need to be converted to polygons, so they are compatible with the overlay function
        #  The conversion to polygons is achieved using the geopandas 'buffer' function
        bufwidth = 5  #  Width of polygon in metres
        oil["geometry"] = oil.geometry.buffer(bufwidth)
        model["geometry"] = model.geometry.buffer(bufwidth)
        if noOilFile is not None:
            no_oil["geometry"] = no_oil.geometry.buffer(bufwidth)

    #  Before we go any further, we need to check if noOilFile has been specified, and if so,
    #  we use this to exclude any model data that lies outside the known detection limit of the observations
    if noOilFile is not None:
        #  Combine the oil and no_oil geodataframes into a single geodataframe
        df_list = [oil, no_oil]
        obs_combined = gpd.GeoDataFrame(pd.concat(df_list, sort=True))
        #  Dissolve the combined obs into a single multipolygon
        obs_combined = obs_combined.dissolve(by="test-case")
        obs_combined["data"] = "Known observation region"
        obs_combined.drop(
            "level", axis=1, inplace=True
        )  #  remove redundant level column
        obs_combined.crs = {"init": "epsg:" + str(crs)}
        #  Use overlay to clip the model prediction according to the bounds of the observations
        model_known = gpd.overlay(model, obs_combined, how="intersection", keep_geom_type=False)
    else:
        model_known = model

    #  Sort again to ensure correct order after use of overlay
    model_known = model_known.sort_values(by="contourlev")
    plevs = (model_known.contourlev).to_numpy()

    #####

    ##### USE GEOPANDAS FUNCTIONS TO CALCULATE OIL AREAS AND THE OVERLAP BETWEEN OBS AND MODEL

    #  Now calculate the area (in km^2) of each model contour and add as a new GeoSeries (column)
    model_known["contour_cutout_area"] = model_known["geometry"].area / 10 ** 6

    #  Calculate the full area enclosed by each contour level
    #  This is necessary since the contours are saved as cut-outs
    #  NB - this has a null effect for BE cases, since we have already dissolved the thickness contours
    #  into a single full area contour. But it is necessary for Prob cases where we require the full area
    #  enclosed by each individual probability level
    model_known["area_full_contour"] = model_known.loc[
        ::-1, "contour_cutout_area"
    ].cumsum()[::-1]

    #  Now add a new GeoSeries (column) to the oil dataframe containing the area of the multipolygon in km^2
    oil["obs_area"] = oil["geometry"].area / 10 ** 6

    #  Create a new geodataframe containing the overlap between predicted and observed oil
    #  For probabilistic output, this will calculate the area of overlap for each prob level individually
    overlap = gpd.overlay(model_known, oil, how="intersection", keep_geom_type=False)
    overlap["overlap_area"] = overlap["geometry"].area / 10 ** 6

    #  For each contour level, calculate the full area of overlap with obs
    overlap["overlap_full_contour"] = overlap.loc[::-1, "overlap_area"].cumsum()[::-1]

    #####

    return oil, model_known, overlap, plevs


def check_geom_types(geom, valType):
    #  Function to check that input geometries within geodataframes contain the correct data types
    #  Ensures that Polygons are used for Satellite-based validation,
    #  and LineStrings are used for coastal-based validation
    #
    #   Input arguments:
    #
    #   geom      - geodataframe to be checked
    #   valType   - Type of validation to be performed, either 'Satellite' or 'Coastal'
    #
    #  C. Dearden, March 2020

    if valType == "Satellite":
        assert (
            geom.geom_type[0] is "MultiPolygon" or geom.geom_type[0] is "Polygon"
        ), "Unexpected geometry type in input geodataframe"
    elif valType == "Coastal":
        assert (
            geom.geom_type[0] is "MultiLineString" or geom.geom_type[0] is "LineString"
        ), "Unexpected geometry type in input geodataframe"
