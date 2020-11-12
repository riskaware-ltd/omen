"""
Script name: Calc_2D_MOE_GeoJSON.py
Author: Dr. Chris Dearden (Hartree Centre, STFC Daresbury Laboratory)
Date: March 2020
Purpose: Script to calculate validation metrics for oil spill dispersion models relative to satellite observations and/or coastal reports.
Both obs and model data must be in GeoJSON format. Both deterministic and probabilistic model output are supported. Model contours are assumed to
be cut-outs, such that they do not overlap with contours of a higher level.
Usage: ./Calc_2D_MOE_GeoJSON.py <obsFile> <modelFile> <modelType> <valType> [--noOilFile NOOILFILE] [--crs CRS] [-h]
        <obsFile>     - Required. Path (relative or full) to the GeoJSON file defining the oil detected within the satellite data
        <modelFile>   - Required. Path (relative or full) to the GeoJSON file containing the model prediction data.
                        This can be either deterministic or probabilistic output.
        <modelType>   - Required. Type of model output, either 'BE' (best estimate, aka deterministic) or 'Prob' (probabilistic)
        <valType>     - Required. Type of validation to be performed, either 'Satellite' or 'Coastal'
        <--noOilFile> - Optional. Used to specify the path to a file defining the region where no oil was detected in the satellite data.
                        If this is specified, any model output that lies outside this detection region will be excluded from the analysis.
        <--crs>       - Optional. Integer specifying the code of a particular coordinate reference system to convert to.
                        If not specified, the code will use the default value of 3857, which corresponds to WGS 84 (pseudo mercator projection).
                        See http://epsg.io/3857 for details
        <--help>      - Optional. Shows help text.

Output:
This script produces validation plots in png format. The principal metric for both coastal and satellite validation
is the 2-D Measure of Effectiveness (Warner et al, 2004, J. Appl. Met.). The result of the 2-D MOE calculation
is presented as a scatter plot, revealing the extent of the overlap between the model prediction
and the observations. In addition, skill scores based on area and centroid location are also calculated
for validation of 'best estimate' model output against satellite data. These results are also presented as a 2-D scatter plot.
Maps showing the predicted and observed oil spill areas/coastlines are also produced.
"""

##### IMPORT RELEVANT LIBRARIES

import argparse
from process_data import calc_poly_overlap, read_geojson
from plot_maps_metrics import plot_2D_MOE_scat, plot_area_maps, plot_coastal_maps
import mplleaflet as leaf
from calc_metrics import calc_2DMOE

#####


