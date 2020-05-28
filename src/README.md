## Analysis and Product Development


## Usage

### 1. Using Bash/Terminal 

To replicate the analysis performed in this project, clone this GitHub repository, install the required [dependencies](#package-dependencies) listed below, and run the following commands in your command line/terminal from the root directory of this project:

**Part 1: Download Data**  
```{bash}
# 1. 01_download_data.py

python3 src/01_download/01_download_data.py --file_path="data/raw" --urls="src/01_download/urls.txt"
```

**Part 2: Data Cleaning and Wrangling**  
```{bash}
# 2. 02_split_licence.R

Rscript src/02_clean_wrangle/02_split_licence.R --filepath_in="data/raw" \
--filepath_out="data/processed" \
--filename_1="licence_1997_2012.csv" \
--filename_2="licence_2013_current.csv"


# 3. 03_clean_licence.py

python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/train.csv" \
--save_to="data/processed/train_cleaned.csv"
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/validate.csv" \
--save_to="data/processed/validate_cleaned.csv"
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/test.csv" \
--save_to="data/processed/test_cleaned.csv"
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/combined_licences.csv" \
--save_to="data/processed/combined_licences_cleaned.csv"

# 4. 04_synthesis.py

python3 src/02_clean_wrangle/04_synthesis.py --file_path="src/02_clean_wrangle/synthesis_script_input.txt" --save_to1="data/processed/combined_train.csv" --save_to2="data/processed/paking_meter_vis.csv" --save_to3="data/processed/disability_parking_vis.csv" --save_to4="data/processed/licence_vis.csv"
```

**Part 3: Modelling**

```{bash}

```

**Part 4: Visualization**
```{bash}
# 5. 05_kepler_vis.py
python3 src/04_visualization/05_kepler_vis.py --file_path1="data/processed/licence_vis.csv" --file_path2="data/processed/disability_parking_vis.csv" --file_path3="data/processed/paking_meter_vis.csv" 
```

## Package Dependencies

### Python 3.7 and Python packages:

- datetime
- docopt
- eli5
- geopandas
- json
- keplergl
- lightgbm
- matplotlib.pyplot
- numpy
- os
- pandas 
- re
- requests
- seaborn
- shap
- sklearn
- time
- warnings
- xgboost
- zipfile

### R 3.6 and R packages:

- data.table
- docopt
- tidyverse
- rgdal
- timevis
- leaflet
