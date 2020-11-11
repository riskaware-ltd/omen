# OMEN: Oil Model EvaluatioN

OMEN is a Python-based code for validating oil spill dispersion models against satellite imagery and coastal report data. Validation is based on the 2-D Measure of Effectiveness performance metric (Warner et al 2004, Journal of Applied Meteorology) and two skill scores based on the area and centroid of a predicted oil spill. The code is designed to read and process geospatial data in geojson format, using the GeoPandas library. Further details of the metrics, including examples of their application to two historic test cases, are given in the manuscript by Dearden et al ('Performance measures for validation of oil spill dispersion models based on satellite and coastal report data', prepared for submission to the IEEE Journal of Oceanic Engineering). Model and observational datasets from both test cases are also included within this repository to demonstrate the use of the code, and to allow the results of the Dearden et al manuscript to be reproduced. 

This code was originally developed by the STFC Hartree Centre, UK in collaboration with Riskware Ltd through the Analysis 4 Innovators (A4I) programme, funded by Innovate UK. STFC Hartree Centre and Innovate UK are a part of UK Research and Innovation. 

### Overview of repository content

`Dockerfile`: A recipe for building a containerised conda environment to run the OMEN software.

`Python_source` directory: Contains four python modules which between them provide the necessary functions for calculating the validation metrics and plotting the results. The purpose of each file is described below:

  - `Calc_2D_MOE_GeoJSON.py`: Main script used to perform the validation based on the 2-D Measure of Effectiveness metric (2-D MOE). Makes use of functions contained within the module files below:

  - `process_dataframes.py`: Contains functions used to read in the geojson files, check their validity, and prepare the data into geodataframes in order to calculate the areas of the modelled and observed spills and their overlap.

  - `calc_metrics.py`: Contains functions used to calculate the 2-D MOE components, as well as skill score metrics based on centroid location and area magnitude.

  - `plot_maps_metrics.py`: Contains functions responsible for plotting the results from the validation metrics.

  Details of the purpose of each function, along with their inputs and outputs, are specified in the header comments of each file.

`validation_data` directory: contains the observational data (satellite measurements and/or coastal reports) and model data in GeoJSON format for the two historical test cases presented in the study of Dearden et al. Model output is supplied in both deterministic and probabilistic forms. The deterministic data contain up to 5 contour levels which represent the thickness of the oil spill at each location (with thickness categorized into the ranges 0.04 - 0.30 µm, 0.3 - 5.0 µm , 5 - 50 µm, 50 - 200 µm and >200 µm), which is based on the bonn agreement oil appearance code (see https://odnature.naturalsciences.be/mumm/en/national/ba-oil-appearance-code). The probabilistic files each contain multiple contour (probability) levels indicating where the probability of the oil exceeding 0.04 µm is. The model contours are supplied as 'cut-outs', i.e. they do not overlap with contours of higher level. This is important to note since the validation scripts assume that all model contours are supplied in this way.

`shell_scripts` directory: Example bash scripts used to automate the running of the Python code within the Docker container.

### Quick-start instructions for running the validation code

The validation software has been designed to run inside a containerised conda environment, initiated by running a bash script from within the `shell_scripts` directory on a host system. The shell scripts make use of environment variables that allow the user to specify the date and type of validation to be performed (e.g. deterministic or probabilistic model output; satellite or coastal observations). The shell scripts are responsible for spinning up the docker container (with the `validation_data` directory on the host system bind-mounted within the container for read/write file access), before calling the main python control script. The container instance is automatically closed down after the validation is complete.

##### 1) Build the Docker image

To build the docker image, from the top-level directory of the repository, type:

`docker build --rm -t omen/geopandas .`

##### 2) Configuration of shell scripts

Next, change to the sub-directory containing the bash scripts (`cd shell_scripts`). This sub-directory contains two files, one for each test case considered in the Dearden et al study. For the purpose of this example, we shall run the validation for the Corsica test case. First, it is helpful to inspect the contents of the file `corsica.sh`. Within this file it is possible to specify the date to run the validation for via the `DATE` environment variable (note this must match the timestamp format used in the filenames of the input geojson files). It is also possible to set `modeltype` to either `BE` for deterministic model output, or `Prob` for probabilistic model output. For the purpose of this example, no changes are necessary, so the file can be closed before returning to the top-level directory of the repository (`cd ../`).

##### 3) Run the script

Run the Corica shell script to initiate the container and invoke the Python code by typing:

`./shell_scripts/corsica.sh`

Validation plots will be written to the `validation_data/Corsica` sub-directory on the host system. Validation of the Corsica test case is performed against satellite data, but the software is also capable of validating against coastal report data as well (as in the supplied 'Sea Empress' test case example).


