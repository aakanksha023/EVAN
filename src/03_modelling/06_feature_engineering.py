# author: Jasmine Qin
# date: 2020-05-27

"""
This script performs feature engineering for a specified csv
and saves it to a specified file path.

Usage: src/03_modelling/06_feature_engineering.py --file_path=<file_path> --mapping_csv=<mapping_csv> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path of the csv
                               to be performed feature engineering
--mapping_csv=<mapping_csv>    A csv file mapping the BusinessType to
                               NAICS Canada 2017 Industry classification
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import csv
from collections import defaultdict, Counter

opt = docopt(__doc__)


def historic_mapping(df, col='BusinessType'):
    """
    This function creates mapping rules for historic
    BusinessType and BusinessSubType.

    Parameters:
    -----------
    df: pandas.core.frame.DataFrame
        The dataframe used to set-up mapping rules

    col: str
        The column where historic types need to be cleaned

    Returns:
    -----------
    dict: A look-up dictionary
    """
    df = df.copy(deep=True).dropna(subset=[col])

    contain_historic = df.groupby('BusinessName')[col].apply(
        lambda x: list(x) if x.str.contains(r'\*').any() else False)

    contain_historic_list = [
        list(set(i)) for i in contain_historic[~(
            contain_historic == False)].tolist()]

    historic_lookup_all = defaultdict(Counter)

    for items in contain_historic_list:
        new_types, historic_types = [], []
        for bt in items:
            if 'Historic' not in bt:
                new_types.append(bt)
            else:
                historic_types.append(bt)
        for h in historic_types:
            for n in new_types:
                historic_lookup_all[h][n] += 1

    # create dictionary for mapping
    historic_lookup = {}
    for key, value in historic_lookup_all.items():
        historic_lookup[key] = value.most_common()[0][0]

    return historic_lookup


def main(file_path, new_csv, save_to):
    """
    Feature engineering main function.
    """  
    # create empty dictionary
    my_dict = {' ': ' '}

    # Read csv and write to dictionary
    with open(new_csv, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            my_dict[row[0]] = row[1]

    # Remove additional key value pair
    my_dict.pop(' ')
    my_dict.pop('BusinessType')

    # Read data frame
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns={'Geo Local Area': 'LocalArea'})

    # Add BusinessIndustry column
    df['BusinessIndustry'] = df['BusinessType'].map(my_dict)

    # Remove 2010 Winter games : Outlier
    df = df[df.BusinessIndustry != 'Historic']

    
    # feautures
    num_vars = ['NumberofEmployees', 'FeePaid', 'Parking meters',
                'Disability parking', 'Unemployment_rate']
    cat_vars = ['FOLDERYEAR', 'BusinessType', 'BusinessSubType', 'LocalArea']
    label = ['label']

    # 1. Remove missing LocalArea
    df = df[df.LocalArea.notnull()]

    # 2. Remove previous status != Issued
    df = df[df.Status == 'Issued']

    # 3. Map historic types to current ones
    # df = df.replace({'BusinessType': historic_mapping(
    #     df), 'BusinessSubType': historic_mapping(df, col='BusinessSubType')})

    # 4. Group business types
    # INSERT CODE HERE

    df = df[num_vars+cat_vars+label]

    df.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--mapping_csv"] , opt["--save_to"])
