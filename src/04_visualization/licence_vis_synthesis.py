# author: Jasmine Qin
# date: 2020-06-09

"""
This script performs data wrangling and sythesizing needed for
visualization of the business licence file.

Usage: src/04_visualization/licence_vis_synthesis.py
"""

# load packages
import pandas as pd
import json
import csv
import re


def main():

    # read data
    licence_df = pd.read_csv(
        "data/processed/03_combined_licences_cleaned.csv",
        low_memory=False)
    parking = pd.read_csv(
        "data/raw/parking-meters.csv", sep=';')
    disability_parking = pd.read_csv(
        "data/raw/disability-parking.csv", sep=';')

    # parking cleaning
    parking = parking[['Geom', 'Geo Local Area']].rename(
        columns={'Geo Local Area': 'LocalArea'})

    disability_parking = disability_parking[[
        'Geom', 'Geo Local Area']].rename(
        columns={'Geo Local Area': 'LocalArea'})

    # licence cleaning
    # 1. remove null geom
    licence_df = licence_df[licence_df['Geom'].notnull()]

    # 2. remove unused columns
    cols_not_used = ['business_id',
                     'LicenceRSN',
                     'LicenceNumber',
                     'LicenceRevisionNumber',
                     'Unit',
                     'UnitType',
                     'House',
                     'Street',
                     'Country',
                     'label']

    licence_df = licence_df.drop(columns=cols_not_used)

    # 3. remove null BusinessIndustry
    licence_df = licence_df[licence_df.BusinessIndustry.notnull()]

    # 4. FOLDERYEAR to int
    licence_df['FOLDERYEAR'] = [int(i) for i in licence_df['FOLDERYEAR']]
    licence_df = licence_df.sort_values('FOLDERYEAR')

    # get coordinates
    for df in [parking, disability_parking, licence_df]:
        df["coord-x"] = df['Geom'].apply(
            lambda p: json.loads(p)['coordinates'][0])
        df["coord-y"] = df['Geom'].apply(
            lambda p: json.loads(p)['coordinates'][1])

    # save to files
    licence_df.to_csv("data/processed/vis_licence.csv", index=False)
    parking.to_csv("data/processed/vis_parking.csv", index=False)
    disability_parking.to_csv(
        "data/processed/vis_disability_parking.csv", index=False)

    #################
    # Aggregated df #
    #################

    df = pd.read_csv(
        "data/processed/combined_licences.csv",
        low_memory=False)

    # organize FOLDERYEAR
    df = df.loc[df.FOLDERYEAR.notnull()]
    df['FOLDERYEAR'] = [y + 2000 if y >= 0 and y <
                        90 else y + 1900 for y in df.FOLDERYEAR]
    df['ExtractDate'] = pd.to_datetime(df['ExtractDate'], errors='ignore')
    df['IssuedDate'] = pd.to_datetime(df['IssuedDate'], errors='ignore')
    df['ExpiredDate'] = pd.to_datetime(df['ExpiredDate'], errors='ignore')

    df.loc[(df['FOLDERYEAR']
            < 1997.0) & (df['IssuedDate'].dt.year == 1996.0)
           & (df['ExpiredDate'].dt.year == 1997.0), 'FOLDERYEAR'] = 1997.0

    df = df[~(df.FOLDERYEAR < 1997.0)]
    df['FOLDERYEAR'] = [int(i) for i in df['FOLDERYEAR']]
    
    df = df.sort_values(by=['business_id', 'FOLDERYEAR', 'ExtractDate'])
    df = df[df.groupby(['business_id'])['FOLDERYEAR'].apply(
        lambda x: ~(x.duplicated(keep='last')))]
    
    # only Issued licences
    df = df.query('Status == "Issued"')

    # Industry mapping
    mapping_dict = {' ': ' '}

    # Read csv and write to dictionary
    with open("src/02_clean_wrangle/business_mapping_dictionary.csv",
              mode='r') as csv_file:

        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            mapping_dict[row[0]] = row[1]

    # Remove additional key value pair
    mapping_dict.pop(' ')
    mapping_dict.pop('BusinessType')

    # Add BusinessIndustry column
    df['BusinessIndustry'] = df['BusinessType'].map(mapping_dict)

    # Remove 2010 Winter games : Outlier
    df = df[df.BusinessIndustry != 'Historic']
    df = df[df.BusinessIndustry != 'Real estate and rental and leasing']
    df = df[df.LocalArea.notnull()]

    agg_viz = pd.DataFrame(df.groupby([
        'FOLDERYEAR', 'LocalArea',
        'BusinessIndustry', 'BusinessType'])[
        'business_id'].count()).reset_index()

    agg_viz = agg_viz[~(agg_viz.BusinessType.str.contains(
        r'\*Historic\*'))]

    # save to files
    licence_df.to_csv("data/processed/vis_licence.csv", index=False)
    agg_viz.to_csv("data/processed/vis_agg_licence.csv", index=False)
    parking.to_csv("data/processed/vis_parking.csv", index=False)
    disability_parking.to_csv(
        "data/processed/vis_disability_parking.csv", index=False)


if __name__ == "__main__":
    main()
