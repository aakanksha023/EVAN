# author: Aakanksha Dimri, Keanna Knebel, Jasmine Qin, Xinwen Wang
# date: 2020-06-01

"""
This script performs data cleaning and wrangling for a specified csv
and saves it to a specified file path

Usage: src/02_clean_wrangle/03_clean_licence.py --file_path=<file_path> \
--mapping_csv=<mapping_csv> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path of the csv
                               to be cleaned and wrangled
--mapping_csv=<mapping_csv>    A csv file mapping the BusinessType to
                               NAICS Canada 2017 Industry classification
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages
from docopt import docopt
import os
import pandas as pd
import numpy as np
import warnings
import csv

opt = docopt(__doc__)


def main(file_path, mapping_csv, save_to):

    df = pd.read_csv(file_path, low_memory=False, dtype={
                     'NumberofEmployees': 'object'})

    #############
    # Cleaning  #
    #############

    # 1. location data cleaning
    city_list = ['vancouver', 'vacouver', 'vacouver', 'van', 'v',
                 'vanc', 'vancouver (ubc)', 'bc vancouver',
                 'v5x 3g9vancouver', 'vancovuer', 'vancouver(ubc)',
                 '`vancouver', '0vancouver', 'qbcvancouver']

    df['City'] = ['vancouver' if str(
        c).lower() in city_list else c for c in df.City]

    df = df[~((df.PostalCode.isnull()) & (df.LocalArea.isnull()))]

    # 2. replace '000' values in NumberofEmployees to NA
    df = df.replace({'NumberofEmployees': {"000": None}})
    df["NumberofEmployees"] = df.NumberofEmployees.astype(float)

    # 3. remove null FOLDERYEAR with warning
    if len(df[df.FOLDERYEAR.isnull()]) != 0:
        warnings.warn(
            "Removing " +
            str(len(df[df.FOLDERYEAR.isnull()])) + " nan FOLDERYEAR",
            stacklevel=2)

    df = df.loc[df.FOLDERYEAR.notnull()]

    # 4. organize years
    df['FOLDERYEAR'] = [y + 2000 if y >= 0 and y <
                        90 else y + 1900 for y in df.FOLDERYEAR]

    # 5. convert dates to datetime objects and adjust 1996 or before data
    df['ExtractDate'] = pd.to_datetime(df['ExtractDate'], errors='ignore')
    df['IssuedDate'] = pd.to_datetime(df['IssuedDate'], errors='ignore')
    df['ExpiredDate'] = pd.to_datetime(df['ExpiredDate'], errors='ignore')

    df.loc[(df['FOLDERYEAR']
            < 1997.0) & (df['IssuedDate'].dt.year == 1996.0)
           & (df['ExpiredDate'].dt.year == 1997.0), 'FOLDERYEAR'] = 1997.0

    df = df[~(df.FOLDERYEAR < 1997.0)]

    # 6. sort by ExtractDate the keep the latest entry
    df = df.sort_values(by=['business_id', 'FOLDERYEAR', 'ExtractDate'])
    df = df[df.groupby(['business_id'])['FOLDERYEAR'].apply(
        lambda x: ~(x.duplicated(keep='last')))]

    #############
    # Wrangling #
    #############

    # 1. shift to find next year's status
    df_shifted = df.sort_values(
        ['business_id', 'FOLDERYEAR']).shift(periods=-1)
    df['business_id_lag1'] = df_shifted.business_id
    df['NextYearStatus'] = df_shifted.Status
    df['folderyear_lag1'] = df_shifted.FOLDERYEAR

    # 2. remove different id caused by shifting
    df = df[df.business_id_lag1 == df.business_id]
    df = df[df.FOLDERYEAR + 1 == df.folderyear_lag1]

    # 3. define conditions to label 1 (success)
    #       current year = Issued, no matter what status in last year
    df['label'] = np.where(df.NextYearStatus == 'Issued', 1, 0)
    # drop columns
    df = df.drop(columns=['business_id_lag1', 'folderyear_lag1'])

    ####################
    # Industry Mapping #
    ####################

    mapping_dict = {' ': ' '}

    # Read csv and write to dictionary
    with open(mapping_csv, mode='r') as csv_file:
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

    #######################
    # Reduce Dataset Size #
    #######################

    # 1. Drop null LocalArea
    df = df[df.LocalArea.notnull()]

    # 2. Remove BusinessIndustry = 'Real estate and rental and leasing'
    df = df[~(df.BusinessIndustry == 'Real estate and rental and leasing')]

    # save to a new csv
    df.to_csv(save_to, index=False)

def test_fun():
    """
    Checks if the req. i/p files exist and if the main function is able\
    to store the results at correct location
    """
    # Run main function for validation set
    main(file_path="data/processed/validate.csv", mapping_csv="src/02_clean_wrangle/business_mapping_dictionary.csv", save_to="data/processed/03_cleaned_validate.csv")
    # Confirm input and output CSV files exist or not
    assert os.path.exists("src/02_clean_wrangle/business_mapping_dictionary.csv"), "Business mapping Dictionary csv not found in location" 
    assert os.path.exists("data/processed/train.csv"), "Input training csv file not found in location"
    assert os.path.exists("data/processed/validate.csv"), "Input validation csv file not found in location"
    assert os.path.exists("data/processed/test.csv"), "Input test csv file not found in location"
    assert os.path.exists("data/processed/03_cleaned_validate.csv"), "Validation Result csv file not found in location" 
    print("Tests cleared successfully")

if __name__ == "__main__":
    test_fun()
    main(opt["--file_path"], opt["--mapping_csv"], opt["--save_to"])
