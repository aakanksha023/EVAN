# author: Xinwen Wang
# date: 2020-05-21

"""
This script performs data wrangling and sythesis for multiple csv
and saves it to a specified file path. The input licence data needs to
be the output of 03_clean_wrangle.py script. The ouput will be feeding into
machine learning algorithm and visualization.

Usage: src/02_clean_wrangle/06_sythesis.py --file_path=<file_path>  \
--save_to1=<save_to1> --save_to2=<save_to2> \
--save_to3=<save_to3> --save_to4=<save_to4>

Options:
--file_path=<file_path>         A txt file storing two-dimensional array,
                                    specifing the file path for input dataset.
--save_to1=<save_to1>           This is the file path the processed training
                                    csv will be saved to
--save_to2=<save_to2>           This is the file path the parking
                                    meters for visualization will be saved to
--save_to3=<save_to3>           This is the file path the disability parking
                                    for visualization will be saved to
--save_to4=<save_to4>           This is the file path the licence data for
                                    visualization will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import numpy as np
import zipfile
import json
import re
from datetime import datetime


opt = docopt(__doc__)


def main(file_path, save_to1, save_to2, save_to3, save_to4):

    # read files

    with open(file_path, 'r') as file:
        file_path = file.read().replace('\n', '')

    file_path = file_path.strip('[]')
    file_path = re.findall(r'\([^\)\(]*\)', file_path)

    file_lis = []

    for file in file_path:
        file_name = file.strip('()')
        file_lis.append(file_name)

    disability_parking_df = pd.read_csv(file_lis[0], sep=';')
    parking_meters_df = pd.read_csv(file_lis[1], sep=';')

    licence_df = pd.read_csv(file_lis[2], low_memory=False)

    # census
    family_2001 = pd.read_csv(file_lis[5])
    family_2006 = pd.read_csv(file_lis[6])
    family_2011 = pd.read_csv(file_lis[7])
    family_2016 = pd.read_csv(file_lis[8])
    language_2001 = pd.read_csv(file_lis[9])
    language_2006 = pd.read_csv(file_lis[10])
    language_2011 = pd.read_csv(file_lis[11])
    language_2016 = pd.read_csv(file_lis[12])
    marital_2001 = pd.read_csv(file_lis[13])
    marital_2006 = pd.read_csv(file_lis[14])
    marital_2011 = pd.read_csv(file_lis[15])
    marital_2016 = pd.read_csv(file_lis[16])
    population_2001 = pd.read_csv(file_lis[17])
    population_2006 = pd.read_csv(file_lis[18])
    population_2011 = pd.read_csv(file_lis[19])
    population_2016 = pd.read_csv(file_lis[20])
    minority_2001 = pd.read_csv(file_lis[21])
    minority_2006 = pd.read_csv(file_lis[22])
    minority_2011 = pd.read_csv(file_lis[23])
    minority_2016 = pd.read_csv(file_lis[24])
    dwelling_2001 = pd.read_csv(file_lis[25])
    dwelling_2006 = pd.read_csv(file_lis[26])
    dwelling_2011 = pd.read_csv(file_lis[27])
    dwelling_2016 = pd.read_csv(file_lis[28])
    shelter_2001 = pd.read_csv(file_lis[29])
    shelter_2006 = pd.read_csv(file_lis[30])
    shelter_2011 = pd.read_csv(file_lis[31])
    shelter_2016 = pd.read_csv(file_lis[32])
    lone_parent_2001 = pd.read_csv(file_lis[33])
    lone_parent_2006 = pd.read_csv(file_lis[34])
    lone_parent_2011 = pd.read_csv(file_lis[35])
    lone_parent_2016 = pd.read_csv(file_lis[36])
    imgra_period_2001 = pd.read_csv(file_lis[37])
    imgra_period_2006 = pd.read_csv(file_lis[38])
    imgra_period_2011 = pd.read_csv(file_lis[39])
    imgra_period_2016 = pd.read_csv(file_lis[40])
    citizen_2001 = pd.read_csv(file_lis[41])
    citizen_2006 = pd.read_csv(file_lis[42])
    citizen_2011 = pd.read_csv(file_lis[43])
    citizen_2016 = pd.read_csv(file_lis[44])
    generation_2001 = pd.read_csv(file_lis[45])
    generation_2006 = pd.read_csv(file_lis[46])
    generation_2011 = pd.read_csv(file_lis[47])
    generation_2016 = pd.read_csv(file_lis[48])
    household_size_2001 = pd.read_csv(file_lis[49])
    household_size_2006 = pd.read_csv(file_lis[50])
    household_size_2011 = pd.read_csv(file_lis[51])
    household_size_2016 = pd.read_csv(file_lis[52])
    household_type_2001 = pd.read_csv(file_lis[53])
    household_type_2006 = pd.read_csv(file_lis[54])
    household_type_2011 = pd.read_csv(file_lis[55])
    household_type_2016 = pd.read_csv(file_lis[56])
    imgra_age_2001 = pd.read_csv(file_lis[57])
    imgra_age_2006 = pd.read_csv(file_lis[58])
    imgra_age_2011 = pd.read_csv(file_lis[59])
    imgra_age_2016 = pd.read_csv(file_lis[60])
    industry_2001 = pd.read_csv(file_lis[61])
    industry_2006 = pd.read_csv(file_lis[62])
    industry_2011 = pd.read_csv(file_lis[63])
    industry_2016 = pd.read_csv(file_lis[64])
    labour_2001 = pd.read_csv(file_lis[65])
    labour_2006 = pd.read_csv(file_lis[66])
    labour_2011 = pd.read_csv(file_lis[67])
    labour_2016 = pd.read_csv(file_lis[68])
    mobility_2001 = pd.read_csv(file_lis[69])
    mobility_2006 = pd.read_csv(file_lis[70])
    mobility_2011 = pd.read_csv(file_lis[71])
    mobility_2016 = pd.read_csv(file_lis[72])
    occupation_2001 = pd.read_csv(file_lis[73])
    occupation_2006 = pd.read_csv(file_lis[74])
    occupation_2011 = pd.read_csv(file_lis[75])
    occupation_2016 = pd.read_csv(file_lis[76])
    time_worked_2001 = pd.read_csv(file_lis[77])
    time_worked_2006 = pd.read_csv(file_lis[78])
    time_worked_2011 = pd.read_csv(file_lis[79])
    time_worked_2016 = pd.read_csv(file_lis[80])
    transport_2001 = pd.read_csv(file_lis[81])
    transport_2006 = pd.read_csv(file_lis[82])
    transport_2011 = pd.read_csv(file_lis[83])
    transport_2016 = pd.read_csv(file_lis[84])
    workplace_2001 = pd.read_csv(file_lis[85])
    workplace_2006 = pd.read_csv(file_lis[86])
    workplace_2011 = pd.read_csv(file_lis[87])
    workplace_2016 = pd.read_csv(file_lis[88])
    education_2001 = pd.read_csv(file_lis[89])
    education_2006 = pd.read_csv(file_lis[90])
    education_2011 = pd.read_csv(file_lis[91])
    education_2016 = pd.read_csv(file_lis[92])
    im_birth_2001 = pd.read_csv(file_lis[93])
    im_birth_2006 = pd.read_csv(file_lis[94])
    im_birth_2011 = pd.read_csv(file_lis[95])
    im_birth_2016 = pd.read_csv(file_lis[96])

    # suppress warning
    pd.options.mode.chained_assignment = None

    # read from zip file
    vancouver_zip_path = file_lis[3]
    with zipfile.ZipFile(vancouver_zip_path, "r") as z:
        with z.open("14100096.csv") as f:
            vancouver_employment = pd.read_csv(f, header=0, delimiter=",")

    bc_zip_path = file_lis[4]
    with zipfile.ZipFile(bc_zip_path, "r") as z:
        with z.open("14100327.csv") as f:
            bc_employment = pd.read_csv(f, header=0, delimiter=",")

    # clean

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

    # Clean bc employmentd data, only need 1997-2000 as subsitude for vancouver
    bc_unemployment = bc_employment[
        (bc_employment['GEO'] == 'British Columbia') &
        (bc_employment['Labour force characteristics'] ==
         'Unemployment rate') &
        (bc_employment['REF_DATE'] < 2001) &
        (1996 < bc_employment['REF_DATE']) &
        (bc_employment['UOM'] == 'Percentage') &
        (bc_employment['Age group'] == '15 years and over') &
        (bc_employment['Sex'] == 'Both sexes')][['REF_DATE', 'VALUE']]

    # clean Vancouver data, since BC level only have unemployment,
    # use unemployment rate note unemployment+employment !=1
    vancouver_unemployment = vancouver_employment[
        (vancouver_employment['GEO'] == 'Vancouver, British Columbia') &
        (vancouver_employment[
            'Labour force characteristics'] == 'Unemployment rate') &
        (vancouver_employment['Sex'] == 'Both sexes') &
        (vancouver_employment['UOM'] == 'Percentage') &
        (vancouver_employment[
            'Age group'] == '15 years and over')][['REF_DATE', 'VALUE']]

    unemployment_rate = pd.concat([bc_unemployment, vancouver_unemployment])

    ###############
    # Census Data #
    ###############

    def fill_missing_year(df, start_year, end_year):
        """
        This function will repeat the dataframe and fill the year
        from the start to end
        Args:
            df (pandas dataframe): The dataframe
            start_year (int): The four digit strat year
            end_year (int): The four digit end year, note end year not included

        Returns:
            df: The expanded dataframe

        """

        year_lis = list(range(start_year, end_year))
        df = pd.concat([df]*len(year_lis))
        df.reset_index(drop=True, inplace=True)
        df['Year'] = 0
        i = 0

        for year in year_lis:
            df.iloc[i:i+24]['Year'] = year
            i += 24

        return df

    # family sub-data
    def clean_family(family, start_year, end_year):
        """
        This function cleans the family census data
        Args:
            family (pandas dataframe): The dataframe for family data
            start_year (int): The four digit strat year
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

    #family_2001 = clean_family(family_2001, 1997, 2002)
    #family_2006 = clean_family(family_2006, 2002, 2007)
    #family_2011 = clean_family(family_2011, 2007, 2012)
    #family_2016 = clean_family(family_2016, 2012, 2020)

    # language sub-data
    def clean_language(language, start_year, end_year):
        """
        This function cleans the language census data
        Args:
            language (pandas dataframe): The dataframe for language data
            start_year (int): The four digit strat year
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

    language_2001 = clean_language(language_2001, 1997, 2002)
    language_2006 = clean_language(language_2006, 2002, 2007)
    language_2011 = clean_language(language_2011, 2007, 2012)
    language_2016 = clean_language(language_2016, 2012, 2020)

    # marital sub-data
    def clean_marital(marital, start_year, end_year):
        """
        This function cleans the marital census data
        Args:
            marital (pandas dataframe): The dataframe for language data
            start_year (int): The four digit strat year
            end_year (int): The four digit end year, note end year not included

        Returns:
            marital: A cleaned pandas dataframe

        """

        marital['Married or living with a or common-law partner'] = marital[
            'Married or living with a or common-law partner'] / \
            marital['Total population 15 years and over']
        marital[
            'Not living with a married spouse or common-law partner'] = \
            marital['Not living with a married spouse or common-law partner'] / \
            marital['Total population 15 years and over']

        if start_year == 2007 or start_year == 2012:
            marital = marital.query('Type == "total"')

        marital = marital[['LocalArea',
                           'Married or living with a or common-law partner',
                           'Not living with a married spouse or common-law partner']]

        marital = fill_missing_year(marital, start_year, end_year)
        return marital

    marital_2001 = clean_marital(marital_2001, 1997, 2002)
    marital_2006 = clean_marital(marital_2006, 2002, 2007)
    marital_2011 = clean_marital(marital_2011, 2007, 2012)
    marital_2016 = clean_marital(marital_2016, 2012, 2020)

    # population sub-data
    def clean_age(age, start_year, end_year):
        """
        This function cleans the marital census data
        Args:
            age (pandas dataframe): The dataframe for population data
            start_year (int): The four digit strat year
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

    age_2001 = clean_age(population_2001, 1997, 2002)
    age_2006 = clean_age(population_2006, 2002, 2007)
    age_2011 = clean_age(population_2011, 2007, 2012)
    age_2016 = clean_age(population_2016, 2012, 2020)

    # gender
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

    gender_2001 = clean_gender(population_2001, 1997, 2002)
    gender_2006 = clean_gender(population_2006, 2002, 2007)
    gender_2011 = clean_gender(population_2011, 2007, 2012)
    gender_2016 = clean_gender(population_2016, 2012, 2020)

    # visible minority
    def clean_minority(mino, start_year, end_year):

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

    minority_2001 = clean_minority(minority_2001, 1997, 2002)
    minority_2006 = clean_minority(minority_2006, 2002, 2007)
    minority_2011 = clean_minority(minority_2011, 2007, 2012)
    minority_2016 = clean_minority(minority_2016, 2012, 2020)

    # dwelling
    def clean_dwelling(dwel, start_year, end_year):

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
            dwel['dwelling_Other'] = (
                dwel['Total'] - dwel[
                    'dwelling_Apartment'] - dwel[
                    'dwelling_House'])/dwel['Total']

        else:
            dwel['dwelling_Apartment'] = (dwel[
                'Apartment, detached duplex'] + dwel[
                'Apartment, building that has five or more storeys'
            ] + dwel[
                'Apartment, building that has fewer than five storeys'
            ])/dwel['Total']
            dwel['dwelling_Other'] = (
                dwel['Total'] - dwel[
                    'dwelling_Apartment'] - dwel['dwelling_House'
                                                 ])/dwel['Total']

        dwel = dwel[['LocalArea',
                     'dwelling_House',
                     'dwelling_Apartment']]

        dwel = fill_missing_year(dwel, start_year, end_year)
        return dwel

    dwelling_2001 = clean_dwelling(dwelling_2001, 1997, 2002)
    dwelling_2006 = clean_dwelling(dwelling_2006, 2002, 2007)
    dwelling_2011 = clean_dwelling(dwelling_2011, 2007, 2012)
    dwelling_2016 = clean_dwelling(dwelling_2016, 2012, 2020)

    # shelter tenure
    def clean_shelter(shel, start_year, end_year):

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

    shelter_2001 = clean_shelter(shelter_2001, 1997, 2002)
    shelter_2006 = clean_shelter(shelter_2006, 2002, 2007)
    shelter_2011 = clean_shelter(shelter_2011, 2007, 2012)
    shelter_2016 = clean_shelter(shelter_2016, 2012, 2020)

    # lone parent
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

    lone_parent_2001 = clean_lone_parent(lone_parent_2001, 1997, 2002)
    lone_parent_2006 = clean_lone_parent(lone_parent_2006, 2002, 2007)
    lone_parent_2011 = clean_lone_parent(lone_parent_2011, 2007, 2012)
    lone_parent_2016 = clean_lone_parent(lone_parent_2016, 2012, 2020)

    # immigrates_period
    def clean_imgra_period(im_p, start_year, end_year):
        # please note that start year should only be 1997 or 2002 or 2007 or 2012
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
                'Invalid start year. A valid start year should be 1997 or 2002 or 2007 or 2012')

        im_p['Immigrates'] = im_p[
            'Immigrates'] / im_p['Total immigrant population']

        im_p = im_p[['LocalArea',
                     'Immigrates']]

        im_p = fill_missing_year(im_p, start_year, end_year)
        return im_p

    #imgra_period_2001 = clean_imgra_period(imgra_period_2001, 1997, 2002)
    #imgra_period_2006 = clean_imgra_period(imgra_period_2006, 2002, 2007)
    # note this is not an error, intentional using 2016
    #imgra_period_2011 = clean_imgra_period(imgra_period_2016, 2007, 2012)
    #imgra_period_2016 = clean_imgra_period(imgra_period_2016, 2012, 2020)

    # citizenship
    def clean_citizen(citizen, start_year, end_year):

        if start_year == 2007:
            citizen = citizen[citizen['Unnamed: 0'] == 0]

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

    #citizen_2001 = clean_citizen(citizen_2001, 1997, 2002)
    #citizen_2006 = clean_citizen(citizen_2006, 2002, 2007)
    #citizen_2011 = clean_citizen(citizen_2011, 2007, 2012)
    #citizen_2016 = clean_citizen(citizen_2016, 2012, 2020)

    # generation
    def clean_generation(gen, start_year, end_year):
        for i in gen.columns[3:]:
            gen[i] = gen[i]/gen[gen.columns[2]]

        gen = gen.iloc[:, [1, 3, 4, 5]]
        gen = fill_missing_year(gen, start_year, end_year)
        return gen

    generation_2001 = clean_generation(generation_2001, 1997, 2002)
    generation_2006 = clean_generation(generation_2006, 2002, 2007)
    generation_2011 = clean_generation(generation_2011, 2007, 2012)
    generation_2016 = clean_generation(generation_2016, 2012, 2020)

    # household size
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
                     '6 or more persons': '6 or more persons household'}, inplace=True)

        house_size = house_size[[
            'LocalArea', '1 person household',
            '2 persons household', '3 persons household',
            '4 to 5 persons household',
            '6 or more persons household']]
        
        house_size = fill_missing_year(house_size, start_year, end_year)
        return house_size

    household_size_2001 = clean_household_size(household_size_2001, 1997, 2002)
    household_size_2006 = clean_household_size(household_size_2006, 2002, 2007)
    household_size_2011 = clean_household_size(household_size_2011, 2007, 2012)
    household_size_2016 = clean_household_size(household_size_2016, 2012, 2020)

    # household type
    #household_type_2001 = clean_generation(household_type_2001, 1997, 2002)
    #household_type_2006 = clean_generation(household_type_2006, 2002, 2007)
    #household_type_2011 = clean_generation(household_type_2011, 2007, 2012)
    #household_type_2016 = clean_generation(household_type_2016, 2012, 2020)

    # immigration age
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

    #imgra_age_2001 = imgra_age_2006.copy()
    #imgra_age_2001 = clean_imgra_age(imgra_age_2001, 2002, 2007)
    #imgra_age_2006 = clean_imgra_age(imgra_age_2006, 2002, 2007)
    #imgra_age_2011 = clean_imgra_age(imgra_age_2011, 2007, 2012)
    #imgra_age_2016 = clean_imgra_age(imgra_age_2016, 2012, 2020)

    # industry
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

    industry_2001 = clean_industry(industry_2001, 1997, 2002)
    industry_2006 = clean_industry(industry_2006, 2002, 2007)
    industry_2011 = clean_industry(industry_2011, 2007, 2012)
    industry_2016 = clean_industry(industry_2016, 2012, 2020)

    # labour force
    def clean_labour_force(labour, start_year, end_year):
        labour = labour[labour['Type'] == 'Total']

        labour = labour[['LocalArea',
                         'Employment rate',
                         'Unemployment rate']]

        labour = fill_missing_year(labour, start_year, end_year)
        return labour

    labour_2001 = clean_labour_force(labour_2001, 1997, 2002)
    labour_2006 = clean_labour_force(labour_2006, 2002, 2007)
    labour_2011 = clean_labour_force(labour_2011, 2007, 2012)
    labour_2016 = clean_labour_force(labour_2016, 2012, 2020)

    # mobility
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

    #mobility_2001 = clean_mobility(mobility_2001, 1997, 2002)
    #mobility_2006 = clean_mobility(mobility_2006, 2002, 2007)
    #mobility_2011 = clean_mobility(mobility_2011, 2007, 2012)
    #mobility_2016 = clean_mobility(mobility_2016, 2012, 2020)

    # occupation
    def clean_occupation(occ, start_year, end_year):

        occ['total'] = occ[
            list(occ.columns)[3]] + occ[list(occ.columns)[4]]

        col_lis = list(occ.columns)[4:]
        for col in col_lis:
            occ[col] = occ[col]/occ['total']

        occ.drop(columns=['Type',
                          'All occupations',
                          'Unnamed: 0',
                          'total'], inplace=True)

        occ = fill_missing_year(occ, start_year, end_year)
        return occ

    occupation_2001 = clean_occupation(occupation_2001, 1997, 2002)
    occupation_2006 = clean_occupation(occupation_2006, 2002, 2007)
    occupation_2011 = clean_occupation(occupation_2011, 2007, 2012)
    occupation_2016 = clean_occupation(occupation_2016, 2012, 2020)

    # time_worked
    def time_worked(tw, start_year, end_year):

        tw = tw.query('Type == "total"')
        col_lis = list(tw.columns)[4:6]

        for col in col_lis:
            tw[col] = tw[col]/tw[
                'Population 15 years and over by work activity']

        tw = tw[['LocalArea',
                 'full time',
                 'part time']]

        tw = fill_missing_year(tw, start_year, end_year)
        return tw

    time_worked_2001 = time_worked(time_worked_2001, 1997, 2002)
    time_worked_2006 = time_worked(time_worked_2006, 2002, 2007)
    time_worked_2011 = time_worked(time_worked_2011, 2007, 2012)
    time_worked_2016 = time_worked(time_worked_2016, 2012, 2020)

    # transit
    def clean_transport(trans, start_year, end_year):

        trans = trans.query('Type == "total"')

        cols = list(trans.columns)[4:]
        for c in cols:
            trans[c] = trans[c]/trans['Total']

        trans.drop(columns=['Unnamed: 0',
                            'Type',
                            'Total'], inplace=True)

        trans = fill_missing_year(trans, start_year, end_year)
        return trans

    transport_2001 = clean_transport(transport_2001, 1997, 2002)
    transport_2006 = clean_transport(transport_2006, 2002, 2007)
    transport_2011 = clean_transport(transport_2011, 2007, 2012)
    transport_2016 = clean_transport(transport_2016, 2012, 2020)

    # workplace
    def clean_workplace(wp, start_year, end_year):

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

    workplace_2001 = clean_workplace(workplace_2001, 1997, 2002)
    workplace_2006 = clean_workplace(workplace_2006, 2002, 2007)
    workplace_2011 = clean_workplace(workplace_2011, 2007, 2012)
    workplace_2016 = clean_workplace(workplace_2016, 2012, 2020)

    # education
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

    education_2001 = clean_education(education_2001, 1997, 2002)
    education_2006 = clean_education(education_2006, 2002, 2007)
    education_2011 = clean_education(education_2011, 2007, 2012)
    education_2016 = clean_education(education_2016, 2012, 2020)

    # birth place
    def clean_im_birth(im_birth, start_year, end_year):

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

    im_birth_2001 = clean_im_birth(im_birth_2001, 1997, 2002)
    im_birth_2006 = clean_im_birth(im_birth_2006, 2002, 2007)
    im_birth_2011 = clean_im_birth(im_birth_2011, 2007, 2012)
    im_birth_2016 = clean_im_birth(im_birth_2016, 2012, 2020)

    # wrangle the Geom into coordinates
    parking_meters_df["coord-x"] = parking_meters_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][0])
    parking_meters_df["coord-y"] = parking_meters_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][1])
    disability_parking_df["coord-x"] = disability_parking_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][0])
    disability_parking_df["coord-y"] = disability_parking_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][1])

    # filter out point without Geom location
    licence_vis_df = licence_df[~licence_df['Geom'].isnull()]
    licence_vis_df["coord-x"] = licence_vis_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][0])
    licence_vis_df["coord-y"] = licence_vis_df['Geom'].apply(
        lambda p: json.loads(p)['coordinates'][1])

    # synthesis

    def merge_data(df1, df2, df3, df4, licence_df):

        whole = pd.concat([df1, df2, df3, df4])
        whole.rename(columns={'LocalArea': 'Geo Local Area',
                              'Year': 'FOLDERYEAR'}, inplace=True)
        licence_df = licence_df.merge(
            whole, on=['Geo Local Area', 'FOLDERYEAR'], how='left')

        return licence_df

    # combine two parking
    final_parking_df = meter_count_df.merge(
        area_count_df, on='Geo Local Area', how='outer')

    # combine with licence
    licence_df.rename(columns={'LocalArea': 'Geo Local Area'}, inplace=True)
    licence_df = licence_df.merge(
        final_parking_df, on='Geo Local Area', how='left')

    # change folderyear to be int
    licence_df = licence_df.astype({'FOLDERYEAR': 'int'})
    unemployment_rate.rename(
        columns={'REF_DATE': 'FOLDERYEAR',
                 'VALUE': 'Unemployment_rate'}, inplace=True)
    licence_df = licence_df.merge(
        unemployment_rate, on='FOLDERYEAR', how='left')

    # census data
    # licence_df = merge_data(family_2001, family_2006,
    #                        family_2011, family_2016, licence_df)

