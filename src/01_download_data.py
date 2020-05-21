# author: Keanna Knebel
# date: 2020-05-04

"""
This script downloads files and saves them to the file_path provided. This
script takes an array of urls specifying the files to download, and a local
file path as arguments.

Usage: src/01_download_data.py --file_path=<file_path> --urls=<urls>

Options:
--file_path=<file_path>      Path to the exported files.
--urls=<urls>                Two-dimensional array, specifing the file name(s)
                             and the URL(s) of file(s) to download.
"""

# URLs to pass in for Deetken evan
# [(licence_1997_2012.csv, \
# https://opendata.vancouver.ca/explore/dataset/business-licences-1997-to-2012/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B), \
# (licence_2013_current.csv, \
# https://opendata.vancouver.ca/explore/dataset/business-licences/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B), \
# (census_2016.csv, \
# https://webtransfer.vancouver.ca/opendata/csv/CensusLocalAreaProfiles2016.csv), \
# (census_2011.csv, \
# https://webtransfer.vancouver.ca/opendata/csv/CensusLocalAreaProfiles2011.csv), \
# (census_2006.csv, \
# https://webtransfer.vancouver.ca/opendata/csv/CensusLocalAreaProfiles2006.csv), \
# (census_2001.csv, \
# https://webtransfer.vancouver.ca/opendata/csv/CensusLocalAreaProfiles2001.csv), \
# (local_area_boundary.geojson, \
# https://opendata.vancouver.ca/explore/dataset/local-area-boundary/download/?format=geojson&timezone=America/Los_Angeles&lang=en),\
# (parking-meters.csv, \
# https://opendata.vancouver.ca/explore/dataset/parking-meters/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B),\
# (disability-parking.csv, \
# https://opendata.vancouver.ca/explore/dataset/disability-parking/download/?format=csv&timezone=America/Los_Angeles&lang=en&use_labels_for_header=true&csv_separator=%3B)]

from docopt import docopt
import os
import requests
import re

opt = docopt(__doc__)


def main(file_path, urls):
    """
    Loads files from the array of urls and saves the
    downloaded files to the provided file path.
    """
    # format urls input
    urls = urls.strip('[]')
    urls = re.findall(r'\([^\)\(]*\)', urls)

    for file in urls:

        file_name, url = tuple(file.strip('()').split(', '))

        # check if file is already downloaded
        if os.path.exists(os.path.join(file_path, file_name)):
            print("%s already exists.\n"%file_name)
            continue
        else:
            print("Starting download for %s...\n"%file_name)
            # create response object
            r = requests.get(url, stream=True)

            # download started
            with open(os.path.join(file_path, file_name), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

            print("%s downloaded!\n"%file_name)

    print("All files downloaded!")


if __name__ == "__main__":
    main(opt["--file_path"], opt["--urls"])
