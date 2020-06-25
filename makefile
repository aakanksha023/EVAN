# author: Jasmine Qin
# date: 2020-06-24

all : data/processed/05_feat_eng_test.csv \
data/processed/census_viz.csv \
data/processed/vis_model.csv \
data/processed/vis_licence.csv \
data/processed/vis_agg_licence.csv

# 01_download_data.py
data/raw/licence_1997_2012.csv \
data/raw/licence_2013_current.csv \
data/raw/census_2016.csv \
data/raw/census_2011.csv \
data/raw/census_2006.csv \
data/raw/census_2001.csv \
data/raw/local_area_boundary.geojson \
data/raw/parking-meters.csv \
data/raw/disability-parking.csv \
data/raw/14100096-eng.zip \
data/raw/14100327-eng.zip \
data/raw/vancouver_empolyment_2020.csv \
data/raw/census_boundaries_2011.zip \
data/raw/nhs_census_2011.zip : src/01_download/01_download_data.py src/01_download/urls.txt
	python3 src/01_download/01_download_data.py --file_path="data/raw" --urls="src/01_download/urls.txt"

# 02_split_licence.R
data/processed/combined_licences.csv \
data/processed/train.csv \
data/processed/validate.csv \
data/processed/test.csv : src/02_clean_wrangle/02_split_licence.R data/raw/licence_1997_2012.csv data/raw/licence_2013_current.csv
	Rscript src/02_clean_wrangle/02_split_licence.R --filepath_in="data/raw" \
--filepath_out="data/processed" \
--filename_1="licence_1997_2012.csv" \
--filename_2="licence_2013_current.csv"

# 03_clean_licence.py
data/processed/03_cleaned_train.csv : src/02_clean_wrangle/03_clean_licence.py data/processed/train.csv src/02_clean_wrangle/business_mapping_dictionary.csv
	python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/train.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_train.csv"

data/processed/03_cleaned_validate.csv : src/02_clean_wrangle/03_clean_licence.py data/processed/validate.csv src/02_clean_wrangle/business_mapping_dictionary.csv
	python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/validate.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_validate.csv"

data/processed/03_cleaned_test.csv : src/02_clean_wrangle/03_clean_licence.py data/processed/test.csv src/02_clean_wrangle/business_mapping_dictionary.csv
	python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/test.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_test.csv"

data/processed/03_cleaned_combined_licences.csv : src/02_clean_wrangle/03_clean_licence.py data/processed/combined_licences.csv src/02_clean_wrangle/business_mapping_dictionary.csv
	python3 src/02_clean_wrangle/03_clean_licence.py --file_path="data/processed/combined_licences.csv" \
--mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv" \
--save_to="data/processed/03_cleaned_combined_licences.csv"

# 04_clean_nhs.py
data/processed/nhs/ : src/02_clean_wrangle/04_clean_nhs.py data/raw/nhs_census_2011.zip data/raw/census_boundaries_2011.zip \
data/raw/local_area_boundary.geojson
	python3 src/02_clean_wrangle/04_clean_nhs.py --nhs_zip="data/raw/nhs_census_2011.zip" \
--ct_bound_zip="data/raw/census_boundaries_2011.zip" \
--area_file="data/raw/local_area_boundary.geojson" \
--file_path="data/processed/nhs/"

# 05_clean_census.py
data/processed/census_2001/ : src/02_clean_wrangle/05_clean_census.py data/raw/census_2001.csv
	python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2001.csv" \
--year="2001" \
--file_path="data/processed/census_2001"

data/processed/census_2006/ : src/02_clean_wrangle/05_clean_census.py data/raw/census_2006.csv
	python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2006.csv" \
--year="2006" \
--file_path="data/processed/census_2006"

data/processed/census_2011/ : src/02_clean_wrangle/05_clean_census.py data/processed/nhs/ data/raw/census_2011.csv
	python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2011.csv" \
--year="2011" \
--file_path="data/processed/census_2011"

data/processed/census_2016/ : src/02_clean_wrangle/05_clean_census.py data/raw/census_2016.csv
	python3 src/02_clean_wrangle/05_clean_census.py --census_file="data/raw/census_2016.csv" \
--year="2016" \
--file_path="data/processed/census_2016"

# 06_synthesis.py
data/processed/04_combined_train.csv : src/02_clean_wrangle/06_synthesis.py data/processed/03_cleaned_train.csv \
data/processed/census_2001/ data/processed/census_2006/ data/processed/census_2011/ data/processed/census_2016/
	python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_train.csv" \
--save_to="data/processed/04_combined_train.csv"

data/processed/04_combined_validate.csv : src/02_clean_wrangle/06_synthesis.py data/processed/03_cleaned_validate.csv \
data/processed/census_2001/ data/processed/census_2006/ data/processed/census_2011/ data/processed/census_2016/
	python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_validate.csv" \
--save_to="data/processed/04_combined_validate.csv"

data/processed/04_combined_test.csv : src/02_clean_wrangle/06_synthesis.py data/processed/03_cleaned_test.csv \
data/processed/census_2001/ data/processed/census_2006/ data/processed/census_2011/ data/processed/census_2016/
	python3 src/02_clean_wrangle/06_synthesis.py --path_in="data/processed/03_cleaned_test.csv" \
--save_to="data/processed/04_combined_test.csv"

# 07_feature_engineering.py
data/processed/05_feat_eng_train.csv : src/03_modelling/07_feature_engineering.py data/processed/04_combined_train.csv
	python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_train.csv" \
--save_to="data/processed/05_feat_eng_train.csv"

data/processed/05_feat_eng_validate.csv : src/03_modelling/07_feature_engineering.py data/processed/04_combined_validate.csv
	python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_validate.csv" \
--save_to="data/processed/05_feat_eng_validate.csv"

data/processed/05_feat_eng_test.csv : src/03_modelling/07_feature_engineering.py data/processed/04_combined_test.csv
	python3 src/03_modelling/07_feature_engineering.py --file_path="data/processed/04_combined_test.csv" \
--save_to="data/processed/05_feat_eng_test.csv"

# census_vis_synthesis.py
data/processed/census_viz.csv : src/04_visualization/census_vis_synthesis.py data/raw/local_area_boundary.geojson
	python3 src/04_visualization/census_vis_synthesis.py --path_in="data/processed/census" \
--path_out="data/processed/census_viz.csv" \
--area_file="data/raw/local_area_boundary.geojson"

# licence_vis_synthesis.py
data/processed/vis_model.csv data/processed/vis_licence.csv \
data/processed/vis_agg_licence.csv : src/04_visualization/licence_vis_synthesis.py \
data/processed/combined_licences.csv data/processed/03_cleaned_combined_licences.csv \
data/raw/parking-meters.csv data/raw/disability-parking.csv \
data/processed/05_feat_eng_train.csv data/processed/05_feat_eng_validate.csv
	python3 src/04_visualization/licence_vis_synthesis.py

clean : 
	rm -f data/processed/*.csv
	rm -f data/processed/nhs/*.csv
	rm -f data/processed/census_2001/*.csv
	rm -f data/processed/census_2006/*.csv
	rm -f data/processed/census_2011/*.csv
	rm -f data/processed/census_2016/*.csv
	rm -f data/raw/*.csv
	rm -f data/raw/*.zip
	rm -f data/raw/*.geojson
	rm -f data/raw/*.shp
	rm -f data/raw/*.shx
	rm -f data/raw/*.prj
	rm -f data/raw/*.dbf
	rm -f data/raw/*.pdf