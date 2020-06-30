# author: Aakanksha Dimri, Keanna Knebel, Jasmine Qin, Xinwen Wang
# date: 2020-06-02

"""
This script cleans the census dataset for a given year and saves them to
the file_path provided. This script takes the census year and the csv file
containing the census data as arguments.

Usage: src/02_clean_wrangle/05_clean_census.py --census_file=<census_file> \
    --year=<year> \
    --file_path=<file_path>

Options:
--census_file=<census_file>  csv file containing census data,
                             including file path.
--year=<year>                census year.
--file_path=<file_path>      Path to the exported files folder.
"""

from docopt import docopt
import pandas as pd
import os
import re
import warnings

pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore")

opt = docopt(__doc__)


def create_subgroup_dict(df, year):

    # separate dataframe by 'Variables' containing regex expressions:
    if year == 2001:
        re1 = ['total.*by', 'population.*by', 'common-law couples',
               '^Male', '^Female', 'total - male', 'total - female']

    elif year == 2006:
        re1 = [r'total.*by', r'population.*by', r'common-law couples',\
            r'^Male[s\s,]', r'^Female[s\s,]', r'total - mobility',\
            r'Average number of children']

    elif year == 2011:
        df.drop(index=201, inplace=True)
        re1 = ['total.*by', 'population.*by', 'common-law couples',
               'males', 'Total population excluding institutional residents',
               'Total.*in private households']

    elif year == 2016:
        re1 = ['^total', 'population.*by', 'males']

    subgroup = list(df[df.Variable.str.contains('|'.join(re1),
                                                flags=re.IGNORECASE)].index)
    subgroup.append(len(df.Variable)+1)
    subgroup = subgroup[1:]

    # create census dictionary of sub datasets
    # initialize variables for the lookup dictionary
    start = 0
    census_dict = {}

    for s in subgroup:
        sub_df = df.loc[start:s-1]

        # transpose dataframe and rename column
        sub_df = sub_df.set_index('Variable').T.reset_index()
        sub_df = sub_df.rename(columns={'index': 'LocalArea'})

        # check for duplicates and store dataframes into the dictionary
        if df.Variable[start] in census_dict:
            start = s
        else:
            census_dict[df.Variable[start]] = sub_df
            start = s

    return census_dict

###########################################################################
# HELPER  FUNCTIONS
###########################################################################


def clean_age(census_dict, year, file_path):

    if year == 2001:
        col_names = ['LocalArea', 'Type', 'Total', '0 to 4 years',
                     '5 to 9 years', '10 to 14 years', '15 to 19 years',
                     '20 to 24 years', '25 to 29 years', '30 to 34 years',
                     '35 to 39 years', '40 to 44 years', '45 to 49 years',
                     '50 to 54 years', '55 to 59 years', '60 to 64 years',
                     '65 to 69 years', '70 to 74 years', '75 to 79 years',
                     '80 to 84 years', '85 to 89 years', '90 to 94 years',
                     '95 to 99 years', '100 years and over']

        male = census_dict['Male']
        female = census_dict['Female']

        female.insert(1, 'Type', 'female')
        female.set_axis(col_names, axis=1, inplace=True)
        male.insert(1, 'Type', 'male')
        male.set_axis(col_names, axis=1, inplace=True)

        merged = pd.concat([female, male])
        merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
        total = merged.groupby('LocalArea').sum()
        total['Type'] = 'total'
        total.reset_index(inplace=True)
        merged = pd.concat([merged, total])

    else:
        if year == 2006:

            col_names = ['LocalArea', 'Type', 'Total', '0 to 4 years',
                         '5 to 9 years', '10 to 14 years', '15 to 19 years',
                         '20 to 24 years', '25 to 29 years', '30 to 34 years',
                         '35 to 39 years', '40 to 44 years', '45 to 49 years',
                         '50 to 54 years', '55 to 59 years', '60 to 64 years',
                         '65 to 69 years', '70 to 74 years', '75 to 79 years',
                         '80 to 84 years', '85 to 89 years', '90 to 94 years',
                         '95 to 99 years', '100 years and over', 'Median Age']

            total = census_dict['Male & Female, Total']
            male = census_dict['Male, Total']
            female = census_dict['Female, Total']

        elif year == 2011:

            col_names = ['LocalArea', 'Type', 'Total', '0 to 4 years',
                         '5 to 9 years', '10 to 14 years', '15 to 19 years',
                         '15 years', '16 years', '17 years', '18 years',
                         '19 years', '20 to 24 years', '25 to 29 years',
                         '30 to 34 years', '35 to 39 years', '40 to 44 years',
                         '45 to 49 years', '50 to 54 years', '55 to 59 years',
                         '60 to 64 years', '65 to 69 years', '70 to 74 years',
                         '75 to 79 years', '80 to 84 years',
                         '85 years and over', 'Median age',
                         '% of the population aged 15 and over']

            total = census_dict['Total population by age groups']
            male = census_dict['Males, total']
            female = census_dict['Females, total']

        elif year == 2016:

            col_names = ['LocalArea', 'Type', 'Total', '0 to 14 years',
                         '0 to 4 years', '5 to 9 years', '10 to 14 years',
                         '15 to 64 years', '15 to 19 years',
                         '20 to 24 years', '25 to 29 years',
                         '30 to 34 years', '35 to 39 years',
                         '40 to 44 years', '45 to 49 years',
                         '50 to 54 years', '55 to 59 years',
                         '60 to 64 years', '65 years and over',
                         '65 to 69 years', '70 to 74 years',
                         '75 to 79 years', '80 to 84 years',
                         '85 years and over', '85 to 89 years',
                         '90 to 94 years', '95 to 99 years',
                         '100 years and over']

            total = census_dict['Total - Age groups and average age of the population - 100% data']
            male = census_dict['Total - Age groups and average age of males - 100% data']
            female = census_dict['Total - Age groups and average age of females - 100% data']

        female.insert(1, 'Type', 'female')
        female.set_axis(col_names, axis=1, inplace=True)
        male.insert(1, 'Type', 'male')
        male.set_axis(col_names, axis=1, inplace=True)
        total.insert(1, 'Type', 'total')
        total.set_axis(col_names, axis=1, inplace=True)

        merged = pd.concat([female, male, total])

    merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
    census_dict['population by age and sex'] = merged
    merged.to_csv(file_path + '/population_age_sex.csv')

    return census_dict

###############################################################################


def clean_marital_status(census_dict, year, file_path):

    if year in [2001, 2006]:
        col_names = ['LocalArea', 'Total population 15 years and over',
                     'Single (never legally married)', 'Married',
                     'Separated', 'Divorced', 'Widowed', 'total x',
                     'Not living common law', 'Living common law']

        cols_ord = ['LocalArea', 'Total population 15 years and over',
                    'Married or living with a or common-law partner',
                    'Married', 'Living common law',
                    'Not living with a married spouse or common-law partner',
                    'Single (never legally married)', 'Separated',
                    'Divorced', 'Widowed']

        df1 = census_dict['Total population 15 years and over by legal marital status']
        df2 = census_dict['Total population 15 years and over by common-law status']

        merged = pd.merge(df1, df2, on=['LocalArea'])
        merged.set_axis(col_names, axis=1, inplace=True)

        merged['Married or living with a or common-law partner'] = merged['Married'] + merged['Living common law']
        merged['Not living with a married spouse or common-law partner'] = merged['Total population 15 years and over'] - merged['Married or living with a or common-law partner']
        merged = merged[cols_ord]

    else:
        if year == 2011:
            total = census_dict['Total population 15 years and over by marital status']
            male = census_dict['Males 15 years and over by marital status']
            female = census_dict['Females 15 years and over by marital status']

        elif year == 2016:
            total = census_dict['Total - Marital status for the population aged 15 years and over - 100% data']
            male = census_dict['Total - Marital status for males aged 15 years and over - 100% data']
            female = census_dict['Total - Marital status for females aged 15 years and over - 100% data']

        col_names = ['LocalArea', 'Type',
                     'Total population 15 years and over',
                     'Married or living with a or common-law partner',
                     'Married', 'Living common law',
                     'Not living with a married spouse or common-law partner',
                     'Single (never legally married)', 'Separated',
                     'Divorced', 'Widowed']

        female.insert(1, 'Type', 'female')
        female.set_axis(col_names, axis=1, inplace=True)
        male.insert(1, 'Type', 'male')
        male.set_axis(col_names, axis=1, inplace=True)
        total.insert(1, 'Type', 'total')
        total.set_axis(col_names, axis=1, inplace=True)

        merged = pd.concat([female, male, total])
        merged.sort_values(by=['LocalArea', 'Type'], inplace=True)

    census_dict['marital status'] = merged
    merged.to_csv(file_path + '/marital_status.csv')
    return census_dict

###############################################################################


def clean_couple_fam_structure(census_dict, year, file_path):

    col_names = ['LocalArea', 'Type', 'Total', 'Without children at home',
                 'With children at home', '1 child', '2 children',
                 '3 or more children']

    if year == 2016:
        total = census_dict['Total - Couple census families in private households - 100% data']
        total.insert(1, 'Type', 'total couples')
        total.set_axis(col_names, axis=1, inplace=True)

        census_dict['couples - family structure'] = total
        total.to_csv(file_path + '/couples_family_structure.csv')

    else:
        if year in [2011, 2006]:
            married = census_dict['Total couple families by family structure and number of children']
            married = married[['LocalArea', 'Married couples',
                               'Without children at home',
                               'With children at home', '1 child',
                               '2 children', '3 or more children']]
            common_law = census_dict['Common-law couples']

        elif year == 2001:
            married = census_dict['Total couple families by family structure']
            married = married[['LocalArea', 'Married couples',
                               'Without children at home',
                               'With children at home', '1 child',
                               '2 children', '3 or more children']]
            common_law = census_dict['Common-law couples']

        married.insert(1, 'Type', 'married couples')
        married.set_axis(col_names, axis=1, inplace=True)
        common_law.insert(1, 'Type', 'common-law couples')
        common_law.set_axis(col_names, axis=1, inplace=True)

        merged = pd.concat([married, common_law])
        total = merged.groupby('LocalArea').sum()
        total['Type'] = 'total couples'
        total.reset_index(inplace=True)
        merged = pd.concat([merged, total])

        merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
        census_dict['couples - family structure'] = merged
        merged.to_csv(file_path + '/couples_family_structure.csv')

    return census_dict

