# author: Jasmine Qin
# date: 2020-05-19

"""
This script performs data cleaning and wrangling for a specified csv
and saves it to a specified file path

Usage: src/02_clean_wrangle/03_clean_licence.py --file_path=<file_path> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path of the csv
                               to be cleaned and wrangled
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import numpy as np
import warnings

opt = docopt(__doc__)


def main(file_path, save_to):

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
    df['status_lag1'] = df_shifted.Status
    df['folderyear_lag1'] = df_shifted.FOLDERYEAR

    # 2. remove different id caused by shifting
    df = df[df.business_id_lag1 == df.business_id]
    df = df[df.FOLDERYEAR + 1 == df.folderyear_lag1]

    # 3. define conditions to label 1 (sucesss)
    #       current year = Issued, no matter what status in last year
    df['label'] = np.where(df.status_lag1 == 'Issued', 1, 0)

    # drop columns
    df = df.drop(columns=['business_id_lag1',
                          'status_lag1', 'folderyear_lag1'])

    # save to a new csv
    df.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to"])
