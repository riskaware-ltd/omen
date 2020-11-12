# To build image:  docker build --rm -t omen/geopandas .

# Bootstrap from miniconda3 base image (based on debian)
FROM continuumio/miniconda3:4.8.2

RUN mkdir -p /home/omen_validation

WORKDIR /home/omen_validation

# Install the necessary python packages within the base conda environment
RUN conda install python=3.7.6 matplotlib=3.2.1 descartes=1.1.0
RUN conda install -c conda-forge geopandas=0.7.0
RUN conda install -c conda-forge mplleaflet=0.0.5

RUN mkdir Python_source

# Copy the Python/Geopandas validation scripts into the container
ADD Python_source/*.py Python_source/

