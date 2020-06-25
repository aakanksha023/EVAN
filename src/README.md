## Analysis and Product Development


## Usage

To replicate the analysis performed in this project, clone this GitHub repository, install the required [dependencies](#package-dependencies) listed below, and run the following commands in your command line/terminal from the root directory of this project:

### 1. Using makefile
To generate all required datasets for the model and dashboard:
```{bash}
make all
```

To view dashboard locally:
```{bash}
python3 app.py
```

To remove generated files:
```{bash}
make clean
```

### 2. Using Bash/Terminal

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
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_train.csv"

# validation set
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/validate.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_validate.csv"

# test set
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/test.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_test.csv"

# combined dataset (train+validation+test)
python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/combined_licences.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_combined_licences.csv"

# 4. 04_clean_nhs.py

python3 src/02_clean_wrangle/04_clean_nhs.py --nhs_zip="data/raw/nhs_census_2011.zip" \
--ct_bound_zip="data/raw/census_boundaries_2011.zip" \
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

# 6. 06_synthesis.py

# train set
python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_train.csv" \
--save_to="data/processed/04_combined_train.csv"

# validation set
python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_validate.csv" \
--save_to="data/processed/04_combined_validate.csv"

# test set
python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_test.csv" \
--save_to="data/processed/04_combined_test.csv"
```

**Part 3: Modelling**

```{bash}
# 7. 07_feature_engineering.py

# train set
python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_train.csv" \
--save_to="data/processed/05_feat_eng_train.csv"

# validation set
python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_validate.csv" \
--save_to="data/processed/05_feat_eng_validate.csv"

# test set
python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_test.csv" \
--save_to="data/processed/05_feat_eng_test.csv"
```

**Part 4: Visualization**
```{bash}
# 8. census_vis_synthesis.py

python3 src/04_visualization/census_vis_synthesis.py --path_in="data/processed/census" \
--path_out="data/processed/census_viz.csv" \
--area_file="data/raw/local_area_boundary.geojson"

# 9. licence_vis_synthesis.py

python3 src/04_visualization/licence_vis_synthesis.py

# 10. app.py

python3 app.py

```

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
