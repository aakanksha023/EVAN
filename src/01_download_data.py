# author: Keanna Knebel
# date: 2020-05-04

"""
This script downloads 2 .csv files and saves them to the
file_path provided. This script takes the filename and
url for two csv files, and a local file path as arguments.

Usage: src/01_download_data.py --file_path=<file_path> |
    --filename_1=<filename_1> |
    --url1=<url1> |
    --filename_2=<filename_2> |
    --url2=<url2>

Options:
--file_path=<file_path>      Path to the exported csv files.
--filename_1=<filename_1>    Filename for the first csv
--url1=<url1>                URL of first csv
--filename_2=<filename_2>    Filename for the second csv
--url2=<url2>                URL of second csv
"""

# URLS to pass in for Deetken evan
# https://opendata.vancouver.ca/explore/dataset/business-licences-1997-to-2012/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B
# https://opendata.vancouver.ca/explore/dataset/business-licences/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B

import pandas as pd
from docopt import docopt

opt = docopt(__doc__)


def main(file_path, filename_1, url1, filename_2, url2):
    """
    Loads two .csv files from url1 and url2
    and saves the .csv to the provided file path.
    """

    df_1 = pd.read_csv(url1)
    df_2 = pd.read_csv(url2)
    
    # export loaded data frames to CSVs
    df_1.to_csv(file_path + filename_1)
    df_2.to_csv(file_path + filename_2)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--filename_1"], opt["--url1"], opt["--filename_2"], opt["--url2"])

