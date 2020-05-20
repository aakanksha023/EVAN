# author: Jasmine Qin
# date: 2020-05-19

"""
This script performs data cleaning and wrangling for a specified csv
and saves it to a specified file path

Usage: src/03_data_cleaning.py --file_path=<file_path> --save_to=<save_to>

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
from datetime import datetime


def main():
    opt = docopt(__doc__)
    df = pd.read_csv(opt["--file_path"], low_memory=False)

    #############
    # Cleaning  #
    #############

    # 1. correct spelling
    city_list = ['vancouver', 'vacouver', 'vacouver', 'van', 'v',
                 'vanc', 'vancouver (ubc)', 'bc vancouver',
                 'v5x 3g9vancouver', 'vancovuer', 'vancouver(ubc)',
                 '`vancouver', '0vancouver', 'qbcvancouver']

    df['City'] = ['vancouver' if str(
        c).lower() in city_list else c for c in df.City]

    # 2. remove null FOLDERYEAR with warning
    if len(df[df.FOLDERYEAR.isnull()]) != 0:
        warnings.warn("Removing more than one nan FOLDERYEAR")

    df = df.loc[df.FOLDERYEAR.notnull()]

    # 3. organize years
    df['FOLDERYEAR'] = [y + 2000 if y >= 0 and y <
                        90 else y + 1900 for y in df.FOLDERYEAR]

    # 4. convert dates to datetime objects
    df['ExtractDate'] = [datetime.strptime(
        d, "%Y-%m-%dT%H:%M:%SZ") for d in df.ExtractDate]

    # 5. sort by ExtractDate the keep the latest entry
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
    #       current year = Pending, no matter what status in last year
    df['cond_1'] = np.where(df.status_lag1 == 'Issued', True, False)
    df['cond_2'] = np.where((df.Status == 'Issued') & (
        df.status_lag1 == 'Pending'), True, False)
    df['label'] = np.where((df['cond_1']) | (df['cond_2']), 1, 0)

    # drop columns
    df = df.drop(columns=['business_id_lag1', 'status_lag1',
                          'folderyear_lag1', 'cond_1', 'cond_2'])

    # save to a new csv
    df.to_csv(opt["--save_to"], index=False)


if __name__ == "__main__":
    main()