def main():

    ##### READ IN COMMAND LINE ARGUMENTS

    parser = argparse.ArgumentParser(
        description="""
        Purpose: Script to calculate validation metrics for EASOS model output with respect to observations from
        satellite measurements or coastal reports. Minimum input requirement is a pair of GeoJSON files valid at a given time instance,
        one containing the validation data (either from satellites or coastal reports) and the other the corresponding model prediction data.
        Each GeoJSON file should contain a geodataframe with geometries that define the oil spill area/extent.
        Both deterministic (i.e. 'Best Estimate') and probabilistic model output are supported. """,
        epilog="Example of use: ./Calc_2D_MOE_GeoJSON.py <obsFile> <modelFile> <modelType> <valType> [--noOilFile NOOILFILE] [--crs CRS] ",
    )
    parser.add_argument(
        "obsFile",
        help="Required. Absolute or relative path to observation data file in GeoJSON format",
        type=str,
    )
    parser.add_argument(
        "modelFile",
        help="Required. Absolute/relative path to model output file (either deterministic or probabilistic) in GeoJSON format",
        type=str,
    )
    parser.add_argument(
        "modelType",
        help="Required. Type of model output, either 'BE' (best estimate, aka deterministic) or 'Prob' (probabilistic). Model contours \
                            are assumed to be cut-outs, i.e. no overlap with contours of a higher level.",
        type=str,
    )
    parser.add_argument(
        "valType",
        help="Required. Type of validation to be performed, either 'Satellite' or 'Coastal'",
        type=str,
    )
    parser.add_argument(
        "--noOilFile",
        help="Optional path to a file in GeoJSON format defining the region where oil was not observed in the satellite image. \
                            If this is specified, any model output that lies outside this detection region will be excluded from the analysis.",
        type=str,
    )
    parser.add_argument(
        "--crs",
        help="Optional integer specifying the crs code to convert obs and model data to. Default value is 3857. \
                            See http://epsg.io/3857 for more details",
        type=int,
        default=3857,
    )

    args = parser.parse_args()
    obsFile = args.obsFile
    modelFile = args.modelFile
    modelType = args.modelType
    valType = args.valType
    noOilFile = args.noOilFile
    crs = args.crs

    #####

    ##### READ IN GEOJSON FILES, CHECK VALIDITY, AND RETURN AS GEODATAFRAMES

    oil, model, no_oil, casename, time, plevs = read_geojson(
        obsFile, modelFile, noOilFile, modelType, valType, crs
    )

    if valType == "Coastal":
        #  Do a basic plot of the model coastal prediction with the obs regions highlighted and save as a png file
        modelplot, ax = plot_coastal_maps(
            oil, model, casename, time, modelType, noOil=no_oil, levels=plevs
        )
        modelplot.savefig(
            "/media/Coastal_map_"
            + str(casename)
            + "_"
            + str(modelType)
            + "_"
            + str(time)
            + ".png",
            bbox_inches="tight",
        )
        if modelType == "BE":
            leaf.save_html(
                fig=ax.figure,
                fileobj="/media/Interactive_map_"
                + str(casename)
                + "_"
                + str(modelType)
                + "_"
                + str(time)
                + ".html",
            )

    #####

    ##### PREPARE AND UPDATE GEODATAFRAMES WITH OBS AREA, MODEL AREA AND OVERLAP AREA

    oil, model_known, overlap, plevs = calc_poly_overlap(
        oil, model, no_oil, casename, time, noOilFile, modelType, valType, crs
    )

    if overlap.empty:
        Aob = oil["obs_area"]
        Apr = model_known["area_full_contour"]
        print("Overlap geodataframe is empty; skipping 2-D MOE calculation")

    else:
        if valType == "Satellite":
            #  Produce a basic map of the obs, model and overlap regions and save in png format
            modelplot = plot_area_maps(
                oil, model_known, overlap, casename, time, modelType, levels=plevs
            )
            modelplot.savefig(
                "/media/Area_maps_"
                + str(casename)
                + "_"
                + str(modelType)
                + "_"
                + str(time)
                + ".png",
                bbox_inches="tight",
            )

        ##### CALCULATE THE 2-D MEASURE OF EFFECTIVENESS AND GENERATE PLOTS
        ##### For details, see Warner et al 2004., J. Appl. Met

        Aob = overlap["obs_area"]
        Apr = overlap["area_full_contour"]
        Aov = overlap["overlap_full_contour"]

        #  Call function to return x and y components of the 2-D MOE
        (x, y) = calc_2DMOE(Aob, Apr, Aov)

        #  Generate 2-D MOE space diagram and save in png format
        olevs = (overlap.contourlev).to_numpy()
        if modelType == "BE":
            MOEfig = plot_2D_MOE_scat(x, y, modelType, casename, time)
        elif modelType == "Prob":
            MOEfig = plot_2D_MOE_scat(x, y, modelType, casename, time, levels=olevs)

        MOEfig.savefig(
            "/media/2D_MOE_"
            + str(casename)
            + "_"
            + str(modelType)
            + "_"
            + str(valType)
            + "_"
            + str(time)
            + ".png",
            bbox_inches="tight",
        )

    #####

    ##### FOR SATELLITE VALIDATION AGAINST DETERMINISTIC OUTPUT, CALCULATE ADDITIONAL SKILL SCORES

    if valType == "Satellite" and modelType == "BE":
        from calc_metrics import calc_area_ss, calc_centroid_ss
        from plot_maps_metrics import plot_ss_scat, plot_centroid_map

        print("Area (in km^2) of observed spill is : ", Aob[0])
        print("Area (in km^2) of modelled spill is : ", Apr[0])

        #  Call function to calcluate Area Skill Score, Ass
        Ass = calc_area_ss(Aob[0], Apr[0])
        print("Area skill score is : ", Ass)

        #  Call function to calculate Centroid Skill Score, Css
        Css, obs_centroid, model_centroid, minpoint, maxpoint = calc_centroid_ss(
            oil, model_known
        )
        print("Centroid skill score is : ", Css)

        #  Plot the modelled and observed oil spill areas, with centroids and distances indicated
        centroidfig = plot_centroid_map(
            oil,
            obs_centroid,
            model_known,
            model_centroid,
            minpoint,
            maxpoint,
            casename,
            time,
        )
        centroidfig.savefig(
            "/media/Centroid_map_" + str(casename) + "_" + str(time) + ".png",
            bbox_inches="tight",
        )

        #  Proceed to plot skill score results on a scatter diagram
        SSfig = plot_ss_scat(Ass, Css, casename, time)
        SSfig.savefig(
            "/media/Skillscores_scatterplot_"
            + str(casename)
            + "_"
            + str(time)
            + ".png",
            bbox_inches="tight",
        )

    #####


if __name__ == "__main__":
    main()
