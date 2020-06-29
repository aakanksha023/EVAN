# author: Aakanksha Dimri, Keanna Knebel, Jasmine Qin, Xinwen Wang
# date: 2020-06-24

"""
This script performs data wrangling and synthesis to licence, census,
and parking datasets and saves the combined dataset
to a specified file path. The input licence data needs to
be the output of 03_clean_wrangle.py script. The output will be feeding into
feature engineering script.

Usage: src/02_clean_wrangle/06_synthesis.py --path_in=<path_in>  \
--save_to=<save_to>

Options:
--path_in=<path_in>             This is the file path of the csv
                                  to be synthesized.
--save_to=<save_to>             The file path where the processed training
                                  csv will be saved.
"""

# load packages
from docopt import docopt
import pandas as pd
import re
import os
import warnings

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

opt = docopt(__doc__)


def main(path_in, save_to):

    ####################
    # Licence Cleaning # - for modelling
    ####################

    licence_df = pd.read_csv(path_in)
    licence_df = licence_df.astype({'FOLDERYEAR': 'int'})

    # 1. Remove status != Issued
    licence_df = licence_df[licence_df.Status == 'Issued']

    # 2. Filter out unused columns
    cols_not_used = ['LicenceRSN',
                     'LicenceNumber',
                     'LicenceRevisionNumber',
                     'IssuedDate',
                     'ExpiredDate',
                     'Unit',
                     'UnitType',
                     'House',
                     'Street',
                     'City',
                     'Province',
                     'Country',
                     'PostalCode',
                     'ExtractDate']

    licence_df = licence_df.drop(columns=cols_not_used)

    # 3. Remove null BusinessIndustry
    licence_df = licence_df[licence_df.BusinessIndustry.notnull()]

    ####################
    # Census Functions #
    ####################

    def merge_data(df_list, licence_df):

        whole = pd.concat([i for i in df_list])
        whole = whole.rename(columns={"Year": "FOLDERYEAR"})
        licence_df = licence_df.merge(
            whole,
            on=["LocalArea", "FOLDERYEAR"],
            how='left')

        return licence_df

    def fill_missing_year(df, start_year, end_year):
        """
        This function will repeat the dataframe and fill the year
        from the start to end
        Args:
            df (pandas dataframe): The dataframe
            start_year (int): The four digit start year
            end_year (int): The four digit end year, note end year not included

        Returns:
            df: The expanded dataframe

        """

        df = df[~((
            df.LocalArea == 'Vancouver CMA') | (
            df.LocalArea == 'Vancouver CSD'))]

        year_lis = list(range(start_year, end_year))
        df = pd.concat([df]*len(year_lis))
        df.reset_index(drop=True, inplace=True)
        df['Year'] = 0
        i = 0

        for year in year_lis:
            df.iloc[i:i+22]['Year'] = year
            i += 22

        return df

    def clean_couples_family_structure(family, start_year, end_year):
        """
        This function cleans the family census data
        Args:
            family (pandas dataframe): The dataframe for family data
            start_year (int): The four digit start year
            end_year (int): The four digit end year, note end year not included

        Returns:
            family: A cleaned pandas dataframe

        """
        family = family[family['Type'] == 'total couples']

        family['Without children at home'] = family[
            'Without children at home']/family['Total']

        family['1 child'] = family['1 child'] / family['Total']

        family['2 children'] = family['2 children'] / family['Total']

        family['3 or more children'] = family['3 or more children'] / \
            family['Total']

        family = family[['LocalArea',
                         'Without children at home',
                         '1 child',
                         '2 children',
                         '3 or more children']]

        family = fill_missing_year(family, start_year, end_year)

        return family

    def clean_detailed_language(language, start_year, end_year):
        """
        This function cleans the language census data
        Args:
            language (pandas dataframe): The dataframe for language data
            start_year (int): The four digit start year
            end_year (int): The four digit end year, note end year not included

        Returns:
            language: A cleaned pandas dataframe

        """
        # only keeping their mother tongue
        language = language[language['Type'] == 'mother tongue - total']

        cols = ['English', 'French', 'Chinese, n.o.s.',
                'Mandarin', 'Cantonese', 'Italian',
                'German', 'Spanish']

        sum_language = 0
        for c in cols:
            language[c] = language[c]/language['Single responses']
            sum_language += language[c]

        language['other language'] = 1 - sum_language

        language['Chinese'] = language['Mandarin'] + \
            language['Cantonese'] + \
            language['Chinese, n.o.s.']

        language = language[['LocalArea', 'English',
                             'French', 'Chinese',
                             'Italian', 'German',
                             'Spanish', 'other language']]

        language = fill_missing_year(
            language, start_year, end_year)
        return language

    def clean_marital_status(marital, start_year, end_year):
        """
        This function cleans the marital census data
        Args:
            marital (pandas dataframe): The dataframe for language data
            start_year (int): The four digit start year
            end_year (int): The four digit end year, note end year not included

        Returns:
            marital: A cleaned pandas dataframe

        """

        marital['Married or living with a or common-law partner'] = marital[
            'Married or living with a or common-law partner'] / \
            marital['Total population 15 years and over']
        marital[
            'Not living with a married spouse or common-law partner'] = \
            marital[
                'Not living with a married spouse or common-law partner'] / \
            marital['Total population 15 years and over']

        if start_year == 2007 or start_year == 2012:
            marital = marital.query('Type == "total"')

        marital = marital[['LocalArea',
                           'Married or living with a or common-law partner',
                           'Not living with a married spouse or common-law partner']]

        marital = fill_missing_year(marital, start_year, end_year)
        return marital

    def clean_age(age, start_year, end_year):
        """
        This function cleans the marital census data
        Args:
            age (pandas dataframe): The dataframe for population data
            start_year (int): The four digit start year
            end_year (int): The four digit end year, note end year not included

        Returns:
            age: A cleaned pandas dataframe

        """
        age = age[age['Type'] == 'total']

        age['age below 20'] = (age[
            '0 to 4 years'] + age[
            '5 to 9 years'] + age[
            '10 to 14 years'] + age[
            '15 to 19 years'])/age['Total']

        age['age between 20 and 35'] = (
            age['20 to 24 years'] + age[
                '25 to 29 years'] + age[
                '30 to 34 years'])/age['Total']

        age['age between 35 and 60'] = (
            age['35 to 39 years'] + age[
                '40 to 44 years'] + age[
                '45 to 49 years'] + age[
                '50 to 54 years'] + age[
                '55 to 59 years'])/age['Total']

        age['age above 60'] = 1 - (
            age['age below 20'] + age[
                'age between 20 and 35'] + age[
                'age between 35 and 60'])

        age = age[['LocalArea', 'age below 20',
                   'age between 20 and 35',
                   'age between 35 and 60',
                   'age above 60']]

        age = fill_missing_year(age, start_year, end_year)
        return age

    def clean_gender(gender, start_year, end_year):

        gender = gender.iloc[:, 1:4].pivot(
            index='LocalArea', columns='Type', values='Total'
        ).reset_index()

        gender['female'] = gender['female']/gender['total']
        gender['male'] = gender['male']/gender['total']

        gender = gender[['LocalArea',
                         'female',
                         'male']]

        gender = fill_missing_year(gender, start_year, end_year)
        return gender

    def clean_visible_minority(mino, start_year, end_year):

        if start_year == 2007:
            mino = mino[mino.Type == 'Total']

        mino = mino[['LocalArea', 'Not a visible minority',
                     'Total visible minority population']]

        mino['total_sum'] = mino[
            'Not a visible minority'] + mino[
            'Total visible minority population']

        mino['Not a visible minority'] = mino[
            'Not a visible minority'] / mino['total_sum']
        mino['Total visible minority population'] = mino[
            'Total visible minority population']/mino['total_sum']

        mino.drop(columns=['total_sum'], inplace=True)

        mino = fill_missing_year(mino, start_year, end_year)
        return mino

    def clean_structural_dwelling_type(dwel, start_year, end_year):

        dwel['dwelling_House'] = (dwel['Single-detached house'] +
                                  dwel['Semi-detached house'] +
                                  dwel['Row house'])/dwel['Total']

        if start_year == 1997:
            dwel['dwelling_Apartment'] = (
                dwel['Apartment, detached duplex'] + dwel[
                    'Apartment, building that has five or more storeys'
                ] + dwel[
                    'Apartment, building that has fewer than five storeys'
                ])/dwel['Total']
            dwel['dwelling_Other'] = (
                dwel['Other single-attached house'] + dwel[
                    'Movable dwelling'])/dwel['Total']

        elif start_year == 2002:
            dwel['dwelling_Apartment'] = (
                dwel['Apartment, duplex'] + dwel[
                    'Apartment, building that has five or more storeys'
                ])/dwel['Total']
            dwel['dwelling_Other'] = 1 - dwel[
                'dwelling_Apartment'] - dwel[
                'dwelling_House']

        else:
            dwel['dwelling_Apartment'] = (dwel[
                'Apartment, detached duplex'] + dwel[
                'Apartment, building that has five or more storeys'
            ] + dwel[
                'Apartment, building that has fewer than five storeys'
            ])/dwel['Total']
            dwel['dwelling_Other'] = 1 - dwel[
                'dwelling_Apartment'] - dwel[
                'dwelling_House']

        dwel = dwel[['LocalArea',
                     'dwelling_House',
                     'dwelling_Apartment',
                     'dwelling_Other']]

        dwel = fill_missing_year(dwel, start_year, end_year)
        return dwel

    def clean_shelter_tenure(shel, start_year, end_year):

        if start_year == 2007:
            shel = shel.query('Type == "Total"')

        shel['Owned_Rented'] = shel[
            'Owned'] + shel['Rented']
        shel['Owned shelter'] = shel[
            'Owned']/shel['Owned_Rented']
        shel['Rented shelter'] = shel[
            'Rented']/shel['Owned_Rented']

        shel = shel[['LocalArea',
                     'Owned shelter',
                     'Rented shelter']]

        shel = fill_missing_year(shel, start_year, end_year)
        return shel

    def clean_lone_parent(lone, start_year, end_year):
        lone['Female lone parent'] = lone[
            'Female parent'] / lone['Total lone-parent families']
        lone['Male lone parent'] = lone[
            'Male parent'] / lone['Total lone-parent families']

        lone = lone[['LocalArea',
                     'Female lone parent',
                     'Male lone parent']]

        lone = fill_missing_year(lone, start_year, end_year)
        return lone

    def clean_imgra_period(im_p, start_year, end_year):
        # note that start year should only be 1997 or 2002 or 2007 or 2012
        if start_year == 1997:
            col_names = ['LocalArea',
                         'Total immigrant population',
                         '1996 to 2001']
            im_p = im_p[col_names]
            im_p.rename(columns={'1996 to 2001': 'Immigrates'}, inplace=True)

        elif start_year == 2002:
            col_names = ['LocalArea',
                         'Total immigrant population',
                         '2001 to 2006']
            im_p = im_p[col_names]
            im_p.rename(columns={'2001 to 2006': 'Immigrates'}, inplace=True)

        elif start_year == 2007:
            col_names = ['LocalArea',
                         'Immigrants',
                         '2006 to 2010']
            im_p = im_p[col_names]
            im_p.rename(columns={'Immigrants': 'Total immigrant population',
                                 '2006 to 2010': 'Immigrates'}, inplace=True)

        elif start_year == 2012:
            col_names = ['LocalArea',
                         'Immigrants',
                         '2011 to 2016']
            im_p = im_p[col_names]
            im_p.rename(columns={'Immigrants': 'Total immigrant population',
                                 '2011 to 2016': 'Immigrates'}, inplace=True)

        else:
            print(
                'Invalid start year. Valid years are: 1997, 2002, 2007, 2012')

        im_p['Immigrates'] = im_p[
            'Immigrates'] / im_p['Total immigrant population']

        im_p = im_p[['LocalArea',
                     'Immigrates']]

        im_p = fill_missing_year(im_p, start_year, end_year)
        return im_p

    def clean_citizenship(citizen, start_year, end_year):

        if start_year == 2007:
            citizen = citizen[citizen['Unnamed: 0'] == 0]

        if start_year == 1997:
            citizen = citizen.rename(
                columns={'Canadian Citizenship': 'Canadian citizens',
                         'Citizenship other than Canadian': 'Not Canadian citizens'})

        citizen['total'] = citizen[
            'Canadian citizens'] + citizen[
            'Not Canadian citizens']
        citizen['Canadian citizens'] = citizen[
            'Canadian citizens'] / citizen['total']
        citizen['Not Canadian citizens'] = citizen[
            'Not Canadian citizens'] / citizen['total']

        citizen = citizen[['LocalArea',
                           'Canadian citizens',
                           'Not Canadian citizens']]
        citizen = fill_missing_year(citizen, start_year, end_year)
        return citizen

    def clean_generation_status(gen, start_year, end_year):
        for i in gen.columns[3:]:
            gen[i] = gen[i]/gen[gen.columns[2]]

        gen = gen.iloc[:, [1, 3, 4, 5]]
        gen = fill_missing_year(gen, start_year, end_year)
        return gen

    def clean_household_size(house_size, start_year, end_year):

        col_lis = list(house_size.columns)[3:8]
        for col in col_lis:
            house_size[col] = house_size[
                col]/house_size['Total households']

        house_size.rename(
            columns={'1 person': '1 person household',
                     '2 persons': '2 persons household',
                     '3 persons': '3 persons household',
                     '4 persons': '4 to 5 persons household',
                     '5 or more persons': '6 or more persons household',
                     '4 to 5 persons': '4 to 5 persons household',
                     '6 or more persons': '6 or more persons household'},
            inplace=True)

        house_size = house_size[[
            'LocalArea', '1 person household',
            '2 persons household', '3 persons household',
            '4 to 5 persons household',
            '6 or more persons household']]

        house_size = fill_missing_year(house_size, start_year, end_year)
        return house_size

    def clean_household_type(house_type, start_year, end_year):
        for i in house_type.columns[3:]:
            house_type[i] = house_type[
                i]/house_type[house_type.columns[2]]

        house_type = house_type.iloc[:, [1, 3, 4, 5]]

        house_type.columns = ['LocalArea',
                              'One-family households',
                              'Multiple-family households',
                              'Non-family households']

        house_type = fill_missing_year(house_type, start_year, end_year)
        return house_type

    def clean_imgra_age(img_age, start_year, end_year):

        img_age.rename(
            columns={'Under 5 years': 'Immigrants under 5 years',
                     '5 to 14 years': 'Immigrants 5 to 14 years',
                     '15 to 24 years': 'Immigrants 15 to 24 years',
                     '25 to 44 years': 'Immigrants 25 to 44 years',
                     '45 years and over': 'Immigrants 45 years and over'
                     }, inplace=True)

        img_age.drop(columns=['Unnamed: 0'], inplace=True)

        if start_year == 2007:
            img_age = img_age[img_age['Type'] == 'Total']
            img_age.drop(columns=['Type'], inplace=True)

        col_lis = list(img_age.columns)[2:]
        for col in col_lis:
            img_age[col] = img_age[
                col]/img_age['Total immigrant population']

        img_age = fill_missing_year(img_age, start_year, end_year)
        return img_age

    def clean_industry(ind, start_year, end_year):

        col_lis = list(ind.columns)[5:]
        for col in col_lis:
            ind[col] = ind[col]/ind['total']

        ind['Industry - Not applicable'] = ind[
            'Industry - Not applicable']/ind['total']

        ind.drop(columns=['All industries',
                          'Unnamed: 0', 'total'], inplace=True)

        ind = fill_missing_year(ind, start_year, end_year)
        return ind

    def clean_labour_force_status(labour, start_year, end_year):
        labour = labour[labour['Type'] == 'Total']

        labour = labour[['LocalArea',
                         'Employment rate',
                         'Unemployment rate']]

        labour = fill_missing_year(labour, start_year, end_year)
        return labour

    def clean_mobility(mob, start_year, end_year):

        mob['total'] = mob[
            'Non-movers 1 yr ago'] + mob[
            'Non-migrants 1 yr ago'] + mob[
            'Migrants 1 yr ago']

        mob['Non-movers 1 yr ago'] = mob[
            'Non-movers 1 yr ago']/mob['total']
        mob['Non-migrants 1 yr ago'] = mob[
            'Non-migrants 1 yr ago']/mob['total']
        mob['Migrants 1 yr ago'] = mob[
            'Migrants 1 yr ago']/mob['total']

        mob = mob[['LocalArea',
                   'Non-movers 1 yr ago',
                   'Non-migrants 1 yr ago',
                   'Migrants 1 yr ago']]
        mob = fill_missing_year(mob, start_year, end_year)
        return mob

    def clean_occupation(occ, start_year, end_year):

        occ['total'] = occ[
            list(occ.columns)[3]] + occ[list(occ.columns)[4]]

        col_lis = list(occ.columns)[4:]
        for col in col_lis:
            occ[col] = occ[col]/occ['total']

        occ = occ[occ.Type == "Total"]

        occ.drop(columns=['Type',
                          'All occupations',
                          'Unnamed: 0',
                          'total'], inplace=True)

        occ = fill_missing_year(occ, start_year, end_year)
        return occ

    def clean_time_worked(tw, start_year, end_year):

        tw = tw.query('Type == "Total"')
        col_lis = list(tw.columns)[4:6]

        for col in col_lis:
            tw[col] = tw[col]/tw[
                'Population 15 years and over by work activity']

        tw = tw[['LocalArea',
                 'full time',
                 'part time']]

        tw = fill_missing_year(tw, start_year, end_year)
        return tw

    def clean_transport_mode(trans, start_year, end_year):

        trans = trans.query('Type == "Total"')

        cols = list(trans.columns)[4:]
        for c in cols:
            trans[c] = trans[c]/trans['Total']

        trans.drop(columns=['Unnamed: 0',
                            'Type',
                            'Total'], inplace=True)

        trans = fill_missing_year(trans, start_year, end_year)
        return trans

    def clean_workplace_status(wp, start_year, end_year):

        wp = wp.query('Type == "Total"')

        cols = list(wp.columns)[3:]
        wp['total'] = wp[list(wp.columns)[3]] + wp[
            list(wp.columns)[4]] + wp[
            list(wp.columns)[5]] + wp[
            list(wp.columns)[6]]

        for c in cols:
            wp[c] = wp[c]/wp['total']

        wp.drop(columns=['Unnamed: 0',
                         'Type',
                         'total'], inplace=True)

        wp = fill_missing_year(wp, start_year, end_year)
        return wp

    def clean_education(education, start_year, end_year):

        if start_year == 1997:
            uni = education[
                'Total population with postsecondary qualifications']
            total = education[
                'Total population 20 years and over']
        elif start_year == 2002:
            uni = education[
                'Total population 25 to 64 years with postsecondary qualifications']
            total = education[
                'Total population aged 15 years and over']
        else:
            uni = education[
                'population aged 15 years and over - Postsecondary certificate, diploma or degree']
            total = education[
                'Total population aged 15 years and over']
            if start_year == 2007:
                education = education.query(
                    'Type == "Total"')

        high_school = total - uni
        education['education below postsecondary'] = high_school/total
        education['education above postsecondary'] = uni/total

        education = education[['LocalArea',
                               'education below postsecondary',
                               'education above postsecondary']]

        education = fill_missing_year(education, start_year, end_year)
        return education

    def clean_immigration_birth_place(im_birth, start_year, end_year):

        if start_year == 2007:
            im_birth = im_birth.query('Type == "Total"')

        col_lis = ['Non-immigrants',
                   'Non-permanent residents',
                   'Immigrants']

        for col in col_lis:
            im_birth[col] = im_birth[
                col]/im_birth['Total population']

        im_birth = im_birth[['LocalArea',
                             'Non-immigrants',
                             'Non-permanent residents',
                             'Immigrants']]

        im_birth = fill_missing_year(im_birth, start_year, end_year)
        return im_birth

    ################
    # Merge Census #
    ################

    list_years = {2001: [1997, 2002],
                  2006: [2002, 2007],
                  2011: [2007, 2012],
                  2016: [2012, 2020]}
    excluded = ["official_language", "worker_class",
                "immigration_period", "immigration_age"]

    file_names = [os.path.splitext(entry.name)[0]
                  for entry in os.scandir("data/processed/census_2001")
                  if os.path.splitext(entry.name)[0]
                  not in excluded and entry.is_file()]

    for f in file_names:
        df_f = []
        for y in list_years.keys():
            # read csv
            df_y = pd.read_csv("data/processed/census_" + str(y) + "/" + f + ".csv")

            # clean dataframe
            if f == "population_age_sex":
                func_name = "clean_age"
            else:
                func_name = "clean_" + f

            df_f.append(eval(func_name)(df_y,
                                        list_years[y][0],
                                        list_years[y][1]))

        # merge dataframes
        licence_df = merge_data(df_f, licence_df)

        if f == "population_age_sex":
            df_f = []
            for y in list_years.keys():
                df_y = pd.read_csv("data/processed/census_" + str(y) + "/" + f + ".csv")

                df_f.append(clean_gender(df_y,
                                         list_years[y][0],
                                         list_years[y][1]))

            licence_df = merge_data(df_f, licence_df)

    #################
    # Merge Parking #
    #################

    disability_parking_df = pd.read_csv(
        "data/raw/disability-parking.csv", sep=';')
    parking_meters_df = pd.read_csv(
        "data/raw/parking-meters.csv", sep=';')

    # only keeping Geom, and Geo Local Area column
    disability_parking_df = disability_parking_df[['Geom', 'Geo Local Area']]
    # groupby Local area to get a count of how many parking in a local area
    area_count_df = disability_parking_df.groupby('Geo Local Area').count()
    area_count_df.rename(columns={'Geom': 'Disability parking'}, inplace=True)
    # this is kept for individual point/for vis
    disability_parking_df = disability_parking_df.merge(
        area_count_df, on='Geo Local Area', how='left')

    # same processing as disability dataset
    parking_meters_df = parking_meters_df[['Geom', 'Geo Local Area']]
    meter_count_df = parking_meters_df.groupby('Geo Local Area').count()
    meter_count_df.rename(columns={'Geom': 'Parking meters'}, inplace=True)
    # this is kept for individual point
    parking_meters_df = parking_meters_df.merge(
        meter_count_df, on='Geo Local Area', how='left')
    
    # combine two parking
    final_parking_df = meter_count_df.merge(
        area_count_df, on='Geo Local Area', how='outer')

    # combine with licence
    licence_df.rename(columns={'LocalArea': 'Geo Local Area'}, inplace=True)
    licence_df = licence_df.merge(
        final_parking_df, on='Geo Local Area', how='left')

    #############
    # Save File #
    #############

    licence_df.rename(columns={'Geo Local Area': 'LocalArea'}).to_csv(
        save_to, index=False)

def test_fun():
    """
    Checks if the req. i/p files exist and if the main function is able\
    to store the results at correct location
    """
    main(path_in="data/processed/03_cleaned_validate.csv", save_to="data/processed/04_combined_validate.csv")
    # Confirm input and output CSV files exist or not
    assert os.path.exists("data/processed/03_cleaned_train.csv"), "Input train csv file\
                                                            not found in location"
    assert os.path.exists("data/processed/03_cleaned_validate.csv"), "Input validation csv file\
                                                            not found in location"
    assert os.path.exists("data/processed/03_cleaned_test.csv"), "Input test csv file\
                                                            not found in location"
    assert os.path.exists("data/processed/04_combined_validate.csv.csv"), "Output CSV file\
                                                            not found in location"
    print("Tests cleared successfully")


if __name__ == "__main__":
    test_fun()
    main(opt["--path_in"], opt["--save_to"])