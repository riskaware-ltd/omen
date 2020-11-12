import matplotlib as mpl
import matplotlib.pyplot as plot
import numpy as np


def plot_2D_MOE_scat(xval, yval, outputtype, casename, time, levels=None):
    #  Function to plot results from 2-D Measure of Effectiveness metric as a scatter plot
    #  On the plot, the desire is to get as close to the top right corner as possible
    #  Perfect agreement between obs and model would be a point with coordinates (1,1)
    #  No overlap at all between obs and model would be a point with coordinate (0,0)
    #  On the scatter diagram, if the point(s) lie beneath the red 1-2-1 line,
    #  it means that the the region of false positive exceeds the region of false negative.
    #  If the point(s) lie above the red 1-2-1 line, the region of false
    #  negative exceeds the region of false positive.
    #  Points that sit on the red 1-2-1 line mean that the predicted area has the same
    #  magnitude as the observed area, but they do not perfectly overlap,
    #  i.e. there is some spatial offset between the two. As the offset gets smaller,
    #  points will get closer to the top right corner of the scatter plot
    #
    #   Input arguments:
    #
    #   xval       - Pandas Series of floats denoting the x component of the 2-D MOE
    #   yval       - Pandas Series of floats denoting the y component of the 2-D MOE
    #   outputtype - String to denote type of model output, either 'BE' or 'Prob'
    #   casename   - String to denote the name of case study (used in plot title)
    #   time       - String specifying the validitity time of case study (used in plot title)
    #   levels     - 1-D numpy array for Probabilistic output, representing the contour levels to be plotted
    #
    #   Output arguments:
    #
    #   MOEfig - figure handle
    #
    #  C. Dearden, March 2020

    if outputtype == "BE":
        MOEfig, ax1 = plot.subplots(1, figsize=(8, 8))
        scat = ax1.scatter(xval, yval)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.plot([0, 1], [0, 1], color="red", linestyle="dashed")
        ax1.set_title(
            "2-D MOE space diagram\n" + str(casename) + ", valid at " + str(time)
        )
        ax1.set_xlabel("$x ( = A_{ov}/A_{ob})$", size=12)
        ax1.set_ylabel("$y ( = A_{ov}/A_{pr})$", size=12)

    elif outputtype == "Prob":
        MOEfig, ax1 = plot.subplots(1, figsize=(8, 8))
        cmap = plot.cm.coolwarm  # define the colormap

        # extract all colors from the chosen map
        cmaplist = [cmap(i) for i in range(cmap.N)]
        tag = levels

        # create the new map
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            "Custom cmap", cmaplist, cmap.N
        )

        # define the bins and normalize
        tagdiff = np.diff(tag)
        upperbound = tagdiff[len(tagdiff) - 1]
        bounds = np.append(tag, max(tag) + upperbound)

        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        #  Create scatter plot
        scat = ax1.scatter(xval, yval, c=tag, s=100, cmap=cmap, norm=norm)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.plot([0, 1], [0, 1], color="red", linestyle="dashed")
        ax1.set_title(
            "2-D MOE space diagram\n" + str(casename) + ", valid at " + str(time)
        )
        ax1.set_xlabel("$x ( = A_{ov}/A_{ob})$", size=12)
        ax1.set_ylabel("$y ( = A_{ov}/A_{pr})$", size=12)

        # create a second axes for the colorbar
        ax2 = MOEfig.add_axes([0.95, 0.1, 0.03, 0.8])
        cb = mpl.colorbar.ColorbarBase(
            ax2,
            cmap=cmap,
            norm=norm,
            spacing="proportional",
            ticks=bounds,
            boundaries=bounds,
            format="%1i",
        )
        ax2.set_ylabel("Probability level (%)", size=12)

    return MOEfig


