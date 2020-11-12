def calc_2DMOE(Aob, Apr, Aov):
    #  Function to calculate the x and y components of the Two Dimensional Measure of Effectiveness (Warner et al 2004, J. Appl. Met.)
    #
    #   Input arguments:
    #
    #   Aob - Pandas Series of float data type, defining the area of observed oil spill extent
    #   Apr - Pandas Series of float data type, defining the area of predicted oil spill extent
    #   Aov - Pandas Series of float data type, defining the overlap area between the observed oil and model prediction
    #
    #   Output arguments:
    #
    #   x - Pandas Series of float(s) in the range 0.0 to 1.0, equal to the ratio of overlap area to observed area
    #   y - Pandas Series of float(s) in the range 0.0 to 1.0, equal to the ratio of overlap area to predicted area
    #
    #   C. Dearden, March 2020

    print("Observed oil area:\n ", str(Aob[0]))
    print("Total predicted oil area:\n ", str(Apr[0]))
    print("Oil overlap area:\n ", str(Aov[0]))

    x = Aov / Aob
    x_out = round(x, 4)
    y = Aov / Apr
    y_out = round(y, 4)
    sizex = len(x_out)

    print("2-D MOE values are: ")
    for i in range(sizex):
        print("(" + str(x_out[i]), str(y_out[i]) + ")")

    #  Calculate areas of false negative (Afn) and false positive (Afp) for completeness
    Afn = (1 - x) * Aob
    Afp = (1 - y) * Apr
    print("Area of false negative:\n ", str(Afn))
    print("Area of false positive:\n ", str(Afp))

    return x, y


def calc_area_ss(Aob, Apr):
    #  Function to calculate and return the Area Skillscore for deterministic model output
    #  relative to satellite observations of detected oil spills
    #
    #   Input arguments:
    #
    #   Aob - Pandas Series of float data type, defining the area of observed oil spill extent
    #   Apr - Pandas Series of float data type, defining the area of predicted oil spill extent
    #
    #   Output arguments:
    #
    #   Ass - float in the range 0.0 to 1.0, equal to the Area Skill Score
    #
    #  C. Dearden, March 2020

    #  First, calculate the area index (the normalised area difference between model and obs)
    Area_index = abs(Apr - Aob) / Aob

    #  Use Area_index to calculate the area skill score, for an area threshold of one
    #  This means that for the model to have some skill, the error in the predicted oil spill area
    #  must not exceed the magnitude of the observed oil spill area
    A_thr = 1

    if Area_index < A_thr:
        Ass = 1 - (Area_index / A_thr)
    elif Area_index >= A_thr:
        Ass = 0

    return Ass


def calc_centroid_ss(oil, model):
    #  Function to calculate and return the Centroid Skillscore for deterministic model output
    #  relative to satellite observations of detected oil spills
    #
    #   Input arguments:
    #
    #   oil      - GeoPandas geodataframe containing the oil observations
    #   model    - GeoPandas geodataframe containing the deterministic model prediction
    #
    #   Output arguments:
    #
    #   Css            - float in the range 0.0 to 1.0, equal to the Centroid Skill Score
    #   obs_centroid   - Shapely Point object defining the centroid position of the polygon representing the observed oil
    #   model_centroid - Shapely Point object defining the centroid position of the polygon representing the predicted oil
    #   minpoint       - Shapely Point object representing the lower corner of a bounding box surrounding the observations.
    #                  - Used by the plotting function 'plot_centroid_map' to indicate the lengthscale of the observations
    #   maxpoint       - Shapely Point object representing the upper corner of a bounding box surrounding the observations.
    #                  - Used by the plotting function 'plot_centroid_map' to indicate the lengthscale of the observations
    #
    #  C. Dearden, March 2020

    from shapely.geometry import Point

    #  First, let's compute the Centroid Skillscore
    #  Start by calculating the centroid locations of the obs and modelled oil extents
    obs_centroid = oil.geometry.centroid[0]
    model_centroid = model.geometry.centroid[0]

    #  Now use the distance function to take min distance between the two centroids
    centroid_dist = model_centroid.distance(other=obs_centroid)
    print(
        "Distance (in km) between observed and modelled centroid is : ",
        centroid_dist / 1000.0,
    )

    #  Now use the bounds function to return the coordinates of a bounding box around the observed oil extent
    obsbounds = oil.geometry.bounds

    #  Store the points that make up the diagonal of the bounding box;
    #  we will use these points to calculate the observed length scale
    minpoint = Point(obsbounds.minx[0], obsbounds.miny[0])
    maxpoint = Point(obsbounds.maxx[0], obsbounds.maxy[0])

    #  Now take the distance between the two points and use this as the length scale of the observed area
    obslengthscale = minpoint.distance(other=maxpoint)
    print("Lengthscale (in km) of observed spill is : ", obslengthscale / 1000.0)

    #  Calculate the centroid index, i.e. the normalised centroid displacement
    C_index = centroid_dist / obslengthscale

    #  Use centroid index to calculate centroid skill score, assuming a threshold of one
    #  This means that for the model to have some skill, the error in the centroid location
    #  must not exceed the magnitude of the observed oil spill length scale. This criteria
    #  can be relaxed by choosing a higher threshold value
    C_thr = 1  #  Define centroid threshold used to calculate area skill score
    if C_index < C_thr:
        Css = 1 - (C_index / C_thr)
    elif C_index >= C_thr:
        Css = 0

    return Css, obs_centroid, model_centroid, minpoint, maxpoint
