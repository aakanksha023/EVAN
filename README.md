<div align="center">

# Understanding the Evolution of <br> Vancouver's Business Landscape

</div>

## Summary

In the continuing age of digital revolution, data is used ubiquitously among industries and individuals. Everyday problems, such as finding the quickest route home and tracking food deliveries, have been effectively tackled by data. The same approach could be implemented in the public sector, helping to inform policy decisions and future planning. 

With COVID-19 governing our economy and lifestyle, it is critical to understand the evolution of the city’s neighbourhoods and leverage that to predict potential future outcomes. One way to approach this problem, is to track the evolution of businesses in Vancouver’s diverse neighbourhoods and develop/extract meaningful insights. 

To address this we have defined the following research questions for the project: 

* Will a business renew their license in the coming year?  
* Geospatial summary of Vancouver's business landscape


## Table of Contents
- [Contributing](https://github.com/deetken/evan/blob/master/Contributing.md)
- [Contributors](#Contributors)
- [How to use this repository](#how-to-use-this-repository)
- [Data Requirements](#data-requirements)
- [Usage](#usage)
- [Data Products](#data-products)
- [Examples](#examples)
- [Package Dependencies](#package-dependencies)
- [License](https://github.com/deetken/evan/blob/master/LICENSE)


## Contributing

Contributions are welcome! Read detailed instructions [here](https://github.com/deetken/evan/blob/master/Contributing.md)

### Contributors

UBC Data Science Team:

* Aakanksha Dimri
* Jasmine Qin
* Keanna Knebel
* Xinwen Wang

Mentor:

* Simon Goring

Deetken Team:

* Tom Reimer
* Kristiana Powell


## How to use this repository

Navigation of files and descriptions of directory structure in the repository. Specific commands will be given in Usage section and example usage will be given in Examples section. 


## Data Requirements

The primary dataset utilized in this project consists of all Vancouver Business Licence applications from 1997 to the current date. This data is made available as part of the city of Vancouver’s [Open Data Portal](https://opendata.vancouver.ca/pages/home/) and regulated under the terms of the [Open Government Licence – Vancouver](https://opendata.vancouver.ca/pages/licence/). The most pertinent features present in this dataset are business type, location, and number of employees.

In addition to the business licence dataset, the Canadian census surveys provide another important source of data for this project. The census data is hosted on the Vancouver Open Data Portal and provides demographic information, such as population density, average income, age distribution, and ethnicity. The current census dataset aggregates the demographic data by Vancouver neighbourhoods. As the project progresses, we may choose to further refine our model by obtaining census data aggregated at the postal code level.


## Usage

To replicate the analysis performed in this project, clone this GitHub repository, install the required [dependencies](#package-dependencies) listed below, and follow the commands included in the README of the [source folder](https://github.com/deetken/evan/tree/master/src#usage) in your command line/terminal from the root directory of this project.


## Data Products

*Description or screenshot of end products and where to find them*

The proposed final product consists of a data pipeline, as well as, a geospatial visualization of Vancouver's business landscape. Users will be able to locate a specific zone on the interactive map and view relevant descriptive information, such as business type distribution and census data [**figure 1**]. The data pipeline will pass processed input data of a specific business to a machine learning model and produce a predicted renewal probability.

![**Figure 1.** geospatial visualization of Vancouver's business landscape.](figures/dashboard_demo.png)

## Examples

*Specific illustration of how to use the end product*


## Package Dependencies

### Python 3.7 and Python packages:

altair==4.0.1
- Datetime==4.3
- dash==1.6.1
- dash-bootstrap-components==0.7.2
- dash-core-components==1.5.1
- dash-html-components==1.0.2
- docopt==0.6.2
- docutils==0.15.2
- eli5==0.10.1
- geopandas==0.7.0
- jupyter_dash==0.2.1
- jupyter_plotly_dash==0.4.2
- joblib==0.15.1
- json5==0.9.4
- joblib==0.15.1
- lightgbm==2.3.1
- numpy==1.18.4
- pandas==1.0.3
- progressbar2==3.51.3
- python-utils==2.4.0
- plotly==4.8.1
- re==2.2.1
- requests==2.23.0
- scikit-learn==0.22.1
- seaborn==0.10.1
- shap==0.34.0
- shapely==1.7.0
- zipp==3.1.0

### R 3.6 and R packages:

- data.table==1.12.6
- docopt==0.6.1
- tidyverse==1.2.1
- rgdal==1.4.6
- timevis==0.5
- leaflet==2.0.3
