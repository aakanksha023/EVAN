# author: Xinwen Wang
# date: 2020-05-25

"""
This script performs will create a visualization using Kepler and save
the visualization into a html file. 

Usage: src/04_kepler_vis.py --file_path1=<file_path1> --file_path2=<file_path2> --file_path3=<file_path3> 

Options:
--file_path1=<file_path1>        This is the file path for the licence_vis.csv
--file_path2=<file_path2>        This is the file path of the disability_vis.csv
--file_path3=<file_path3>        This is the file path for the parking_meter_vis.csv

"""

from docopt import docopt
import pandas as pd
import geopandas as gpd
import keplergl

opt = docopt(__doc__)


def main(file_path1, file_path2, file_path3):

    licence_df = pd.read_csv(file_path1)
    dis_parking_df = pd.read_csv(file_path2)
    parking_meter_df = pd.read_csv(file_path3)

    w1 = keplergl.KeplerGl(height=1000,width=100)
    w1.add_data(licence_df, name = "Census")
    w1.add_data(parking_meter_df, name = "Parking")
    w1.add_data(dis_parking_df, name = "Disability Parking")
    w1.save_to_html()


if __name__ == "__main__":
    main(opt["--file_path1"], opt["--file_path2"], opt["--file_path3"])
