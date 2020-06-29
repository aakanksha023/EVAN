# author: Jasmine Qin and Xinwen Wang
# date: 2020-06-13

"""
This script performs feature engineering for a specified csv
and saves it to a specified file path.

Usage: src/03_modelling/07_feature_engineering.py \
--file_path=<file_path> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path for licence
--save_to=<save_to>            This is the file path the processed
                                 csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import numpy as np
import math
import json
from collections import Counter
import warnings

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

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

    ###################
    # Nearby Parkings #
    ###################

    # Get coordinates
    parking_meters_df["lat"] = parking_meters_df[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    parking_meters_df["lon"] = parking_meters_df[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][1])
    dis_park["lat"] = dis_park[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    dis_park["lon"] = dis_park[
        'Geom'].apply(lambda p: json.loads(p)['coordinates'][1])

    # To keep null Geom records - JQ
    def get_coords(p, axis='lat'):
        """Get a coordinate or return null"""
        ind = 0 if axis == 'lat' else 1

        coord = json.loads(p)['coordinates'][ind]

#         try:
#             coord = json.loads(p)['coordinates'][ind]
#         except:
#             coord = np.nan

        return coord

    # Filter out points without geom location
    licence_geom = licence[pd.notnull(licence['Geom'])]
    licence_geom["lat"] = licence_geom['Geom'].apply(
        lambda p: get_coords(p))
    licence_geom["lon"] = licence_geom['Geom'].apply(
        lambda p: get_coords(p, 'lon'))

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
    new_licence = get_nearby_facility(area_lis[0], licence_geom,
                                      dis_park, 150, 'nearby_dis_park')

    for area in area_lis[1:]:
        new_licence = pd.concat([
            new_licence, get_nearby_facility(
                area, licence_geom, dis_park, 150, 'nearby_dis_park')])

    parking_area_lis = list(parking_meters_df[
        'Geo Local Area'].unique())
    new_licence_with_parking = get_nearby_facility(
        parking_area_lis[0], new_licence,
        parking_meters_df, 300, 'nearby_parking_meters')

    for area in parking_area_lis[1:]:
        new_licence_with_parking = pd.concat([
            new_licence_with_parking, get_nearby_facility(
                area, licence_geom,
                parking_meters_df, 300,
                'nearby_parking_meters')])

    licence_geom = new_licence_with_parking

    ###########
    # History # - JQ
    ###########
    def fill_geom(df):
        """This function fills Geom for some business_id
            and recovers around 1000 geoms in train set.
        """

        # list of business_id that has null geom
        list_of_id = df[df.Geom.isnull()].business_id.unique()

        # get all rows for these ids from original df
        could_fill = df[df.business_id.isin(list_of_id)]

        # able to find geom for these ids
        list_of_id = could_fill[could_fill.Geom.notnull()].business_id.unique()

        # fill geoms
        for i in list_of_id:
            df_i = df[df.business_id == i]
            geom = df_i[df_i.Geom.notnull()].Geom.values[0]
            df.loc[df.business_id == i, 'Geom'] = geom

        return df

    def history(df):
        """This function assigns a binary variable
            to each business id:
            if the business has been operating for
            more than 5 years, it will be assigned
            an 1, otherwise 0.
        """

        df['history'] = np.zeros(len(df))

        for i in df.business_id.unique():
            id_hist = len(df[df.business_id == i])

            if id_hist >= 5:
                history = [0]*5+[1]*(id_hist-5)
                df.loc[df.business_id == i,
                       'history'] = history

        return df

    ##################
    # Chain business # - JQ
    ##################

    def chain(df):
        """This function counts how many times a business name
            occurs in the entire dataframe.

           It is not aggregated to years in order to capture
            the scenario of a business gone out of business
            for a couple of years but came back at a different
            location later on.

           When counting chain businesses, both business name
            and business industry are used. This is because
            some business names are owner's names so there are
            duplicated names for completely different businesses.
        """

        # count business by name so filter out the ones
        #   without a name first
        df_copy = df[df.BusinessName.notnull()]

        names = []

        # use business_id because ids are aggregated
        #  using location. e.g., Starbucks at different locations
        #  will have the same name but different ids
        for i in df_copy.business_id.unique():
            names.append(
                (df_copy.loc[df_copy.business_id == i,
                             'BusinessName'].values[0],
                 df_copy.loc[df_copy.business_id == i,
                             'BusinessIndustry'].values[0]))

        # count names
        name_dict = Counter(names)

        # add chain column
        chain = []
        for i in range(len(df)):
            name = df.iloc[i, df.columns.get_loc(
                'BusinessName')]
            industry = df.iloc[i, df.columns.get_loc(
                'BusinessIndustry')]

            if pd.isnull(name):
                chain.append(name)
            else:
                try:
                    chain.append(name_dict[
                        (name, industry)])
                except:
                    chain.append(0)

        df['chain'] = chain

        return df

    licence_feat_eng = chain(history(fill_geom(licence)))

    ##############################
    # Count of Nearby Businesses # - JQ
    ##############################

    # The lookup information is saved to csv's
    #   because it's time consuming to run

    if 'train' in file_path:
        nearby_business_lookup = pd.read_csv(
            'src/03_modelling/nearby_business_train.csv')
    elif 'valid' in file_path:
        nearby_business_lookup = pd.read_csv(
            'src/03_modelling/nearby_business_valid.csv')
    else:
        nearby_business_lookup = pd.read_csv(
            'src/03_modelling/nearby_business_test.csv')

    licence_feat_eng = licence_feat_eng.merge(
        nearby_business_lookup,
        how='left',
        left_on=['FOLDERYEAR', 'business_id'],
        right_on=['FOLDERYEAR', 'business_id'])

    # Output
    licence_feat_eng.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to"])
