# author: Jasmine Qin
# date: 2020-06-01

"""
This script performs feature engineering for a specified csv
and saves it to a specified file path.

Usage: src/03_modelling/05_feature_engineering.py \
--file_path=<file_path> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path for licence
--save_to=<save_to>            This is the file path the processed
                                 csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import math
import json

opt = docopt(__doc__)


def main(file_path, save_to):
    """
    Feature engineering main function.
    """

    # Read data frame
    licence = pd.read_csv(
        file_path, low_memory=False)
    dis_park = pd.read_csv(
        "data/raw/disability-parking.csv", sep=';')
    parking_meters_df = pd.read_csv(
        "data/raw/parking-meters.csv", sep=';')

    # Get coordinates
    parking_meters_df["lat"] = parking_meters_df[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    parking_meters_df["lon"] = parking_meters_df[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][1])
    dis_park["lat"] = dis_park[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    dis_park["lon"] = dis_park[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][1])

    # Filter out points without geom location
    licence = licence[pd.notnull(licence['Geom'])]
    licence["lat"] = licence['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][0])
    licence["lon"] = licence['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][1])

    # this function is from
    # https://gis.stackexchange.com/questions/293310/how-to-use-geoseries-distance-to-get-the-right-answer
    def haversine(coord1, coord2):

        # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        R = 6371000  # radius of Earth in meters
        phi_1 = math.radians(lat1)
        phi_2 = math.radians(lat2)

        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(
            phi_1) * math.cos(phi_2) * math.sin(
            delta_lambda / 2.0) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        meters = R * c

        return round(meters)

    def get_nearby_facility(area, licence, facility_df,
                            distance, name_for_new_column):

        licence_partial = licence[licence['LocalArea'] == area]
        licence_partial[name_for_new_column] = 0
        facility_partial = facility_df[
            facility_df['Geo Local Area'] == area]

        for index, row in licence_partial.iterrows():
            for index_i, row_i in facility_partial.iterrows():
                count = 0
                dis = haversine(coord1=(
                    row['lat'], row['lon']), coord2=(
                    row_i['lat'], row_i['lon']))
                if dis < distance:
                    count += 1
            licence_partial.at[index, name_for_new_column] = count
            return licence_partial

    area_lis = list(dis_park['Geo Local Area'].unique())
    new_licence = get_nearby_facility(area_lis[0], licence,
                                      dis_park, 150, 'nearby_dis_park')

    for area in area_lis[1:]:
        new_licence = pd.concat([
            new_licence, get_nearby_facility(
                area, licence, dis_park, 150, 'nearby_dis_park')])

    parking_area_lis = list(parking_meters_df[
        'Geo Local Area'].unique())
    new_licence_with_parking = get_nearby_facility(
        parking_area_lis[0], new_licence,
        parking_meters_df, 300, 'nearby_parking_meters')

    for area in parking_area_lis[1:]:
        new_licence_with_parking = pd.concat([
            new_licence_with_parking, get_nearby_facility(
                area, licence,
                parking_meters_df, 300,
                'nearby_parking_meters')])

    licence = new_licence_with_parking

    licence.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to"])
