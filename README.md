<div align="center">

# Understanding the Evolution of <br> Vancouver's Business Landscape

</div>

## Summary

Strategic urban planning provides a framework for achieving socio-economic objectives driven by actionable and sustainable development. Centralized city plans serve to reach these objectives through the coordination of efforts from the government, the private sector, and the community. Importantly, by planning and anticipating a community’s future needs, city leaders are better able to allocate municipal spending, mitigate potential risks, and capitalize on opportunities.

In particular, developing an understanding of how Vancouver’s business landscape has evolved over time can provide insight into how to efficiently allocate the city’s resources and services. To achieve this we have established two main research objectives. 

* A machine learning model to predict whether a business will renew its licence, given a set of underlying factors.
* A broader geospatial summary of the evolution of Vancouver’s business landscape


## Table of Contents
- [Contributing](https://github.com/deetken/evan/blob/master/Contributing.md)
- [Contributors](#Contributors)
- [Data Requirements](#data-requirements)
- [Final Report](#Final-Report)
- [Usage](#usage)
- [Data Products](#data-products)
- [Package Dependencies](#package-dependencies)
- [Licence](https://github.com/deetken/evan/blob/master/LICENSE)


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


## Data Requirements

The primary dataset utilized in this project consists of all Vancouver Business Licence applications from 1997 to the current date. This data is made available as part of the city of Vancouver’s [Open Data Portal](https://opendata.vancouver.ca/pages/home/) and regulated under the terms of the [Open Government Licence – Vancouver](https://opendata.vancouver.ca/pages/licence/). The most pertinent features present in this dataset are business type, location, and number of employees.
In addition to the business licence dataset, the Canadian census surveys provide another important source of data for this project. The census data is hosted on the Vancouver Open Data Portal and provides demographic information, such as population density, average income, age distribution, and ethnicity. The current census dataset aggregates the demographic data by Vancouver neighbourhoods. In addition, due to the lack of employment and other important information in Vancouver census data in 2011, we use National Census data available on [Statistic Canada](https://www12.statcan.gc.ca/census-recensement/index-eng.cfm) for 2011.

Another data source we have is the parking meters and disability parking zone. These two data is also available at the Open Data Portal.
For the boundary data of the 22 Vancouver geological areas, we use the local_area_boundary data available on Vancouver's Open Data Portal.


## Final Report

The final report can be found [here](https://github.com/deetken/evan/blob/master/doc/final_report/final_report.pdf).


## Usage

To replicate the analysis performed in this project, clone this GitHub repository, install the required [dependencies](#package-dependencies) listed below, and follow the commands included in the README of the [source folder](https://github.com/deetken/evan/tree/master/src#usage) in your command line/terminal from the root directory of this project.


## Data Products

The final data product consists of a fully-reproducible machine learning model pipeline and a visualization dashboard (figure shown below) with the model embedded. The entire pipeline along with usage instructions and commands required to host the Dash dashboard are documented in this repository. Currently, the dashboard is only available to be viewed locally, but it can be easily deployed to Heroku or other cloud servers if public sharing is needed in the future.

The machine learning model pipeline automatically pre-processes, trains, performs hyperparameter tuning and uses a Light-GBM model to make predictions. The accuracy for the current model is 0.60 and the BNR recall is 0.64. Modelling results have been saved to the [results folder](https://github.com/deetken/evan/tree/master/results).

An integrated data product is desired to reflect the reality that predictive modelling of landscape evolution is a sophisticated task that cannot be well explained alone by a model. Cities are dynamic living organisms and associated datasets often contain both temporal and spatial dimensions. In order to aid collaboration and communication among different stakeholders in city planning or business decision-making, it is valuable to visualize these factors on top of Vancouver's physical structure.


![**Figure 1.** geospatial visualization of Vancouver's business landscape.](figures/dashboard_demo.png)


## Package Dependencies

### Python 3.7 and Python packages:

- altair==4.0.1
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
- lightgbm==2.3.1
- numpy==1.18.4
- openpyxl==3.0.4
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

- compare==0.2.6
- data.table==1.12.6
- docopt==0.6.1
- tidyverse==1.2.1
- rgdal==1.4.6
- timevis==0.5
- leaflet==2.0.3
