# author: Keanna Knebel
# date: 2020-05-04

"""
This script downloads 2 .csv files with the same columns and,
combines them into a single data frame, and exports this data frame
as a .csv into the /data folder. This script takes the filename,
2 urls, and a local file path as arguments.

Usage: src/01_download_data.py --file_path=<file_path> --url1=<url1> --url2=<url2>

Options:
--file_path=<file_path>  Path (including filename) to the csv file.
--url1=<url1>            URL of first csv
--url2=<url2>            URL of second csv
"""

# URLS to pass in for Deetken evan
# https://opendata.vancouver.ca/explore/dataset/business-licences-1997-to-2012/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B
# https://opendata.vancouver.ca/explore/dataset/business-licences/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B

import pandas as pd
from docopt import docopt

opt = docopt(__doc__)


def main(file_path, url1, url2):
    """
    Combines two .csv files from url1 and url2
    into a single data-frame and writes a .csv
    to the provided file path. The csv's to be
    combined need to have the same columns.

    Parameters
    ----------
    file_path : str
        The local file-path (including file name)

    url1 : str
        URL to a .csv file

    url2 : str
        URL to a .csv file

    Returns
    -------
        csv file written in the provided file path

    Examples
    --------
    main('data/alphabet_data.csv',
        'https://public-data.com/url_abc.csv',
        'https://public-data.com/url_def.csv')
    """
    df_1 = pd.read_csv(url1)
    df_2 = pd.read_csv(url2)

    df_combo = df_1.append(df_2)
    df_combo.to_csv(file_path)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--url1"], opt["--url2"])