#     licence_df = merge_data(language_2001, language_2006,
#                              language_2011, language_2016, licence_df)

#     licence_df = merge_data(marital_2001, marital_2006,
#                             marital_2011, marital_2016, licence_df)

#     licence_df = merge_data(age_2001, age_2006,
#                             age_2011, age_2016, licence_df)

#     licence_df = merge_data(gender_2001, gender_2006,
#                             gender_2011, gender_2016, licence_df)

#     licence_df = merge_data(minority_2001, minority_2006,
#                             minority_2011, minority_2016, licence_df)

#     licence_df = merge_data(dwelling_2001, dwelling_2006,
#                             dwelling_2011, dwelling_2016, licence_df)

#     licence_df = merge_data(shelter_2001, shelter_2006,
#                             shelter_2011, shelter_2016, licence_df)

#     licence_df = merge_data(lone_parent_2001, lone_parent_2006,
#                             lone_parent_2011, lone_parent_2016, licence_df)

    # licence_df = merge_data(imgra_period_2001, imgra_period_2006,
    #                        imgra_period_2011, imgra_period_2016, licence_df)

    # licence_df = merge_data(citizen_2001, citizen_2006,
    #                        citizen_2011, citizen_2016, licence_df)

#     licence_df = merge_data(generation_2001, generation_2006,
#                             generation_2011, generation_2016, licence_df)

