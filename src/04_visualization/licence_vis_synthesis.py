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


if __name__ == "__main__":
    main()