###############################################################################


def clean_language_detailed(census_dict, year, file_path):

    if year == 2006:
        mt_total = census_dict['Total population by mother tongue']
        home_total = census_dict['Total population by language spoken most often at home']
        home_total = home_total.iloc[:, 0:104].copy()
        work_total = census_dict['Total population 15 years and over who worked since January 1, 2005 by language used most often at work']

        mt_total.rename(columns={mt_total.columns[1]: 'Total'}, inplace=True)
        mt_total.insert(1, 'Type', 'mother tongue - total')
        home_total.rename(columns={home_total.columns[1]: 'Total'},
                          inplace=True)
        home_total.insert(1, 'Type',
                          'language most often spoken at home - total')
        work_total.rename(columns={work_total.columns[1]: 'Total'},
                          inplace=True)
        work_total.insert(1, 'Type',
                          'language most often spoken at work - total')

        merged = pd.concat([mt_total, home_total, work_total])

    elif year == 2001:
        mt_total = census_dict['Total population by mother tongue']
        home_total = census_dict['Total population by home language']
        home_total = home_total.groupby(home_total.columns, axis=1).sum()

        mt_total.rename(columns={mt_total.columns[1]: 'Total'}, inplace=True)
        mt_total.insert(1, 'Type', 'mother tongue - total')
        home_total.rename(columns={'Total population by home language': 'Total'}, inplace=True)
        home_total.insert(1, 'Type', 'language most often spoken at home - total')

        merged = pd.concat([mt_total, home_total])

    else:
        if year == 2011:
            mt_total = census_dict['Detailed mother tongue - Total population excluding institutional residents']
            mt_male = census_dict['Detailed mother tongue - Males excluding institutional residents']
            mt_female = census_dict['Detailed mother tongue - Females excluding institutional residents']

            home_total = census_dict['Detailed language spoken most often at home - Total population excluding institutional residents']
            home_male = census_dict['Detailed language spoken most often at home - Males excluding institutional residents']
            home_female = census_dict['Detailed language spoken most often at home - Females excluding institutional residents']

            home2_total = census_dict['Detailed other language spoken regularly at home - Total population excluding institutional residents']
            home2_male = census_dict['Detailed other language spoken regularly at home - Males excluding institutional residents']
            home2_female = census_dict['Detailed other language spoken regularly at home - Females excluding institutional residents']

        elif year == 2016:
            mt_total = census_dict['Total - Mother tongue for the total population excluding institutional residents - 100% data']
            mt_male = census_dict['Total - Mother tongue for males excluding institutional residents - 100% data']
            mt_female = census_dict['Total - Mother tongue for females excluding institutional residents - 100% data']

            home_total = census_dict['Total - Language spoken most often at home for the total population excluding institutional residents - 100% data']
            home_male = census_dict['Total - Language spoken most often at home for males excluding institutional residents - 100% data']
            home_female = census_dict['Total - Language spoken most often at home for females excluding institutional residents - 100% data']

            home2_total = census_dict['Total - Other language(s) spoken regularly at home for the total population excluding institutional residents - 100% data']
            home2_male = census_dict['Total - Other language(s) spoken regularly at home for males excluding institutional residents - 100% data']
            home2_female = census_dict['Total - Other language(s) spoken regularly at home for females excluding institutional residents - 100% data']

        mt_female.rename(columns={mt_female.columns[1]: 'Total'}, inplace=True)
        mt_female.insert(1, 'Type', 'mother tongue - female')
        mt_male.rename(columns={mt_male.columns[1]: 'Total'}, inplace=True)
        mt_male.insert(1, 'Type', 'mother tongue - male')
        mt_total.rename(columns={mt_total.columns[1]: 'Total'}, inplace=True)
        mt_total.insert(1, 'Type', 'mother tongue - total')

        home_female.rename(columns={home_female.columns[1]: 'Total'}, inplace=True)
        home_female.insert(1, 'Type', 'language most often spoken at home - female')
        home_male.rename(columns={home_male.columns[1]: 'Total'}, inplace=True)
        home_male.insert(1, 'Type', 'language most often spoken at home - male')
        home_total.rename(columns={home_total.columns[1]: 'Total'}, inplace=True)
        home_total.insert(1, 'Type', 'language most often spoken at home - total')

        home2_female.rename(columns={home2_female.columns[1]: 'Total'}, inplace=True)
        home2_female.insert(1, 'Type', 'other language spoken at home - female')
        home2_male.rename(columns={home2_male.columns[1]: 'Total'}, inplace=True)
        home2_male.insert(1, 'Type', 'other language spoken at home - male')
        home2_total.rename(columns={home2_total.columns[1]: 'Total'}, inplace=True)
        home2_total.insert(1, 'Type', 'other language spoken at home - total')

        merged = pd.concat([mt_female, mt_male, mt_total,
                            home_female, home_male, home_total,
                            home2_female, home2_male, home2_total])

    merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
    census_dict['detailed language'] = merged
    merged.to_csv(file_path + '/detailed_language.csv')

    return census_dict

###############################################################################


def clean_official_language(census_dict, year, file_path):
    col_names = ['LocalArea', 'Type', 'Total', 'English', 'French',
                 'English and French', 'Neither English nor French']

    if year == 2016:
        known = census_dict['Total - Knowledge of official languages for the total population excluding institutional residents - 100% data']
        first = census_dict['Total - First official language spoken for the total population excluding institutional residents - 100% data']

    elif year == 2011:
        known = census_dict['Knowledge of official languages - Total population excluding institutional residents']
        first = census_dict['First official language spoken - Total population excluding institutional residents']

    elif year in [2001, 2006]:
        known = census_dict['Total population by knowledge of official languages']
        first = census_dict['Total population by first official language spoken']

    known.insert(1, 'Type', 'knowledge of official languages')
    known.set_axis(col_names, axis=1, inplace=True)
    first.insert(1, 'Type', 'first official language spoken')
    first.set_axis(col_names, axis=1, inplace=True)

    merged = pd.concat([known, first])
    merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
    census_dict['official language'] = merged
    merged.to_csv(file_path + '/official_language.csv')

    return census_dict

###############################################################################


def clean_structural_dwelling_type(census_dict, year, file_path):

    if year == 2006:
        col_names = ['LocalArea', 'Total', 'Single-detached house',
                     'Semi-detached house', 'Row house', 'Apartment, duplex',
                     'Apartment, building that has five or more storeys']
        df = census_dict['Total number of occupied private dwellings by structural type of dwelling']

    elif year in [2001, 2011, 2016]:
        col_names = ['LocalArea', 'Total', 'Single-detached house',
                     'Semi-detached house', 'Row house',
                     'Apartment, detached duplex',
                     'Apartment, building that has five or more storeys',
                     'Apartment, building that has fewer than five storeys',
                     'Other single-attached house', 'Movable dwelling']

        if year == 2001:
            df = census_dict['Total number of occupied private dwellings by structural type of dwelling']
            df = df.iloc[:, 0:10].copy()

        elif year == 2011:
            df = census_dict['Total number of occupied private dwellings by structural type of dwelling']
            df = df[['LocalArea',
                     'Total number of occupied private dwellings by structural type of dwelling',
                     'Single-detached house', 'Semi-detached house',
                     'Row house', 'Apartment, duplex',
                     'Apartment, building that has five or more storeys',
                     'Apartment, building that has fewer than five storeys',
                     'Other single-attached house', 'Movable dwelling']].copy()

        elif year == 2016:
            df = census_dict['Total - Occupied private dwellings by structural type of dwelling - 100% data']
            df = df[['LocalArea',
                     'Total - Occupied private dwellings by structural type of dwelling - 100% data',
                     'Single-detached house', 'Semi-detached house',
                     'Row house', 'Apartment or flat in a duplex',
                     'Apartment in a building that has five or more storeys',
                     'Apartment in a building that has fewer than five storeys',
                     'Other single-attached house', 'Movable dwelling']].copy()

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['structural dwelling type'] = df
    df.to_csv(file_path + '/structural_dwelling_type.csv')

    return census_dict

###############################################################################


def clean_household_size(census_dict, year, file_path):

    if year == 2001:

        col_names = ['LocalArea', 'Total households', '1 person', '2 persons',
                     '3 persons', '4 to 5 persons', '6 or more persons',
                     'Average household size']

        df = census_dict['Total number of private households by household size']

    elif year in [2006, 2011]:

        col_names = ['LocalArea', 'Total households', '1 person', '2 persons',
                     '3 persons', '4 to 5 persons', '6 or more persons',
                     'Number of persons in private households',
                     'Average household size']

        df = census_dict['Total number of private households by household size']

    elif year == 2016:

        col_names = ['LocalArea', 'Total households', '1 person', '2 persons',
                     '3 persons', '4 persons', '5 or more persons',
                     'Number of persons in private households',
                     'Average household size']

        df = census_dict['Total - Private households by household size - 100% data']

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['household size'] = df
    df.to_csv(file_path + '/household_size.csv')

    return census_dict

###############################################################################