#     licence_df = merge_data(household_size_2001, household_size_2006,
#                             household_size_2011,
#                             household_size_2016, licence_df)

    # licence_df = merge_data(household_type_2001, household_type_2006,
    #                        household_type_2011,
    #                        household_type_2016, licence_df)

    # licence_df = merge_data(imgra_age_2001, imgra_age_2006,
    #                        imgra_age_2011, imgra_age_2016, licence_df)

#     licence_df = merge_data(industry_2001, industry_2006,
#                             industry_2011, industry_2016, licence_df)

#     licence_df = merge_data(labour_2001, labour_2006,
#                             labour_2011, labour_2016, licence_df)

    # licence_df = merge_data(mobility_2001, mobility_2006,
    #                        mobility_2011, mobility_2016, licence_df)

    licence_df = merge_data(occupation_2001, occupation_2006,
                            occupation_2011, occupation_2016, licence_df)

#     licence_df = merge_data(time_worked_2001, time_worked_2006,
#                             time_worked_2011, time_worked_2016, licence_df)

#     licence_df = merge_data(transport_2001, transport_2006,
#                             transport_2011, transport_2016, licence_df)

#     licence_df = merge_data(workplace_2001, workplace_2006,
#                             workplace_2011, workplace_2016, licence_df)

#     licence_df = merge_data(education_2001, education_2006,
#                             education_2011, education_2016, licence_df)

#     licence_df = merge_data(im_birth_2001, im_birth_2006,
#                             im_birth_2011, im_birth_2016, licence_df)

    # save to a new csv
    licence_df.rename(columns={'Geo Local Area': 'LocalArea'}).to_csv(
        save_to1, index=False)
    parking_meters_df.to_csv(save_to2, index=False)
    disability_parking_df.to_csv(save_to3, index=False)
    licence_vis_df.to_csv(save_to4, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to1"],
         opt["--save_to2"], opt["--save_to3"], opt["--save_to4"])