def plot_ss_scat(Ass, Css, casename, time):
    #  Function to plot the Area Skill Score and Centroid Skill Score as a scatter plot
    #
    #   Input arguments:
    #
    #   Ass      - float in the range 0.0 to 1.0 representing the Area Skill Score
    #   Css      - float in the range 0.0 to 1.0 representing the Centroid Skill Score
    #   casename - string to identify the case study (used in title heading)
    #   time     - string denoting the validity time (used in title heading)
    #
    #   Output arguments:
    #
    #   SSfig - figure handle
    #
    #  C. Dearden, March 2020

    SSfig, ax1 = plot.subplots(1, figsize=(8, 8))
    scat = ax1.scatter(Ass, Css)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.plot([0, 1], [0, 1], color="red", linestyle="dashed")
    ax1.set_title(
        "Skill score space diagram\n" + str(casename) + ", valid at " + str(time)
    )
    ax1.set_xlabel("Area skill score", size=12)
    ax1.set_ylabel("Centroid skill score", size=12)

    return SSfig


def plot_centroid_map(oil, obsc, model, modc, minp, maxp, casename, time):
    #  Function to plot basic map showing the observed and predicted oil spill extents along with
    #  their centroid locations, the length scale of the observations, and the distance
    #  between centroids
    #
    #   Input arguments:
    #
    #   oil      - geodataframe containing the oil observations
    #   obsc     - Shapely Point object defining the coordinates of the centroid of the observed oil spill
    #   model    - geodataframe containing the deterministic model prediction
    #   modc     - Shapely Point object defining the coordinates of the centroid of the predicted oil spill
    #   minp     - Shapely Point object defining the coordinates of the lower corner of a bounding box surrounding the observations.
    #   maxp     - Shapely Point object defining the coordinates of the upper corner of a bounding box surrounding the observations.
    #   casename - string to identify the case study (used in title heading)
    #   time     - string denoting the validity time (used in title heading)
    #
    #   Output arguments:
    #
    #   centroidfig - figure handle
    #
    #  C. Dearden, March 2020

    centroidfig, axc = plot.subplots(1, figsize=(12, 12))
    model.plot(ax=axc, cmap="viridis")
    oil.plot(ax=axc, color="gray")
    axc.scatter(modc.x, modc.y, color="red")
    axc.scatter(obsc.x, obsc.y, color="yellow")

    #  Plot line between the centroids in light blue
    centroid_x = [obsc.x, modc.x]
    centroid_y = [obsc.y, modc.y]
    axc.plot(centroid_x, centroid_y, "k--", color="lightblue")

    #  Plot orange line to indicate the lengthscale of the observations
    obsscale_x = [minp.x, maxp.x]
    obsscale_y = [maxp.y, minp.y]
    axc.plot(obsscale_x, obsscale_y, "k--", color="orange")

    #  Add title heading
    axc.set_title(
        str(casename)
        + ", valid at "
        + str(time)
        + "\n \
                Map showing centroid point locations (observed = yellow; predicted = red)\n \
                Lengthscale of observed spill (orange dashed line); distance between centroids (blue dashed line) "
    )

    return centroidfig


def plot_area_maps(oil, model_known, overlap, casename, time, outputtype, levels=None):
    #  Function to plot basic map showing the observed oil spill extent, predicted oil extent,
    #  and the overlapping region between the two. Produces plots for both best estimate
    #  and probabilistic model output.
    #
    #   Input arguments:
    #
    #   oil         - geodataframe containing the oil observations
    #   model_known - geodataframe containing the model prediction
    #   overlap     - geodataframe with geometry that defines the overlap area between obs and model
    #   casename    - String to identify the case study (used in title heading)
    #   time        - String to denote the validity time (used in title heading)
    #   outputtype  - String to denote type of model output, either 'BE' or 'Prob'
    #   levels      - 1-D numpy array for Probabilistic output, representing the contour levels to be plotted
    #
    #   Output arguments:
    #
    #   modelplot - figure handle
    #
    #  C. Dearden, March 2020

    modelplot, ax = plot.subplots(figsize=(10, 10))

    if outputtype == "BE":
        model_known.plot(ax=ax)
        oil.plot(ax=ax, color="gray")
        overlap.plot(ax=ax, color="red")
        ax.set_title(
            "Observed oil (grey), predicted oil (blue), overlap region (red)\n"
            + str(casename)
            + ", valid at "
            + str(time)
        )
    elif outputtype == "Prob":
        model_known.plot(ax=ax, cmap="viridis")
        oil.plot(ax=ax, color="gray")
        overlap.plot(ax=ax, cmap="inferno_r")
        ax.set_title(
            "Observed oil (grey) with predicted oil and overlap region\n"
            + str(casename)
            + ", valid at "
            + str(time)
        )

        # create a second axes for the colorbar

        cmap = plot.cm.viridis  # define the colormap

        # extract all colors from the chosen map
        cmaplist = [cmap(i) for i in range(cmap.N)]
        tag = levels

        # create the new map
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            "Custom cmap", cmaplist, cmap.N
        )

        # define the bins and normalize
        tagdiff = np.diff(tag)
        upperbound = tagdiff[len(tagdiff) - 1]
        bounds = np.append(tag, max(tag) + upperbound)

        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        ax2 = modelplot.add_axes([0.95, 0.2, 0.03, 0.6])
        cb = mpl.colorbar.ColorbarBase(
            ax2,
            cmap=cmap,
            norm=norm,
            spacing="proportional",
            ticks=bounds,
            boundaries=bounds,
            format="%1i",
        )
        ax2.set_ylabel("Probability level (%)", size=12)

    return modelplot


