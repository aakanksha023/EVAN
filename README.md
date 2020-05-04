# Forecasting the Evolution of Vancouver's Business Landscape

## Project Summary  

## Usage
### 1. Using Bash/Terminal 

To replicate the analysis performed in this project, clone this GitHub repository, install the required [dependencies](#package-dependencies) listed below, and run the following commands in your command line/terminal from the root directory of this project:

1. 01_download_data.py
```
python src/01_download_data.py --file_path="data/raw/" |
--filename_1="licence_1997_2012.csv" |
--url1="https://opendata.vancouver.ca/explore/dataset/business-licences-1997-to-2012/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B" |
--filename_2="licence_2013_current.csv" |
--url2="https://opendata.vancouver.ca/explore/dataset/business-licences/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B"
```

## Package Dependencies
### Python 3.7.3 and Python packages:

- pandas 
- docopt 