def clean_lone_parent(census_dict, year, file_path):
    col_names = ['LocalArea', 'Total lone-parent families', 'Female parent',
                 'Male parent', '1 child', '2 children', '3 or more children']

    if year == 2016:
        df1 = census_dict["Total lone-parent families by sex of parent"]
        df2 = census_dict["Total - Lone-parent census families in private households - 100% data"]

        df = pd.concat([df1, df2], axis=1)
        df = df.groupby(df.columns, axis=1).first()
        df = df[['LocalArea', 'Total lone-parent families by sex of parent',
                 'Female parent', 'Male parent', '1 child', '2 children',
                 '3 or more children']].copy()

    elif year == 2011:
        df = census_dict['Total lone-parent families by sex of parent and number of children']
        df = df.groupby(df.columns, axis=1).sum()
        df = df[['LocalArea',
                 'Total lone-parent families by sex of parent and number of children',
                 'Female parent', 'Male parent', '1 child', '2 children',
                 '3 or more children']].copy()

    elif year == 2006:
        df1 = census_dict['Total lone-parent families by sex of parent and number of children']
        df2 = census_dict['Female parent']
        df2 = df2.iloc[:, 1:5].copy()
        df3 = census_dict['Male parent']
        df3 = df3.iloc[:, 1:5].copy()

        df = pd.concat([df1, df2, df3], axis=1)
        df = df.groupby(df.columns, axis=1).sum()
        df = df[['LocalArea',
                 'Total lone-parent families by sex of parent and number of children',
                 'Female parent', 'Male parent', '1 child', '2 children',
                 '3 or more children']].copy()

    elif year == 2001:
        df1 = census_dict['Total lone-parent families by sex of parent']
        df2 = census_dict['Female parent']
        df2 = df2.iloc[:, 1:5].copy()
        df3 = census_dict['Male parent']
        df3 = df3.iloc[:, 1:5].copy()

        df = pd.concat([df1, df2, df3], axis=1)
        df = df.groupby(df.columns, axis=1).sum()
        df = df[['LocalArea', 'Total lone-parent families by sex of parent',
                 'Female parent', 'Male parent', '1 child', '2 children',
                 '3 or more children']].copy()

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['lone_parent'] = df
    df.to_csv(file_path + '/lone_parent.csv')

    return census_dict

###############################################################################


def clean_immigration_age(census_dict, year, file_path):

    if year in [2006, 2016]:
        col_names = ['LocalArea', 'Total immigrant population',
                     'Under 5 years', '5 to 14 years', '15 to 24 years',
                     '25 to 44 years', '45 years and over']

        if year == 2006:
            df = census_dict['Total immigrant population by age at immigration']

        elif year == 2016:
            df = census_dict['Total - Age at immigration for the immigrant population in private households - 25% sample data']

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 'Total immigrant population',
                     'Under 5 years', '5 to 14 years', '15 to 24 years',
                     '25 to 44 years', '45 years and over']

        df = pd.read_csv('data/processed/nhs/Age at immigration.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total immigrant population in private households by age at immigration',
                 '1_Under 5 years', '2_5 to 14 years', '3_15 to 24 years',
                 '4_25 to 44 years', '5_45 years and over']].copy()

    elif year == 2001:
        col_names = ['LocalArea', 'Total immigrant population',
                     'Under 5 years', '5 to 19 years', '20 years and over']
        df = census_dict['Total immigrant population by age at immigration']

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['immigration_age'] = df
    df.to_csv(file_path + '/immigration_age.csv')

    return census_dict

###############################################################################


def clean_immigration_period(census_dict, year, file_path):

    if year == 2001:
        col_names = ['LocalArea', 'Total immigrant population', 'Before 1961',
                     '1961 to 1970', '1971 to 1980', '1981 to 1990',
                     '1991 to 1995', '1996 to 2001']
        df = census_dict['Total immigrant population by period of immigration']

    elif year == 2006:
        col_names = ['LocalArea', 'Total immigrant population', 'Before 1961',
                     '1961 to 1970', '1971 to 1980', '1981 to 1990',
                     '1991 to 2000', '1991 to 1995', '1996 to 2000',
                     '2001 to 2006']
        df = census_dict['Total immigrant population by period of immigration']

    elif year == 2016:
        col_names = ['LocalArea', 'Total population', 'Non-immigrants',
                     'Non-permanent residents', 'Immigrants',
                     'Before 1981', '1981 to 1990', '1991 to 2000',
                     '2001 to 2010', '2001 to 2005', '2006 to 2010',
                     '2011 to 2016']

        df = census_dict['Total - Immigrant status and period of immigration for the population in private households - 25% sample data']
        df = df[['LocalArea',
                 'Total - Immigrant status and period of immigration for the population in private households - 25% sample data',
                 'Non-immigrants', 'Non-permanent residents', 'Immigrants',
                 'Before 1981', '1981 to 1990', '1991 to 2000', '2001 to 2010',
                 '2001 to 2005', '2006 to 2010', '2011 to 2016']].copy()

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 'Total population',
                     'Non-immigrants', 'Non-permanent residents', 'Immigrants',
                     'Before 1971', '1971 to 1980', '1981 to 1990',
                     '1991 to 2000', '2001 to 2005', '2006 to 2011']

        df = pd.read_csv('data/processed/nhs/Immigrant status and period of immigration.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total population in private households by immigrant status and period of immigration',
                 '1_Non-immigrants', '10_Non-permanent residents',
                 '2_Immigrants', '3_Before 1971', '4_1971 to 1980',
                 '5_1981 to 1990', '6_1991 to 2000', '8_2001 to 2005',
                 '9_2006 to 2011']].copy()

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['immigration_period'] = df
    df.to_csv(file_path + '/immigration_period.csv')

    return census_dict

###############################################################################


def clean_visible_minority(census_dict, year, file_path):

    col_names = ['LocalArea', 'Total population', 'Not a visible minority',
                 'Total visible minority population', 'Arab', 'Black',
                 'Chinese', 'Filipino', 'Japanese', 'Korean',
                 'Latin American', 'West Asian', 'South Asian',
                 'Southeast Asian', 'Multiple visible minorities',
                 'Other visible minority']

    if year == 2001:

        df = census_dict['Total population by visible minority groups']
        df = df[['LocalArea', 'Total population by visible minority groups',
                 'All others', 'Total visible minority population',
                 'Arab', 'Black', 'Chinese',  'Filipino', 'Japanese',
                 'Korean', 'Latin American', 'West Asian', 'South Asian',
                 'Southeast Asian', 'Multiple visible minorities',
                 'Visible minority, n.i.e.']].copy()

    elif year == 2006:

        df = census_dict['Total population by visible minority groups']
        df = df[['LocalArea', 'Total population by visible minority groups',
                 'Not a visible minority', 'Total visible minority population',
                 'Arab', 'Black', 'Chinese', 'Filipino', 'Japanese', 'Korean',
                 'Latin American', 'West Asian', 'South Asian',
                 'Southeast Asian', 'Multiple visible minority',
                 'Visible minority, n.i.e.']]

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 'Total population',
                     'Not a visible minority',
                     'Total visible minority population',
                     'Arab', 'Black', 'Chinese', 'Filipino', 'Japanese',
                     'Korean', 'Latin American', 'West Asian', 'South Asian',
                     'Southeast Asian', 'Multiple visible minorities',
                     'Other visible minority']

        df = pd.read_csv('data/processed/nhs/Visible minority population.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total population in private households by visible minority',
                 '14_Not a visible minority',
                 '1_Total visible minority population',
                 '7_Arab', '4_Black', '3_Chinese', '5_Filipino', '11_Japanese',
                 '10_Korean', '6_Latin American', '9_West Asian',
                 '2_South Asian', '8_Southeast Asian',
                 '13_Multiple visible minorities',
                 '12_Visible minority, n.i.e.']].copy()

    elif year == 2016:
        df = census_dict['Total visible minority population']
        df = df[['LocalArea', 'Total visible minority population',
                 'Not a visible minority', 'Total visible minority population',
                 'Arab', 'Black', 'Chinese', 'Filipino', 'Japanese', 'Korean',
                 'Latin American', 'West Asian', 'South Asian',
                 'Southeast Asian', 'Multiple visible minorities',
                 'Visible minority, n.i.e.']]

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['visible_minority'] = df
    df.to_csv(file_path + '/visible_minority.csv')

    return census_dict

###############################################################################


