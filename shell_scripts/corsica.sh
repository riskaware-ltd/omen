#!/bin/bash
#
# Script to automate the validation of Corsica case study using a Docker container
# Prior to running this script, please make sure you have built the Docker image
# using the supplied Dockerfile and the command below:
# 
# docker build --rm -t omen/geopandas .
#
# Then run this script from the top-level of the repository as follows:
#
# ./shell_scripts/corsica.sh
# 
# C. Dearden, 17/03/2020


# SET INPUT ARGUMENTS BELOW
#---------------------------------------------------------------------------------------------

# Specify which testcase sub-directory to use within 'validation_data' directory
export TESTCASE=Corsica

# Set the validation date (must match the format used in the geojson filenames)
export DATE=20181009T171452

# Select model output type - can be either 'BE' or 'Prob'
export modeltype="Prob"

# Set the coordinate reference system
export crs=3857


# DO NOT CHANGE ANYTHING IN THE LINES BELOW!
#----------------------------------------------------------------------------------------------
export valtype='Satellite'

CWD="$(pwd)"
export FILEPATH=$CWD/validation_data/$TESTCASE

echo "Filepath set to: " $FILEPATH
echo "Validation time: "$DATE
echo "Model output type: "$modeltype
echo "Validation method: "$valtype
echo "Coordinate reference system chosen: "$crs

export oilfile="$TESTCASE"_contour_geojson_detected_oil_"$DATE".geojson
echo "Oil observation file: "$oilfile

export nooilfile="$TESTCASE"_contour_geojson_detected_no_oil_"$DATE".geojson
echo "No oil observation file: "$nooilfile

if [ "$modeltype" == "Prob" ] ; then
   export modelfile="$TESTCASE"_contour_geojson_probability_"$DATE".geojson

elif [ "$modeltype" == "BE" ] ; then
   export modelfile="$TESTCASE"_contour_geojson_concentration_"$DATE".geojson

else
   echo "Model file not found"
   exit 1
fi

echo "Model output file: "$modelfile

# Run validation scipt, mounting $FILEPATH on host to /media inside the container
echo "Running validation script..."

docker run -it -v "$FILEPATH":/media omen/geopandas python3.7 Python_source/Calc_2D_MOE_GeoJSON.py \
                   /media/"$oilfile" /media/"$modelfile" $modeltype $valtype --noOilFile /media/"$nooilfile" --crs $crs  \
                   &> $FILEPATH/"$TESTCASE"_2D_MOE_"$valtype"_"$DATE"_"$modeltype"_crs_"$crs".log

echo "Done."
