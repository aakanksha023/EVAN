# author: Keanna Knebel
# date: 2020-06-02

"""
This script performs data wrangling and synthesis of NHS data
with local area boundary datasets. This script serves to aggregate
the NHS data to the neighborhood level in order to be consistent
with the census data.

Usage: src/02_clean_wrangle/04_clean_nhs.py --nhs_zip=<nhs_zip> \
--ct_bound_zip=<ct_bound_zip> \
--nhs_file=<nhs_file> \
--ct_file=<ct_file> \
--area_file=<area_file> \
--file_path=<file_path>

Options:
--nhs_zip=<nhs_zip>                 Path to the zip file containing
                                    the NHS data.
--ct_bound_zip=<ct_bound_zip>       Path to the zip file containing
                                    the census tract boundaries.
--nhs_file=<nhs_file>               Path to the csv file containing the NHS
                                    data for the province of interest.
--ct_file=<ct_file>                 Path to the .shp file containing the
                                    census tract boundaries data.
--area_file=<area_file>             Path to the geojson file containing the
                                    neighborhood boundaries data.
--file_path=<file_path>             Path to the exported files.

"""

# load packages
from docopt import docopt
import pandas as pd
import geopandas as gpd
import os
import zipfile

opt = docopt(__doc__)


def main(nhs_zip, ct_bound_zip, nhs_file, ct_file, area_file, file_path):

    # read NHS data from zip file
    with zipfile.ZipFile(nhs_zip, "r") as z:
        with z.open(nhs_file) as f:
            nhs = pd.read_csv(f,
                              encoding='latin-1',
                              usecols=[0, 2, 3, 4, 5, 6, 8, 10, 12])

    # extract and read boundary data from zip file
    z = zipfile.ZipFile(ct_bound_zip)
    z.extractall(path="data/raw/")
    nhs_boundaries = gpd.read_file(ct_file)

    # read in local areas boundaries
    areas = gpd.read_file(area_file)

    # select only census tracts in Vancouver
    van_bound = nhs_boundaries[nhs_boundaries['CMANAME'] == 'Vancouver']

    # select and rename needed columns
    van_bound = van_bound[['CTUID', 'geometry']]
    van_bound.rename(columns={'CTUID': 'Geo_Code'}, inplace=True)
    van_bound.Geo_Code = van_bound.Geo_Code.apply(lambda x: float(x))
    van_bound['LocalArea'] = 'None'
    van_bound.reset_index(drop=True, inplace=True)

    # find local area of the census tract based on geom
    local_areas = list(van_bound['LocalArea'])
    for row in range(len(local_areas)):
        for area in range(len(areas.name)):
            if areas.geometry[area].contains(van_bound.geometry[row].centroid):
                local_areas[row] = str(areas.name[area])
                break
    # name local areas based on geom
    van_bound['LocalArea'] = local_areas
    van_bound = van_bound[van_bound['LocalArea'] != 'None']

    # merge local area to NHS data
    merged = nhs.merge(van_bound, on='Geo_Code')
    merged = merged.iloc[:, [-1, 2, 4, 5, 6, 7, 8]]
    merged.Characteristic = merged.Characteristic.apply(lambda x: (x.lstrip()).rstrip())

    # get lists of unique topics and areas
    topics = list(merged['Topic'].unique())
    local_areas = list(merged['LocalArea'].unique())
    census_tracts = list(merged['CT_Name'].unique())

    # ensure all variables have a unique name
    for ct in census_tracts:
        for topic in topics:
            tract = merged['CT_Name'] == ct
            tp = merged['Topic'] == topic
            ind = list(merged[tract & tp].Characteristic.index)
            for var in range(len(merged[tract & tp].Characteristic)):
                merged.Characteristic[ind[var]] = str(var) + '_' + merged[tract & tp].Characteristic[ind[var]]

    # split data frame by topics
    sub_dataframes = dict()
    sub_group = dict()
    for topic in topics:
        sub_dataframes[topic] = merged[merged['Topic'] == topic]

    # Create the nhs directory if it doesn't exist
    os.makedirs(file_path, exist_ok=True)

    for topic in topics:
        tp_df = sub_dataframes[topic].copy()
        tp_df.drop(columns=['Topic', 'CT_Name'], inplace=True)
        tp_grp = tp_df.groupby(by=['LocalArea', 'Characteristic']).mean()
        tp_grp.reset_index(inplace=True)
        sub_group[str(topic)] = pd.DataFrame()

        for area in local_areas:
            df = tp_grp[tp_grp['LocalArea'] == area].copy()
            df.drop(columns=['LocalArea'], inplace=True)
            df = df.set_index('Characteristic').T.reset_index()
            df = df.rename(columns={'index': 'Type'})
            df['LocalArea'] = str(area)
            sub_group[str(topic)] = pd.concat([sub_group[str(topic)], df])
        sub_group[str(topic)].to_csv(file_path + str(topic) + '.csv')


if __name__ == "__main__":
    main(opt["--nhs_zip"], opt["--ct_bound_zip"], opt["--nhs_file"],
         opt["--ct_file"], opt["--area_file"], opt["--file_path"])