def clean_birth_place(census_dict, year, file_path):

    if year == 2001:
        col_names = ['LocalArea', 'Total population', 'Non-immigrants',
                     'Born in province of residence',
                     'Born outside province of residence',
                     'Non-permanent residents', 'Immigrants', 'United Kingdom',
                     "China", 'Italy', 'India', 'United States', 'Hong Kong',
                     'Philippines', 'Poland', 'Germany', 'Portugal',
                     'Viet Nam', 'Jamaica', 'Netherlands', 'Guyana', 'Greece',
                     'South Korea', 'France', 'Lebanon', 'Taiwan',
                     'Yugoslavia', 'Haiti', 'Ukraine', 'Croatia', 'Mexico',
                     'Egypt', 'South Africa', 'Ireland', 'Morocco', 'Austria',
                     'Switzerland', 'Other places of birth']

        df1 = census_dict['Total population by immigrant status and place of birth']
        df1 = df1.iloc[:, 1:5].copy()
        df2 = census_dict['Total immigrants by selected places of birth']

        df = pd.concat([df1, df2], axis=1)
        df = df[['LocalArea',
                 'Total population by immigrant status and place of birth',
                 'Non-immigrant population', 'Born in province of residence',
                 'Born outside province of residence',
                 'Non-permanent residents',
                 'Total immigrants by selected places of birth',
                 'United Kingdom', "China, People's Republic of",
                 'Italy', 'India', 'United States',
                 'Hong Kong, Special Administrative Region', 'Philippines',
                 'Poland', 'Germany', 'Portugal', 'Viet Nam', 'Jamaica',
                 'Netherlands', 'Guyana', 'Greece', 'Korea, South', 'France',
                 'Lebanon', 'Taiwan', 'Yugoslavia', 'Haiti', 'Ukraine',
                 'Croatia', 'Mexico', 'Egypt', 'South Africa, Republic of',
                 'Ireland, Republic of (EIRE)', 'Morocco', 'Austria',
                 'Switzerland', 'All other places of birth']].copy()

    elif year == 2006:
        col_names = ['LocalArea', 'Total population', 'Non-immigrants',
                     'Born in province of residence',
                     'Born outside province of residence',
                     'Non-permanent residents', 'Immigrants', 'United States',
                     'Central America', 'Caribbean and Bermuda',
                     'South America', 'Europe', 'Western Europe',
                     'Eastern Europe', 'Southern Europe',
                     'Italy', 'Other Southern Europe', 'Northern Europe',
                     'United Kingdom', 'Other Northern Europe', 'Africa',
                     'Western Africa', 'Eastern Africa', 'Northern Africa',
                     'Central Africa', 'Southern Africa',
                     'Asia and the Middle East',
                     'West Central Asia and the Middle East', 'Eastern Asia',
                     'China', 'Hong Kong', 'Other Eastern Asia',
                     'Southeast Asia', 'Philippines', 'Other Southeast Asia',
                     'Southern Asia', 'India', 'Other Southern Asia',
                     'Oceania and other']

        df = census_dict['Total population by immigrant status and place of birth']
        df = df[['LocalArea',
                 'Total population by immigrant status and place of birth',
                 'Non-immigrants', 'Born in province of residence',
                 'Born outside province of residence',
                 'Non-permanent residents', 'Immigrants',
                 'United States of America', 'Central America',
                 'Caribbean and Bermuda', 'South America', 'Europe',
                 'Western Europe', 'Eastern Europe', 'Southern Europe',
                 'Italy', 'Other Southern Europe', 'Northern Europe',
                 'United Kingdom', 'Other Northern Europe', 'Africa',
                 'Western Africa', 'Eastern Africa', 'Northern Africa',
                 'Central Africa', 'Southern Africa',
                 'Asia and the Middle East',
                 'West Central Asia and the Middle East', 'Eastern Asia',
                 "China, People's Republic of",
                 'Hong Kong, Special Administrative Region',
                 'Other Eastern Asia', 'Southeast Asia', 'Philippines',
                 'Other Southeast Asia', 'Southern Asia', 'India',
                 'Other Southern Asia', 'Oceania and other']]

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 'Total population', 'Non-immigrants',
                     'Born in province of residence',
                     'Born outside province of residence',
                     'Non-permanent residents', 'Immigrants',
                     'Afghanistan', 'Africa', 'Algeria', 'Americas', 'Asia',
                     'Bangladesh', 'Bosnia and Herzegovina', 'Chile', 'China',
                     'Colombia', 'Croatia', 'Egypt', 'El Salvador', 'Ethiopia',
                     'Europe', 'Fiji', 'France', 'Germany', 'Greece', 'Guyana',
                     'Haiti', 'Hong Kong', 'Hungary', 'India', 'Iran', 'Iraq',
                     'Ireland', 'Italy', 'Jamaica', 'Japan', 'Kenya',
                     'South Korea', 'Lebanon', 'Mexico', 'Morocco',
                     'Netherlands', 'Nigeria', 'Pakistan', 'Peru',
                     'Philippines', 'Poland', 'Portugal', 'Romania', 'Russia',
                     'Serbia', 'South Africa', 'Sri Lanka', 'Taiwan',
                     'Trinidad and Tobago', 'Turkey', 'Ukraine',
                     'United Kingdom', 'United States', 'Viet Nam',
                     'Oceania and other', 'Other Africa', 'Other Americas',
                     'Other Asia', 'Other Europe', 'Other places of birth']

        df = pd.read_csv('data/processed/nhs/Immigrant status and selected places of birth.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total population in private households by immigrant status and selected places of birth',
                 '1_Non-immigrants', '2_Born in province of residence',
                 '3_Born outside province of residence',
                 '65_Non-permanent residents', '4_Immigrants',
                 '58_Afghanistan', '35_Africa', '37_Algeria', '5_Americas',
                 '44_Asia', '57_Bangladesh', '31_Bosnia and Herzegovina',
                 '15_Chile', '46_China', '12_Colombia', '29_Croatia',
                 '38_Egypt', '13_El Salvador', '41_Ethiopia', '17_Europe',
                 '63_Fiji', '24_France', '20_Germany', '27_Greece', '8_Guyana',
                 '9_Haiti', '48_Hong Kong Special Administrative Region',
                 '30_Hungary', '45_India', '52_Iran', '56_Iraq',
                 '33_Ireland, Republic of', '19_Italy', '7_Jamaica',
                 '59_Japan', '42_Kenya', '53_Korea, South', '54_Lebanon',
                 '10_Mexico', '36_Morocco', '23_Netherlands', '40_Nigeria',
                 '50_Pakistan', '14_Peru', '47_Philippines', '21_Poland',
                 '22_Portugal', '25_Romania', '26_Russian Federation',
                 '32_Serbia', '39_South Africa, Republic of', '51_Sri Lanka',
                 '55_Taiwan', '11_Trinidad and Tobago', '60_Turkey',
                 '28_Ukraine', '18_United Kingdom', '6_United States',
                 '49_Viet Nam', '62_Oceania and other',
                 '43_Other places of birth in Africa',
                 '16_Other places of birth in Americas',
                 '61_Other places of birth in Asia',
                 '34_Other places of birth in Europe',
                 '64_Other places of birth']].copy()

    elif year == 2016:
        col_names = ['LocalArea', 'Total population', 'Non-immigrants',
                     'Non-permanent residents', 'Immigrants', 'Americas',
                     'Brazil', 'Colombia', 'El Salvador', 'Guyana', 'Haiti',
                     'Jamaica', 'Mexico', 'Peru', 'Trinidad and Tobago',
                     'United States', 'Other  Americas', 'Europe',
                     'Bosnia and Herzegovina', 'Croatia', 'France', 'Germany',
                     'Greece', 'Hungary', 'Ireland', 'Italy', 'Netherlands',
                     'Poland', 'Portugal', 'Romania', 'Russia', 'Serbia',
                     'Ukraine', 'United Kingdom', 'Other Europe', 'Africa',
                     'Algeria', 'Egypt', 'Ethiopia', 'Kenya', 'Morocco',
                     'Nigeria', 'Somalia', 'South Africa', 'Other Africa',
                     'Asia', 'Afghanistan', 'Bangladesh', 'China', 'Hong Kong',
                     'India', 'Iran', 'Iraq', 'Japan', 'South Korea',
                     'Lebanon', 'Pakistan', 'Philippines', 'Sri Lanka',
                     'Syria', 'Taiwan', 'Viet Nam', 'Other Asia',
                     'Oceania and other places of birth']

        df1 = census_dict['Total - Immigrant status and period of immigration for the population in private households - 25% sample data']
        df1 = df1[['Total - Immigrant status and period of immigration for the population in private households - 25% sample data',
                   'Non-immigrants', 'Non-permanent residents']].copy()
        df2 = census_dict['Total - Selected places of birth for the immigrant population in private households - 25% sample data']

        df = pd.concat([df1, df2], axis=1)
        df = df[['LocalArea',
                 'Total - Immigrant status and period of immigration for the population in private households - 25% sample data',
                 'Non-immigrants', 'Non-permanent residents',
                 'Total - Selected places of birth for the immigrant population in private households - 25% sample data',
                 'Americas', 'Brazil', 'Colombia', 'El Salvador', 'Guyana',
                 'Haiti', 'Jamaica', 'Mexico', 'Peru', 'Trinidad and Tobago',
                 'United States', 'Other places of birth in Americas',
                 'Europe', 'Bosnia and Herzegovina', 'Croatia', 'France',
                 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
                 'Netherlands', 'Poland', 'Portugal', 'Romania',
                 'Russian Federation', 'Serbia', 'Ukraine', 'United Kingdom',
                 'Other places of birth in Europe', 'Africa', 'Algeria',
                 'Egypt', 'Ethiopia', 'Kenya', 'Morocco', 'Nigeria', 'Somalia',
                 'South Africa, Republic of',
                 'Other places of birth in Africa', 'Asia', 'Afghanistan',
                 'Bangladesh', 'China', 'Hong Kong', 'India', 'Iran', 'Iraq',
                 'Japan', 'Korea, South', 'Lebanon', 'Pakistan', 'Philippines',
                 'Sri Lanka', 'Syria', 'Taiwan', 'Viet Nam',
                 'Other places of birth in Asia',
                 'Oceania and other places of birth']].copy()

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['immigration_birth_place'] = df
    df.to_csv(file_path + '/immigration_birth_place.csv')

    return census_dict

###############################################################################


def clean_shelter_tenure(census_dict, year, file_path):

    col_names = ['LocalArea', 'Total number of dwellings', 'Owned', 'Rented',
                 'Band housing']

    if year == 2001:
        df = census_dict['Total number of occupied private dwellings by tenure']

    elif year == 2006:
        df = census_dict['Total number of occupied private dwellings by housing tenure']

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 'Total number of dwellings',
                     'Owned', 'Rented']

        df = pd.read_csv('data/processed/nhs/Shelter costs.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total number of owner and tenant households with household total income greater than zero, in non-farm, non-reserve private dwellings by shelter-cost-to-income ratio',
                 '4_Number of owner households in non-farm, non-reserve private dwellings',
                 '11_Number of tenant households in non-farm, non-reserve private dwellings']].copy()

    elif year == 2016:
        df = census_dict['Total - Private households by tenure - 25% sample data']

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['shelter_tenure'] = df
    df.to_csv(file_path + '/shelter_tenure.csv')

    return census_dict

###############################################################################


