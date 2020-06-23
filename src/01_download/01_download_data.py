# author: Keanna Knebel
# date: 2020-05-04

"""
This script downloads files and saves them to the file_path provided. This
script takes an array of urls specifying the files to download, and a local
file path as arguments.

Usage: src/01_download/01_download_data.py --file_path=<file_path> \
    --urls=<urls>

Options:
--file_path=<file_path>      Path to the exported files.
--urls=<urls>                A txt file storing two-dimensional array,
                             specifing the file name(s)
                             and the URL(s) of file(s) to download.
"""

from docopt import docopt
import os
import requests
import re
import progressbar


opt = docopt(__doc__)


def main(file_path, urls):
    """
    Loads files from the array of urls and saves the
    downloaded files to the provided file path.
    """
    # format urls input
    with open(urls, 'r') as file:
        urls = file.read().replace('\n', '')

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

            # Create the data subdirectory if it doesn't exist
            os.makedirs(file_path, exist_ok=True)

            # create response object
            r = requests.get(url, stream=True)
            widgets = ["Progress: ",
                       progressbar.DataSize(), "| ",
                       progressbar.Timer()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=progressbar.UnknownLength)
            value = 0
            # download started
            with open(os.path.join(file_path, file_name), 'wb') as f:
                for chunk in r.iter_content(chunk_size=64*1024):
                    if chunk:
                        f.write(chunk)
                        value += len(chunk)
                        bar.update(value)

            print("\n%s downloaded!\n"%file_name)

    print("All files downloaded!")


if __name__ == "__main__":
    main(opt["--file_path"], opt["--urls"])
