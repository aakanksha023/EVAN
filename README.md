# Forecasting the evolution of Vancouver's Business landscape

`Evolving Vancouver Project`

(Description placeholder)

## Table of Contents
- [Contributing](#contributing)
- [Contributors](#Contributors)
- [How to use this repository](#how-to-use-this-repository)
- [Data Requirements](#data-requirements)
- [Usage](#usage)
- [Data Products](#data-products)
- [Examples](#examples)
- [Package Dependencies](#package-dependencies)
- [License](#license)

## Contributing

Contribution will not be open to public. Contributors please feel free to [open an issue](https://github.com/deetken/evan/issues/new) or send a pull request to report bugs or add features.

### Contributors

## How to use this repository

Navigations of files and descriptions of directory structure in the repository. Specific commands will be given in Usage section and example usage will be given in Examples section. 

## Data Requirements

Describe the data we are using and what data sources they are coming from.

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

## Data Products

Description or screenshot of end product(s) and where to find them.

## Examples

Specific illustration of how to use the end product.

## Package Dependencies
### Python 3.7.3 and Python packages:

- pandas 
- docopt 

## License