def clean_education(census_dict, year, file_path):

    if year == 2001:
        col_names = ['LocalArea', 'Education',
                     'Visual and performing arts, and communications technologies',
                     'Humanities', 'Social and behavioural sciences and law',
                     'Business, management and public administration',
                     'Agriculture, natural resources and conservation',
                     'Engineering and applied sciences',
                     'Applied science technologies and trades',
                     'Health and related fields',
                     'Mathematics, computer and information sciences', 'No specialization',
                     'Total population with postsecondary qualifications',
                     'Total population 20 years and over',
                     'population 20 years and over - Less than grade 9',
                     'population 20 years and over - Grades 9 to 13',
                     'population 20 years and over - Without High school diploma or equivalent',
                     'population 20 years and over - High school diploma or equivalent',
                     'population 20 years and over - Apprenticeship or trades certificate or diploma',
                     'population 20 years and over - College',
                     'population 20 years and over - College without certificate or diploma',
                     'population 20 years and over - College, CEGEP or other non-university certificate or diploma',
                     'population 20 years and over - University',
                     'population 20 years and over - University without degree',
                     'population 20 years and over - University without certificate or diploma',
                     'population 20 years and over - University with certificate or diploma',
                     "population 20 years and over - University certificate, diploma or degree at bachelor level or above"]

        df1 = census_dict['Total population of females with postsecondary qualifications by major field of study']
        df2 = census_dict['Total population of males with postsecondary qualifications by major field of study']
        df3 = census_dict['Total population 20 years and over by highest level of schooling']
        df3 = df3.iloc[:, 1:20].copy()

        df4 = pd.concat([df1, df2])
        df4 = df4.groupby('LocalArea').sum()
        df4['Total population with postsecondary qualifications'] = df4['Total population of females with postsecondary qualifications by major field of study']+ df4['Total population of males with postsecondary qualifications by major field of study']
        df4.reset_index(inplace=True)
        df = pd.concat([df4, df3], axis=1)
        df.drop(columns=['Total population of females with postsecondary qualifications by major field of study',
                         'Total population of males with postsecondary qualifications by major field of study'], inplace=True)

    elif year == 2006:
        col_names = ['LocalArea', 'Total population aged 15 years and over',
                     'population aged 15 years and over - No certificate, diploma or degree', 
                     'population aged 15 years and over - Certificate, diploma or degree',
                     'population aged 15 years and over - High school certificate or equivalent',
                     'population aged 15 years and over - Apprenticeship or trades certificate or diploma',
                     'population aged 15 years and over - College, CEGEP or other non-university certificate or diploma',
                     'population aged 15 years and over - University certificate, diploma or degree',
                     'population aged 15 years and over - University certificate or diploma below bachelor level',
                     'population aged 15 years and over - University certificate or degree', "Bachelor's degree",
                     'population aged 15 years and over - University certificate or diploma above bachelor level',
                     'population aged 15 years and over - Degree in medicine, dentistry, veterinary medicine or optometry',
                     "population aged 15 years and over - Master's degree", 
                     'population aged 15 years and over - Earned doctorate',
                     'Total population 25 to 64 years with postsecondary qualifications',
                     'Education',
                     'Visual and performing arts, and communications technologies',
                     'Humanities', 'Social and behavioural sciences and law',
                     'Business, management and public administration',
                     'Physical and life sciences and technologies',
                     'Mathematics, computer and information sciences',
                     'Architecture, engineering, and related technologies',
                     'Agriculture, natural resources and conservation',
                     'Health, parks, recreation and fitness',
                     'Personal, protective and transportation services',
                     'Other fields of study']

        df1 = census_dict['Total male population 25 to 64 years with postsecondary qualifications by major field of study - Classification of Instructional Programs, 2000']
        df2 = census_dict['Total female population 25 to 64 years with postsecondary qualifications by major field of study - Classification of Instructional Programs, 2000']
        df = pd.concat([df1, df2])
        df = df.groupby('LocalArea').sum()
        df['Total population 25 to 64 years with postsecondary qualifications'] = df['Total male population 25 to 64 years with postsecondary qualifications by major field of study - Classification of Instructional Programs, 2000']+df['Total female population 25 to 64 years with postsecondary qualifications by major field of study - Classification of Instructional Programs, 2000']
        df.reset_index(inplace=True)

        df3 = census_dict['Total population 15 to 24 years by highest certificate, diploma or degree']
        df4 = census_dict['Total population 25 to 64 years by highest certificate, diploma or degree']
        df5 = pd.concat([df3, df4])
        df5 = df5.groupby('LocalArea').sum()
        df5['Total population 15 years and over'] = df5['Total population 15 to 24 years by highest certificate, diploma or degree'] + df5['Total population 25 to 64 years by highest certificate, diploma or degree']
        df5.reset_index(inplace=True)
        df5 = df5.iloc[:, 1:20].copy()

        df = pd.concat([df, df5], axis=1)
        df = df[['LocalArea', 'Total population 15 years and over',
                 'No certificate, diploma or degree',
                 'Certificate, diploma or degree',
                 'High school certificate or equivalent',
                 'Apprenticeship or trades certificate or diploma',
                 'College, CEGEP or other non-university certificate or diploma',
                 'University certificate, diploma or degree',
                 'University certificate or diploma below bachelor level',
                 'University certificate or degree', "Bachelor's degree",
                 'University certificate or diploma above bachelor level',
                 'Degree in medicine, dentistry, veterinary medicine or optometry',
                 "Master's degree", 'Earned doctorate',
                 'Total population 25 to 64 years with postsecondary qualifications',
                 'Education',
                 'Visual and performing arts, and communications technologies',
                 'Humanities', 'Social and behavioural sciences and law',
                 'Business, management and public administration',
                 'Physical and life sciences and technologies',
                 'Mathematics, computer and information sciences',
                 'Architecture, engineering, and related technologies',
                 'Agriculture, natural resources and conservation',
                 'Health, parks, recreation and fitness',
                 'Personal, protective and transportation services',
                 'Other fields of study']].copy()

    elif year == 2011:
        col_names = ['LocalArea', 'Type', 
                     'Total population aged 15 years and over',
                     'population aged 15 years and over - No certificate, diploma or degree',
                     'population aged 15 years and over - High school diploma or equivalent',
                     'population aged 15 years and over - Postsecondary certificate, diploma or degree',
                     'population aged 15 years and over - Apprenticeship or trades certificate or diploma',
                     'population aged 15 years and over - College, CEGEP or other non-university certificate or diploma',
                     'population aged 15 years and over - University certificate or diploma below bachelor level',
                     'population aged 15 years and over - University certificate, diploma or degree at bachelor level or above',
                     "population aged 15 years and over - Bachelor's degree",
                     'population aged 15 years and over - University certificate, diploma or degree above bachelor level',
                     'Total population aged 25 to 64 years',
                     'population aged 25 to 64 years - No certificate, diploma or degree',
                     'population aged 25 to 64 years - High school diploma or equivalent',
                     'population aged 25 to 64 years - Postsecondary certificate, diploma or degree',
                     'population aged 25 to 64 years - Apprenticeship or trades certificate or diploma',
                     'population aged 25 to 64 years - College, CEGEP or other non-university certificate or diploma',
                     'population aged 25 to 64 years - University certificate or diploma below bachelor level',
                     'population aged 25 to 64 years - University certificate, diploma or degree at bachelor level or above',
                     "population aged 25 to 64 years - Bachelor's degree",
                     'population aged 25 to 64 years - University certificate, diploma or degree above bachelor level',
                     'Education',
                     'Visual and performing arts, and communications technologies',
                     'Humanities', 'Social and behavioural sciences and law',
                     'Business, management and public administration',
                     'Physical and life sciences and technologies',
                     'Mathematics, computer and information sciences',
                     'Architecture, engineering, and related technologies',
                     'Agriculture, natural resources and conservation',
                     'Health and related fields',
                     'Personal, protective and transportation services',
                     'Other fields of study',
                     'population aged 15 years and over - No postsecondary certificate, diploma or degree',
                     'population aged 15 years and over - With postsecondary certificate, diploma or degree']

        df = pd.read_csv('data/processed/nhs/Education.csv', index_col=0)
        df = df[['LocalArea', 'Type',
                 '0_Total population aged 15 years and over by highest certificate, diploma or degree',
                 '1_No certificate, diploma or degree',
                 '2_High school diploma or equivalent',
                 '3_Postsecondary certificate, diploma or degree',
                 '4_Apprenticeship or trades certificate or diploma',
                 '5_College, CEGEP or other non-university certificate or diploma',
                 '6_University certificate or diploma below bachelor level',
                 '7_University certificate, diploma or degree at bachelor level or above',
                 "8_Bachelor's degree",
                 '9_University certificate, diploma or degree above bachelor level',
                 '10_Total population aged 25 to 64 years by highest certificate, diploma or degree',
                 '11_No certificate, diploma or degree',
                 '12_High school diploma or equivalent',
                 '13_Postsecondary certificate, diploma or degree',
                 '14_Apprenticeship or trades certificate or diploma',
                 '15_College, CEGEP or other non-university certificate or diploma',
                 '16_University certificate or diploma below bachelor level',
                 '17_University certificate, diploma or degree at bachelor level or above',
                 "18_Bachelor's degree",
                 '19_University certificate, diploma or degree above bachelor level',
                 '22_Education',
                 '23_Visual and performing arts, and communications technologies',
                 '24_Humanities', '25_Social and behavioural sciences and law',
                 '26_Business, management and public administration',
                 '27_Physical and life sciences and technologies',
                 '28_Mathematics, computer and information sciences',
                 '29_Architecture, engineering, and related technologies',
                 '30_Agriculture, natural resources and conservation',
                 '31_Health and related fields',
                 '32_Personal, protective and transportation services',
                 '33_Other fields of study',
                 '35_No postsecondary certificate, diploma or degree',
                 '36_With postsecondary certificate, diploma or degree']].copy()

    elif year == 2016:
        col_names = ['LocalArea', 'Total population aged 15 years and over',
                     'population aged 15 years and over - No certificate, diploma or degree',
                     'population aged 15 years and over - High school diploma or equivalent',
                     'population aged 15 years and over - Postsecondary certificate, diploma or degree',
                     'population aged 15 years and over - Apprenticeship or trades certificate or diploma',
                     'population aged 15 years and over - Trades certificate or diploma',
                     'population aged 15 years and over - Certificate of Apprenticeship or Certificate of Qualification',
                     'population aged 15 years and over - College, CEGEP or other non-university certificate or diploma',
                     'population aged 15 years and over - University certificate or diploma below bachelor level',
                     'population aged 15 years and over - University certificate, diploma or degree at bachelor level or above',
                     "population aged 15 years and over - Bachelor's degree",
                     'population aged 15 years and over - University certificate or diploma above bachelor level',
                     'population aged 15 years and over - Degree in medicine, dentistry, veterinary medicine or optometry',
                     "population aged 15 years and over - Master's degree", 
                     'population aged 15 years and over - Earned doctorate',
                     'population aged 15 years and over - No postsecondary certificate, diploma or degree', 
                     'Education',
                     'Visual and performing arts, and communications technologies',
                     'Humanities', 'Social and behavioural sciences and law',
                     'Business, management and public administration',
                     'Physical and life sciences and technologies',
                     'Mathematics, computer and information sciences',
                     'Architecture, engineering, and related technologies',
                     'Agriculture, natural resources and conservation',
                     'Personal, protective and transportation services',
                     'Other fields of study']

        df1 = census_dict['Total - Highest certificate, diploma or degree for the population aged 15 years and over in private households - 25% sample data']
        df2 = census_dict['Total - Major field of study - Classification of Instructional Programs (CIP) 2016 for the population aged 15 years and over in private households - 25% sample data']
        df2 = df2.iloc[:, 1:70].copy()

        df = pd.concat([df1, df2], axis=1)
        df = df[['LocalArea',
                 'Total - Highest certificate, diploma or degree for the population aged 15 years and over in private households - 25% sample data',
                 'No certificate, diploma or degree',
                 'Secondary (high) school diploma or equivalency certificate',
                 'Postsecondary certificate, diploma or degree',
                 'Apprenticeship or trades certificate or diploma',
                 'Trades certificate or diploma other than Certificate of Apprenticeship or Certificate of Qualification',
                 'Certificate of Apprenticeship or Certificate of Qualification',
                 'College, CEGEP or other non-university certificate or diploma',
                 'University certificate or diploma below bachelor level',
                 'University certificate, diploma or degree at bachelor level or above',
                 "Bachelor's degree",
                 'University certificate or diploma above bachelor level',
                 'Degree in medicine, dentistry, veterinary medicine or optometry',
                 "Master's degree", 'Earned doctorate',
                 'No postsecondary certificate, diploma or degree', 
                 'Education',
                 'Visual and performing arts, and communications technologies',
                 'Humanities', 'Social and behavioural sciences and law',
                 'Business, management and public administration',
                 'Physical and life sciences and technologies',
                 'Mathematics, computer and information sciences',
                 'Architecture, engineering, and related technologies',
                 'Agriculture, natural resources and conservation',
                 'Personal, protective and transportation services',
                 'Other']].copy()

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['education'] = df
    df.to_csv(file_path + '/education.csv')

    return census_dict

