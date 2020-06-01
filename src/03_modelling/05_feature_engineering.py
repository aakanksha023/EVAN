# author: Jasmine Qin
# date: 2020-06-01

"""
This script performs feature engineering for a specified csv
and saves it to a specified file path.

Usage: src/03_modelling/05_feature_engineering.py --file_path=<file_path> \
--save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path of the csv
                               to be performed feature engineering
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd

opt = docopt(__doc__)


def main(file_path, save_to):
    """
    Feature engineering main function.
    """

    # Read data frame
    df = pd.read_csv(file_path, low_memory=False).rename(
        columns={'Geo Local Area': 'LocalArea'})

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

    df = df[num_vars+cat_vars+label]

    df.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to"])