def plot_coastal_maps(oil, model, casename, time, outputtype, noOil=None, levels=None):
    #  Function to plot basic coastal map showing the observed beaching and predicted beaching regions.
    #  Produces plots for both deterministic and probabilistic model output.
    #
    #   Input arguments:
    #
    #   oil         - geodataframe containing the coastal oil observations
    #   model       - geodataframe containing the model prediction
    #   casename    - String to identify the case study (used in title heading)
    #   time        - String to denote the validity time (used in title heading)
    #   outputtype  - String to denote type of model output, either 'BE' or 'Prob'
    #   noOil       - geodataframe defining coastlines unaffected by oil in the coastal reports (set to 'None' if not available)
    #   levels      - 1-D numpy array for Probabilistic output, representing the contour levels to be plotted
    #
    #   Output arguments:
    #
    #   modelplot - figure handle
    #   ax        - axis object
    #
    #  C. Dearden, March 2020

    modelplot, ax = plot.subplots(figsize=(12, 12))

    if outputtype == "BE":
        if noOil is None:
            oil.plot(ax=ax, color="red", linewidth=2.0)
            model.plot(ax=ax, color="black")
            ax.set_title(
                "Observed oil (red), predicted oil (black)\n"
                + str(casename)
                + ", valid at "
                + str(time)
            )
        else:
            noOil.plot(ax=ax, color="blue", linewidth=2.0)
            oil.plot(ax=ax, color="red", linewidth=2.0)
            model.plot(ax=ax, color="black")
            ax.set_title(
                "Observed oil (red), predicted oil (black), no oil region (blue)\n"
                + str(casename)
                + ", valid at "
                + str(time)
            )
    elif outputtype == "Prob":
        model.plot(ax=ax, cmap="viridis", linewidth=2.0)
        ax.set_title(
            "Probabilistic model output\n" + str(casename) + ", valid at " + str(time)
        )

        # create a second axes for the colorbar

        cmap = plot.cm.viridis  # define the colormap

        # extract all colors from the chosen map
        cmaplist = [cmap(i) for i in range(cmap.N)]
        tag = levels

        # create the new map
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            "Custom cmap", cmaplist, cmap.N
        )

        # define the bins and normalize
        tagdiff = np.diff(tag)
        upperbound = tagdiff[len(tagdiff) - 1]
        bounds = np.append(tag, max(tag) + upperbound)

        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        ax2 = modelplot.add_axes([0.1, 0.3, 0.8, 0.02])
        cb = mpl.colorbar.ColorbarBase(
            ax2,
            cmap=cmap,
            norm=norm,
            orientation="horizontal",
            spacing="proportional",
            ticks=bounds,
            boundaries=bounds,
            format="%1i",
        )
        ax2.set_xlabel("Probability level (%)", size=12)

    ax.set_xlabel("Degrees Longitude", size=12)
    ax.set_ylabel("Degrees Latitude", size=12)

    return modelplot, ax