###############################################################################


def clean_household_type(census_dict, year, file_path):

    col_names = ['LocalArea', 
                 'Total number of private households by household type', 
                 'One-family households', 'Multiple-family households', 
                 'Non-family households']

    if year == 2001:
        df = census_dict['Total number of private households by household type']
        df = df[col_names]

    elif year == 2006:
        df = census_dict['Total number of private households by household type']
        df = df[col_names]

    elif year == 2011:
        col_names = ['LocalArea', 
                     'Total number of private households by household type', 
                     'One-family only households', 'Couple family households', 
                     'Other family households']

        df = census_dict['Total number of private households by household type']
        df = df.iloc[:, 0:9]
        df = df[col_names]

    elif year == 2016:
        col_names = ['LocalArea', 
                     'Total - Private households by household type - 100% data', 
                     'One-census-family households',
                     'Multiple-census-family households', 
                     'Non-census-family households']
        df = census_dict['Total - Private households by household type - 100% data']
        df = df[col_names]

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['household_type'] = df
    df.to_csv(file_path + '/household_type.csv')

    return census_dict

###############################################################################


def clean_citizenship(census_dict, year, file_path):

    col_names = ['LocalArea', 'Canadian citizens', 'Not Canadian citizens']

    if year == 2001:
        col_names = ['LocalArea', 'Canadian Citizenship', 
                     'Citizenship other than Canadian']
        df = census_dict['Total population by citizenship']
        df = df[col_names]

    elif year == 2006:
        df = census_dict['Total population by citizenship']
        df = df[col_names]

    elif year == 2011:
        df = pd.read_csv('data/processed/nhs/Citizenship.csv', index_col=0)
        df = df[['LocalArea', '1_Canadian citizens', 
                 '4_Not Canadian citizens']]

    elif year == 2016:
        df = census_dict['Total - Citizenship for the population in private households - 25% sample data']
        df = df[col_names]

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['citizenship'] = df
    df.to_csv(file_path + '/citizenship.csv')

    return census_dict

###############################################################################


def clean_worker_class(census_dict, year, file_path):

    col_names = ['LocalArea', 'Type', 
                 'Total labour force aged 15 years and over',
                 'Class of worker - not applicable',
                 'All classes of worker']

    if year == 2001:
        df1 = census_dict['Total labour force 15 years and over  by class of worker']
        df2 = census_dict['Males labour force 15 years and over  by class of worker']
        df3 = census_dict['Females labour force 15 years and over  by class of worker']

        df1 = df1[['LocalArea',
                   'Total labour force 15 years and over  by class of worker',
                   'Class of worker - Not applicable', 
                   'All classes of worker']].copy()
        df1.insert(1, 'Type', 'total')
        df1.set_axis(col_names, axis=1, inplace=True)

        df2 = df2[['LocalArea', 
                   'Males labour force 15 years and over  by class of worker',
                   'Class of worker - Not applicable', 
                   'All classes of worker']].copy()
        df2.insert(1, 'Type', 'male')
        df2.set_axis(col_names, axis=1, inplace=True)

        df3 = df3[['LocalArea',
                   'Females labour force 15 years and over  by class of worker',
                   'Class of worker - Not applicable',
                   'All classes of worker']].copy()
        df3.insert(1, 'Type', 'female')
        df3.set_axis(col_names, axis=1, inplace=True)
        merged = pd.concat([df1,df2,df3])

    elif year == 2006:
        df1 = census_dict['Total labour force 15 years and over by class of worker']
        df2 = census_dict['Male labour force 15 years and over - class of worker']
        df3 = census_dict['Female labour force 15 years and over - class of worker']

        df1 = df1[['LocalArea', 
                   'Total labour force 15 years and over by class of worker',
                   'Class of worker - Not applicable',
                   'All classes of worker']].copy()
        df1.insert(1, 'Type', 'total')
        df1.set_axis(col_names, axis=1, inplace=True)
        df2 = df2[['LocalArea', 
                   'Male labour force 15 years and over - class of worker',
                   'Class of worker - Not applicable',
                   'All classes of worker']].copy()
        df2.insert(1, 'Type', 'male')
        df2.set_axis(col_names, axis=1, inplace=True)

        df3 = df3[['LocalArea', 
                   'Female labour force 15 years and over - class of worker',
                   'Class of worker - Not applicable',
                   'All classes of worker']].copy()
        df3.insert(1, 'Type', 'female')
        df3.set_axis(col_names, axis=1, inplace=True)
        merged = pd.concat([df1,df2,df3])

    elif year == 2011:
        df = pd.read_csv('data/processed/nhs/Class of worker.csv', index_col=0)
        merged = df[['LocalArea', 'Type',
                 '0_Total labour force aged 15 years and over by class of worker',
                 '1_Class of worker - not applicable',
                 '2_All classes of worker']].copy()
        merged.set_axis(col_names, axis=1, inplace=True)

    elif year == 2016:
        df1 = census_dict['Total labour force aged 15 years and over by class of worker - 25% sample data']
        df1 = df1.iloc[:,0:4].copy()
        df1.insert(1, 'Type', 'total')
        df1.set_axis(col_names, axis=1, inplace=True)

        df2 = census_dict['Total male labour force aged 15 years and over by class of worker - 25% sample data']
        df2 = df2.iloc[:,0:4].copy()
        df2.insert(1, 'Type', 'male')
        df2.set_axis(col_names, axis=1, inplace=True)

        df3 = census_dict['Total female labour force aged 15 years and over by class of worker - 25% sample data']
        df3 = df3.iloc[:,0:4].copy()
        df3.insert(1, 'Type', 'female')
        df3.set_axis(col_names, axis=1, inplace=True)
        merged = pd.concat([df1,df2,df3])

    merged.sort_values(by=['LocalArea','Type'], inplace=True)
    census_dict['worker_class'] = merged
    merged.to_csv(file_path + '/worker_class.csv')
    
    return census_dict

###############################################################################


