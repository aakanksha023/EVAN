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

# train set
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/train.csv" \
--mapping_csv="src/01_download/business_mapping_dictionary.csv" \
--save_to="data/processed/03_train_cleaned.csv"

# validation set
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/validate.csv" \
--mapping_csv="src/01_download/business_mapping_dictionary.csv" \
--save_to="data/processed/03_validate_cleaned.csv"

# test set
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/test.csv" \
--mapping_csv="src/01_download/business_mapping_dictionary.csv" \
--save_to="data/processed/03_test_cleaned.csv"

# combined dataset (train+validation+test)
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/combined_licences.csv" \
--mapping_csv="src/01_download/business_mapping_dictionary.csv" \
--save_to="data/processed/03_combined_licences_cleaned.csv"

# 4. 04_clean_nhs.py

python3 src/02_clean_wrangle/04_clean_nhs.py --nhs_zip="data/raw/nhs_census_2011.zip" \
--ct_bound_zip="data/raw/census_boundaries_2011.zip" \
--nhs_file="99-004-XWE2011001-401-BC.csv" \
--ct_file="data/raw/gct_000b11a_e.shp" \
--area_file="data/raw/local_area_boundary.geojson" \
--file_path="data/processed/nhs/"

# 5. 05_clean_census.py

# census year 2001
python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2001.csv" \
    --year="2001" \
    --file_path="data/processed/census_2001"

# census year 2006
python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2006.csv" \
    --year="2006" \
    --file_path="data/processed/census_2006"

# census year 2011
python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2011.csv" \
    --year="2011" \
    --file_path="data/processed/census_2011"

# census year 2016
python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2016.csv" \
    --year="2016" \
    --file_path="data/processed/census_2016"

# 6. 04_synthesis.py

# train set
python3 src/02_clean_wrangle/04_synthesis.py --file_path="src/02_clean_wrangle/synthesis_script_input.txt" \
--save_to1="data/processed/04_combined_train.csv" \
--save_to2="data/processed/paking_meter_vis.csv" \
--save_to3="data/processed/disability_parking_vis.csv" \
--save_to4="data/processed/train_licence_vis.csv"
```

**Part 3: Modelling**

```{bash}
# 7. 05_feature_engineering.py

# train set
python3 src/03_modelling/05_feature_engineering.py --file_path="data/processed/04_combined_train.csv" \
--save_to="data/processed/05_feat_eng_train.csv"

# validation set
python3 src/03_modelling/05_feature_engineering.py --file_path="data/processed/04_combined_validation.csv" \
--save_to="data/processed/05_feat_eng_validation.csv"

# test set
python3 src/03_modelling/05_feature_engineering.py --file_path="data/processed/04_combined_test.csv" \
--save_to="data/processed/05_feat_eng_test.csv"
```

**Part 4: Visualization**
```{bash}

```

## Package Dependencies

### Python 3.7 and Python packages:

- csv
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