def clean_time_worked(census_dict, year, file_path):

    col_names = ['LocalArea', 'Type',
                 'Population 15 years and over by work activity',
                 'full time', 'part time']

    if year == 2001:
        df1 = census_dict['Total population 15 years and over with employment income, by sex and work activity']
        df1 = df1[['LocalArea',
                   'Total population 15 years and over with employment income, by sex and work activity',
                   'Worked full year, full time',
                   'Worked part year or part time']].copy()
        df1.insert(1, 'Type', 'Total')
        df1.set_axis(col_names, axis=1, inplace=True)
        df1['Worked partially full time and partially part time'] = df1['Population 15 years and over by work activity'] - df1['full time']-df1['part time']

        df2 = census_dict['Males 15 years and over with employment income by work activity']
        df2 = df2[['LocalArea',
                   'Males 15 years and over with employment income by work activity',
                   'Worked full year, full time',
                   'Worked part year or part time']].copy()
        df2.insert(1, 'Type', 'male')
        df2.set_axis(col_names, axis=1, inplace=True)
        df2['Worked partially full time and partially part time'] = df2['Population 15 years and over by work activity'] - df2['full time']-df2['part time']

        df3 = census_dict['Females 15 years and over with employment income by work activity']
        df3 = df3[['LocalArea',
                   'Females 15 years and over with employment income by work activity',
                   'Worked full year, full time',
                   'Worked part year or part time']].copy()
        df3.insert(1, 'Type', 'female')
        df3.set_axis(col_names, axis=1, inplace=True)
        df3['Worked partially full time and partially part time'] = df3['Population 15 years and over by work activity'] - df3['full time']-df3['part time']

        merged = pd.concat([df1,df2,df3])

    elif year == 2006:
        col_names = ['LocalArea',
                     'Population 15 years and over by work activity',
                     'full time', 'part time']

        # Females
        df1 = census_dict['Females 15 years and over with employment income']
        df1 = df1[['LocalArea',
                   'Females 15 years and over with employment income',
                   'Worked full year, full time',
                   'Worked part year or part time']].copy()
        df1.set_axis(col_names, axis=1, inplace=True)

        # Males
        df2 = census_dict['Males 15 years and over with employment income']
        df2 = df2[['LocalArea',
                   'Males 15 years and over with employment income',
                   'Worked full year, full time',
                   'Worked part year or part time']].copy()
        df2.set_axis(col_names, axis=1, inplace=True)

        # Calculate total
        df3 = pd.merge(df1, df2, on='LocalArea')
        df3 = df3.groupby(df3.columns, axis=1).sum()
        df3['Population 15 years and over by work activity'] = df3['Population 15 years and over by work activity_x'] + df3['Population 15 years and over by work activity_x']
        df3['full time'] = df3['full time_x'] + df3['full time_y']
        df3['part time' ]= df3['part time_x'] + df3['part time_y']
        df3 = df3[['LocalArea',
                   'Population 15 years and over by work activity',
                   'full time', 'part time']].copy()
        df1.insert(1, 'Type', 'female')
        df2.insert(1, 'Type', 'male')
        df3.insert(1, 'Type', 'Total')
        merged = pd.concat([df3, df2, df1])
        merged['Worked partially full time and partially part time'] = merged['Population 15 years and over by work activity'] - merged['full time'] - merged['part time']
    
    elif year == 2011:
        col_names = ['LocalArea', 'Type', 
                     'Population 15 years and over by work activity',
                     'full time', 'part time']

        df1 = pd.read_csv('data/processed/nhs/Full-time or part-time weeks worked.csv', index_col=0)
        df1 = df1.iloc[:,[-1,0,1,4,5]].copy()

        df1.columns = col_names  
        merged = df1

    elif year == 2016:
        col_names = ['LocalArea',
                     'Population 15 years and over by work activity',
                     'full time', 'part time', 
                     'Worked partially full time and partially part time']
        df1 = census_dict['Total population aged 15 years and over by work activity during the reference year - 25% sample data']
        df2 = census_dict['Males aged 15 years and over by work activity during the reference year - 25% sample data']
        df3 = census_dict['Females aged 15 years and over by work activity during the reference year - 25% sample data']
        
        # Total
        df1['Worked partially full time and partially part time'] = df1['Total population aged 15 years and over by work activity during the reference year - 25% sample data']-df1['Did not work']-df1['Worked']
        df1.drop(['Did not work', 'Worked'], axis=1, inplace=True)
        df1 = df1[['LocalArea',
                   'Total population aged 15 years and over by work activity during the reference year - 25% sample data',
                   'Worked full year, full time',
                   'Worked part year and/or part time',
                   'Worked partially full time and partially part time']].copy()
        df1.set_axis(col_names, axis=1, inplace=True)
        df1.insert(1, 'Type', 'Total')

        # Male
        df2['Worked partially full time and partially part time'] = df2['Males aged 15 years and over by work activity during the reference year - 25% sample data']-df2['Did not work']-df2['Worked']
        df2.drop(['Did not work', 'Worked'], axis=1, inplace=True)
        df2 = df2[['LocalArea',
                   'Males aged 15 years and over by work activity during the reference year - 25% sample data',
                   'Worked full year, full time',
                   'Worked part year and/or part time',
                   'Worked partially full time and partially part time']].copy()
        df2.set_axis(col_names, axis=1, inplace=True)
        df2.insert(1, 'Type', 'male')

        # Female
        df3['Worked partially full time and partially part time'] = df3['Females aged 15 years and over by work activity during the reference year - 25% sample data']-df3['Did not work']-df3['Worked']
        df3.drop(['Did not work', 'Worked'], axis=1, inplace=True)
        df3 = df3[['LocalArea',
                   'Females aged 15 years and over by work activity during the reference year - 25% sample data',
                   'Worked full year, full time',
                   'Worked part year and/or part time',
                   'Worked partially full time and partially part time']].copy()
        df3.set_axis(col_names, axis=1, inplace=True)
        df3.insert(1, 'Type', 'female')
        merged = pd.concat([df3, df2, df1])

    merged.sort_values(by=['LocalArea', 'Type'], inplace=True)
    census_dict['time_worked'] = merged
    merged.to_csv(file_path + '/time_worked.csv')
    return census_dict

###############################################################################


def clean_generation_status(census_dict, year, file_path):

    col_names = ['LocalArea', 'Total Population 15 years and older',
                '1st generation','2nd generation', '3rd generation and over']

    if year == 2001:
        df = census_dict['Total population 15 years and over by generation status']
        df = df.iloc[:, 0:5].copy()
        df.set_axis(col_names, axis=1, inplace=True)

    elif year == 2006:
        df = census_dict['Total population 15 years and older by generation status']
        df = df.iloc[:, 0:5].copy()
        df.set_axis(col_names, axis=1, inplace=True)

    elif year == 2011:
        df = pd.read_csv('data/processed/nhs/Generation status.csv', index_col=0)
        df = df.loc[df['Type'] == 'Total'].copy().reset_index()
        df.drop(['Type', 'index'], axis=1, inplace=True)

        df = df[['LocalArea',
                 '0_Total population in private households by generation status', 
                 '1_First generation', '2_Second generation',
                 '3_Third generation or more']]
        df.set_axis(col_names, axis=1, inplace=True)

    elif year == 2016:
        df = census_dict['Total - Generation status for the population in private households - 25% sample data']
        df = df.iloc[:, 0:5].copy()
        df.set_axis(col_names, axis=1, inplace=True)

    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['generation_status'] = df
    df.to_csv(file_path + '/generation_status.csv')

    return census_dict

###############################################################################


def clean_industry(census_dict, year, file_path):

    if year == 2011:
        df = pd.read_csv('data/processed/nhs/Industry.csv', index_col=0
                        ).query('Type == "Total"'
                               ).drop(columns='Type')
        df = df.rename(columns={
                       '0_Total labour force population aged 15 years and over by industry - North American Industry Classification System (NAICS) 2007': 'total'})

        meta = ['LocalArea', '2_All industries',
                '1_Industry - not applicable', 'total']

    else:
        if year == 2001:
            df = census_dict[
                'Total labour force 15 years and over by industry - 1997 North American Industry Classification System']
            df = df.rename(columns={
                           'Total labour force 15 years and over by industry - 1997 North American Industry Classification System': 'total'})
            meta = ['LocalArea',
                    'All industries',
                    'Industry - Not applicable',
                    'total']

        elif year == 2006:
            df = census_dict[
                'Total labour force 15 years and over by industry - North American Industry Classification System 2002']
            df = df.rename(columns={
                           'Total labour force 15 years and over by industry - North American Industry Classification System 2002': 'total'})
            meta = ['LocalArea',
                    'All industries',
                    'Industry - Not applicable',
                    'total']
        else:
            df = census_dict[
                'Total Labour Force population aged 15 years and over by Industry - North American Industry Classification System (NAICS) 2012 - 25% sample data']
            df = df.rename(columns={
                           'Total Labour Force population aged 15 years and over by Industry - North American Industry Classification System (NAICS) 2012 - 25% sample data': 'total'})
            meta = ['LocalArea',
                    'All industry categories',
                    'Industry - NAICS2012 - not applicable',
                    'total']

    meta_df = df[meta]
    industries_df = df.drop(columns=meta)
    industries = industries_df.columns
    industries = [re.findall(r'^[0-9 -_]* (.*)', i)[0] for i in industries]
    industries_df.columns = industries
    industries_df = industries_df.loc[:, sorted(industries)]

    column_names = ['LocalArea',
                    'All industries',
                    'Industry - Not applicable',
                    'total',
                    'Accommodation and food services',
                    'Administrative and support, waste management and remediation services',
                    'Agriculture, forestry, fishing and hunting',
                    'Arts, entertainment and recreation', 'Construction',
                    'Educational services', 'Finance and insurance',
                    'Health care and social assistance',
                    'Information and cultural industries',
                    'Management of companies and enterprises', 'Manufacturing',
                    'Mining, quarrying, and oil and gas extraction',
                    'Other services (except public administration)',
                    'Professional, scientific and technical services',
                    'Public administration', 'Real estate and rental and leasing',
                    'Retail trade', 'Transportation and warehousing', 'Utilities',
                    'Wholesale trade']

    df = pd.concat([meta_df, industries_df], axis=1)

    df.set_axis(column_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['industry'] = df
    df.to_csv(file_path + '/industry.csv')

    return census_dict

###############################################################################


def clean_labour_force_status(census_dict, year, file_path):

    col_names = ['LocalArea', 'Type', 'Employed', 'Employment rate', 
                 'In the labour force', 'Not in the labour force', 
                 'Participation rate', 'Unemployed', 'Unemployment rate']

    if year == 2011:
        df = pd.read_csv('data/processed/nhs/Labour force status.csv', index_col=0)
        df = df[['LocalArea', 'Type', '2_Employed', '6_Employment rate', 
                 '1_In the labour force', '4_Not in the labour force',
                 '5_Participation rate', '3_Unemployed', 
                 '7_Unemployment rate']].copy()

    else:
        order = [0, 3, 7, 2, 5, 6, 4, 8]
        if year == 2001:
            total = census_dict['Population - 15 years and over by labour force activity'].iloc[:, order]
            male = census_dict['Total - Males 15 years and over'].iloc[:, order]
            female = census_dict['Total - Females 15 years and over'].iloc[:, order]

        elif year == 2006:
            total = census_dict['Total population 15 years and over by labour force activity'].iloc[:, order]
            male = census_dict['Males 15 years and over - Labour force activity'].iloc[:, order]
            female = census_dict['Females 15 years and over - Labour force activity'].iloc[:, order]

        else:
            total = census_dict['Total - Population aged 15 years and over by Labour force status - 25% sample data'].iloc[:, order]
            male = census_dict['Total - Males aged 15 years and over by Labour force status - 25% sample data'].iloc[:, order]
            female = census_dict['Total - Females aged 15 years and over by Labour force status - 25% sample data'].iloc[:, order]

        total.insert(1, 'Type', 'Total')
        total.columns = col_names
        male.insert(1, 'Type', 'Male')
        male.columns = col_names
        female.insert(1, 'Type', 'Female')
        female.columns = col_names

        df = pd.concat([total, male, female])

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['labour_force_status'] = df
    df.to_csv(file_path + '/labour_force_status.csv')

    return census_dict

###############################################################################


def clean_mobility(census_dict, year, file_path):

    column_names = ['LocalArea', 
                    'Non-movers 1 yr ago',
                    'Non-migrants 1 yr ago', 
                    'Migrants 1 yr ago']

    if year == 2011:
        df = pd.read_csv(
            'data/processed/nhs/Mobility.csv', index_col=0
        ).query('Type == "Total"').iloc[:, [-1, 1, 3, 4]]

    else:
        if year == 2001:
            df = census_dict[
                'Total population 1 year and over by mobility status 1 year ago']
        elif year == 2006:
            df = census_dict[
                'Total - Mobility status 1 year ago']
        else:
            df = census_dict[
                'Total - Mobility status 1 year ago - 25% sample data']
        df = df.iloc[:, [0, 2, 4, 5]]

    df.set_axis(column_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['mobility'] = df
    df.to_csv(file_path + '/mobility.csv')

    return census_dict

###############################################################################


def clean_transport_mode(census_dict, year, file_path):

    column_names = ['LocalArea', 'Type', 'Total',
                    'car as driver', 'car as passenger', 
                    'public transportation', 'walked',
                    'bicycle', 'other transportation']

    if year == 2011:
        df = pd.read_csv('data/processed/nhs/Mode of transportation.csv',
                         index_col=0).iloc[:, [-1, 0, 1, 2, 3, 4, 5, 6, 7]]

    else:
        if year == 2016:
            male = census_dict['Total - Main mode of commuting for the male employed labour force aged 15 years and over in private households with a usual place of work or no fixed workplace address - 25% sample data']
            female = census_dict['Total - Main mode of commuting for the female employed labour force aged 15 years and over in private households with a usual place of work or no fixed workplace address - 25% sample data']

            male.insert(1, 'Type', 'Male')
            female.insert(1, 'Type', 'Female')
        else:
            if year == 2001:
                male = census_dict['Males with a usual place of work or no fixed workplace address']
            else:
                male = census_dict['Males with usual place of work or no fixed workplace address']
            female = census_dict['Females with usual place of work or no fixed workplace address']
                
            male.insert(1, 'Type', 'Male')
            male['Other method'] = male[
                'Other method'] + male[
                'Taxicab'] + male[
                'Motorcycle']
            male.drop(columns=[
                'Taxicab', 'Motorcycle'], inplace=True)

            female.insert(1, 'Type', 'Female')
            female['Other method'] = female[
                'Other method'] + female[
                'Taxicab'] + female[
                'Motorcycle']
            female.drop(columns=['Taxicab', 
                                 'Motorcycle'], inplace=True)
        
        male.columns = column_names
        female.columns = column_names
        
        df = pd.concat([male, female])

        total = df.groupby(['LocalArea']).sum().reset_index()
        total['Type'] = ['Total']*len(total)

        df = pd.concat([df, total])
    df.set_axis(column_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['transport_mode'] = df
    df.to_csv(file_path + '/transport_mode.csv')

    return census_dict

###############################################################################

def clean_occupation(census_dict, year, file_path):

    col_names = ['LocalArea', 'Type', 'All occupations', 'Occupations n/a',
                 'Management', 'Business and finance', 
                 'Natural and applied sciences', 'Health', 
                 'Social Science and education', 'Art', 'Sales and service',
                'Trades and transport', 'Natural resources and agriculture',
                'Manufacturing and utilities']

    if year in [2001, 2006]:
        if year == 2001:
            female = census_dict['Female labour force 15 years and over - Occupation']
            male = census_dict['Male labour force 15 years and over - Occupation']
        
        else:
            female = census_dict['Female labour force 15 years and over by occupation - National Occupational Classification for Statistics 2006']
            male = census_dict['Male labour force 15 years and over by occupation - National Occupational Classification for Statistics 2006']

        occupations = [i for i in female.columns if re.match(r'^[A-Z] ', i)]
        female['Type'] = ['Female'] * len(female)
        female = pd.concat(
            [female.iloc[:, [0, -1, 3, 2]], female.loc[:, occupations]], axis=1)
        female.columns = col_names

        male['Type'] = ['Male'] * len(male)
        male = pd.concat(
            [male.iloc[:, [0, -1, 3, 2]], male.loc[:, occupations]], axis=1)
        male.columns = col_names

        df = pd.concat([female, male])

        total = df.groupby(['LocalArea']).sum().reset_index()
        total['Type'] = ['Total'] * len(total)

        df = pd.concat([df, total])

    elif year == 2011:
        df = pd.read_csv(
            'data/processed/nhs/Occupation.csv', index_col=0
        ).iloc[:, [14, 0, 6, 5, 7, 8, 9, 10, 11, 12, 13, 2, 3, 4]]

    elif year == 2016:
        total = census_dict['Total labour force population aged 15 years and over by occupation - National Occupational Classification (NOC) 2016 - 25% sample data']
        female = census_dict['Total female labour force population aged 15 years and over by occupation - National Occupational Classification (NOC) 2016 - 25% sample data']
        male = census_dict['Total male labour force population aged 15 years and over by occupation - National Occupational Classification (NOC) 2016 - 25% sample data']

        male['Type'] = ['Male'] * len(male)
        total['Type'] = ['Total'] * len(total)
        female['Type'] = ['Female'] * len(female)

        total = pd.concat(
            (total.iloc[:, [0, -1, 3, 2]], total.iloc[:, 4:14]), axis=1)
        female = pd.concat(
            (female.iloc[:, [0, -1, 3, 2]], female.iloc[:, 4:14]), axis=1)
        male = pd.concat(
            (male.iloc[:, [0, -1, 3, 2]], male.iloc[:, 4:14]), axis=1)
        
        female.columns, male.columns, total.columns = col_names, col_names, col_names

        df = pd.concat([total, female, male])

    df.set_axis(col_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['occupation'] = df
    df.to_csv(file_path + '/occupation.csv')

    return census_dict

###############################################################################


def clean_workplace_status(census_dict, year, file_path):

    column_names = ['LocalArea', 'Type',
                    'Worked at home',
                    'Worked at usual place',
                    'Worked outside Canada',
                    'No fixed workplace']

    if year == 2011:

        df = pd.read_csv('data/processed/nhs/Place of work status.csv',
                         index_col=0).iloc[:, [-1, 0, 2, 5, 3, 4]]

    else:
        if year == 2001 or year == 2006:
            order = [0, -3, 2, -2, -1]
            male = census_dict['Males'].iloc[:, order]
            female = census_dict['Females'].iloc[:, order]
        else:
            order = [0, 2, -1, 3, 4]
            male = census_dict[
                'Total - Place of work status for the male employed labour force aged 15 years and over in private households - 25% sample data'].iloc[:, order]
            female = census_dict['Total - Place of work status for the female employed labour force aged 15 years and over in private households - 25% sample data'].iloc[:, order]

        male.insert(1, 'Type', 'Male')
        female.insert(1, 'Type', 'Female')

        male.columns = column_names
        female.columns = column_names

        df = pd.concat([female, male])

        total = df.groupby(['LocalArea']).sum().reset_index()
        total['Type'] = ['Total'] * len(total)

        df = pd.concat([df, total])

    df.set_axis(column_names, axis=1, inplace=True)
    df.sort_values(by=['LocalArea'], inplace=True)
    census_dict['workplace_status'] = df
    df.to_csv(file_path + '/workplace_status.csv')

    return census_dict

###############################################################################
# MAIN FUNCTION
###############################################################################


def main(census_file, year, file_path):

    col_names = ['Variable', 'Arbutus-Ridge', 'Downtown',
                 'Dunbar-Southlands', 'Fairview', 'Grandview-Woodland',
                 'Hastings-Sunrise', 'Kensington-Cedar Cottage',
                 'Kerrisdale', 'Killarney', 'Kitsilano', 'Marpole',
                 'Mount Pleasant', 'Oakridge', 'Renfrew-Collingwood',
                 'Riley Park', 'Shaughnessy', 'South Cambie', 'Strathcona',
                 'Sunset', 'Victoria-Fraserview', 'West End',
                 'West Point Grey', 'Vancouver CSD', 'Vancouver CMA']
    year = int(year)

    # read in csv file as dataframe
    df = pd.read_csv(census_file, encoding='latin-1', skiprows=4)

    # remove 'ID' column if present
    df.drop(columns='ID', inplace=True, errors='ignore')

    # rename columns
    df.set_axis(col_names, axis=1, inplace=True)

    # remove empty rows
    df.dropna(0, 'all', inplace=True)

    # remove whitespace from variables
    df.Variable = df.Variable.apply(lambda x: (x.lstrip()).rstrip())
    df.drop(df[df.Variable.str.contains('20%.*data', flags=re.IGNORECASE)].index, inplace=True)

    # convert numeric data to float type
    df.iloc[:, 1:25] = df.iloc[:, 1:25].applymap(lambda x: str(x) if x == x else x)
    df.iloc[:, 1:25] = df.iloc[:, 1:25].applymap(lambda x: re.sub("[-]", "0", x) if x == x else x)
    df.iloc[:, 1:25] = df.iloc[:, 1:25].applymap(lambda x: float(re.sub("[,$]", "", x)) if x == x else x)

    # Create the census subdirectory for given year if it doesn't exist
    os.makedirs(file_path, exist_ok=True)

    # divide the census datasets into subgroups
    census_dict = create_subgroup_dict(df, year)

    # clean the datatables by topics
    helper_func = [clean_age, clean_marital_status,
                   clean_couple_fam_structure, clean_language_detailed,
                   clean_official_language, clean_structural_dwelling_type,
                   clean_household_size, clean_lone_parent,
                   clean_immigration_age, clean_immigration_period,
                   clean_birth_place, clean_shelter_tenure,
                   clean_visible_minority, clean_education,
                   clean_household_type, clean_citizenship,
                   clean_worker_class, clean_time_worked,
                   clean_generation_status, clean_industry,
                   clean_labour_force_status, clean_mobility,
                   clean_transport_mode, clean_occupation,
                   clean_workplace_status]

    for func in helper_func:
        census_dict = func(census_dict, year, file_path)

if __name__ == "__main__":
    main(opt["--census_file"], opt["--year"], opt["--file_path"])
