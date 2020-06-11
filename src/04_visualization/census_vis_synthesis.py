# author: Keanna Knebel
# date: 2020-06-05

"""
This script performs data wrangling and synthesis to combine the census
data .csv files across all census years. The output of the script is a
single csv file containing all census data. The script takes the path to
the census data directory, the local area boundary file, and the path
to the exported csv file, as inputs.

Usage: src/04_visualization/census_vis_synthesis.py --path_in=<path_in> \
--path_out=<path_out> \
--area_file=<area_file>

Options:

--path_in=<path_in>                 Path to the directory containing the census
                                    subfolders of .csv files.
--path_out=<path_out>               Path to the exported file.
--area_file=<area_file>             Path to the geojson file containing the
                                    neighborhood boundaries data.
"""

from docopt import docopt
import pandas as pd
import geopandas as gpd
import os

opt = docopt(__doc__)


def main(path_in, path_out, area_file):

    ###########################################################################
    #  HELPER CLEANING FUNCTIONS
    ###########################################################################

    # suppress warning
    pd.options.mode.chained_assignment = None

    def clean_couples_family_structure(family, year):
        """
        This function cleans the family census data
        Args:
            family (pd.DataFrame): The dataframe for family data
            year (int): census year

        Returns:
            family: A cleaned pandas dataframe
        """

        family = family[family['Type'] == 'total couples']
        van_total = family.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'total couples'
        family = family.append(van_total, ignore_index=True)

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

        return family

    def clean_detailed_language(language, year):
        """
        This function cleans the language census data
        Args:
            language (pd.DataFrame): The dataframe for language data
            year (int) : Census year

        Returns:
            language: A cleaned pandas dataframe
        """

        # only keeping their mother tongue
        language = language[language['Type'] == 'mother tongue - total']

        van_total = language.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'mother tongue - total'
        language = language.append(van_total, ignore_index=True)

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

        return language

    def clean_marital_status(marital, year):
        """
        This function cleans the marital census data
        Args:
            marital (pd.DataFrame): The dataframe for language data
            year (int) : Census year

        Returns:
            marital: A cleaned pandas dataframe
        """

        marital['Married or living with a or common-law partner'] = marital[
                'Married or living with a or common-law partner'] / marital[
                'Total population 15 years and over']

        marital[
            'Not living with a married spouse or common-law partner'] = marital[
            'Not living with a married spouse or common-law partner']/marital[
            'Total population 15 years and over']

        if year == 2011 or year == 2016:
            marital = marital.query('Type == "total"')
            van_total = marital.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Type'] = 'total'
            marital = marital.append(van_total, ignore_index=True)

        marital = marital[[
            'LocalArea',
            'Married or living with a or common-law partner',
            'Not living with a married spouse or common-law partner']]

        return marital

    def clean_population_age_sex(age, year):
        """
        This function cleans the population age census data
        Args:
            age (pd.DataFrame): The dataframe for population data
            year (int) : Census year

        Returns:
            age: A cleaned pandas dataframe
        """
        age = age[age['Type'] == 'total']
        van_total = age.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'total'
        age = age.append(van_total, ignore_index=True)

        age['Under 20'] = (age[
            '0 to 4 years'] + age[
            '5 to 9 years'] + age[
            '10 to 14 years'] + age[
            '15 to 19 years'])

        age['20 to 34'] = (age[
            '20 to 24 years'] + age[
            '25 to 29 years'] + age[
            '30 to 34 years'])

        age['35 to 44'] = (age[
            '35 to 39 years'] + age[
            '40 to 44 years'])

        age['45 to 54'] = (age[
            '45 to 49 years'] + age[
            '50 to 54 years'])

        age['55 to 64'] = (age[
            '55 to 59 years'] + age[
            '60 to 64 years'])

        age['65 to 79'] = (age[
            '65 to 69 years'] + age[
            '70 to 74 years'] + age[
            '75 to 79 years'])

        if year in [2001, 2006]:

            age['80 and Older'] = (age[
                '80 to 84 years'] + age[
                '85 to 89 years'] + age[
                '90 to 94 years'] + age[
                '95 to 99 years'] + age[
                '100 years and over'])

        elif year in [2011, 2016]:

            age['80 and Older'] = (age[
                '80 to 84 years'] + age[
                '85 years and over'])

        age = age[['LocalArea', 'Under 20',
                   '20 to 34',
                   '35 to 44',
                   '45 to 54',
                   '55 to 64',
                   '65 to 79',
                   '80 and Older']]

        return age

    def clean_gender(gender, year):
        """
        This function cleans the population gender census data
        Args:
            gender (pd.DataFrame): The dataframe for gender data
            year (int): census year

        Returns:
            gender: A cleaned pandas dataframe
        """

        gender = gender.iloc[:, 1:4].pivot(
            index='LocalArea', columns='Type', values='Total'
            ).reset_index()

        gender['female'] = gender['female'] / gender['total']
        gender['male'] = gender['male'] / gender['total']

        gender = gender[['LocalArea',
                         'female',
                         'male']]

        return gender

    def clean_visible_minority(mino, year):
        """
        This function cleans the visible minority census data
        Args:
            mino (pd.DataFrame): The dataframe for visible minority data
            year (int): census year

        Returns:
            mino: A cleaned pandas dataframe
        """

        if year == 2011:
            mino = mino[mino.Type == 'Total']
            van_total = mino.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Type'] = 'Total'
            mino = mino.append(van_total, ignore_index=True)

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

        return mino

    def clean_structural_dwelling_type(dwel, year):
        """
        This function cleans the dwelling type census data
        Args:
            dwel (pd.DataFrame): The dataframe for dwelling type data
            year (int): census year

        Returns:
            dwel: A cleaned pandas dataframe
        """

        dwel['dwelling_House'] = (dwel['Single-detached house'] +
                                  dwel['Semi-detached house'] +
                                  dwel['Row house']) / dwel['Total']

        if year == 2001:
            dwel['dwelling_Apartment'] = (dwel[
                    'Apartment, detached duplex'] + dwel[
                    'Apartment, building that has five or more storeys'] + dwel[
                    'Apartment, building that has fewer than five storeys'
                    ]) / dwel['Total']

            dwel['dwelling_Other'] = (
                dwel['Other single-attached house'] + dwel[
                    'Movable dwelling']) / dwel['Total']

        elif year == 2006:
            dwel['dwelling_Apartment'] = (dwel[
                 'Apartment, duplex'] + dwel[
                 'Apartment, building that has five or more storeys'
                ])/dwel['Total']

            dwel['dwelling_Other'] = 1 - dwel[
                'dwelling_Apartment'] - dwel[
                'dwelling_House']

        else:
            dwel['dwelling_Apartment'] = (dwel[
                 'Apartment, detached duplex'] + dwel[
                 'Apartment, building that has five or more storeys'] + dwel[
                 'Apartment, building that has fewer than five storeys'
                ]) / dwel['Total']

            dwel['dwelling_Other'] = 1 - dwel[
                    'dwelling_Apartment'] - dwel[
                    'dwelling_House']

        dwel = dwel[['LocalArea',
                     'dwelling_House',
                     'dwelling_Apartment',
                     'dwelling_Other']]

        return dwel

    def clean_shelter_tenure(shel, year):
        """
        This function cleans the shelter tenure census data
        Args:
            shel (pd.DataFrame): The dataframe for shelter tenure data
            year (int): census year

        Returns:
            shel: A cleaned pandas dataframe
        """

        if year == 2011:
            shel = shel.query('Type == "Total"')
            van_total = shel.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Type'] = 'Total'
            shel = shel.append(van_total, ignore_index=True)

        shel['Owned_Rented'] = shel['Owned'] + shel['Rented']
        shel['Owned shelter'] = shel['Owned'] / shel['Owned_Rented']
        shel['Rented shelter'] = shel['Rented'] / shel['Owned_Rented']

        shel = shel[['LocalArea', 'Owned shelter', 'Rented shelter']]

        return shel

    def clean_lone_parent(lone, year):
        lone['Female lone parent'] = lone[
             'Female parent'] / lone[
             'Total lone-parent families']
        lone['Male lone parent'] = lone[
             'Male parent'] / lone[
             'Total lone-parent families']

        lone = lone[['LocalArea', 'Female lone parent', 'Male lone parent']]
        return lone

    def clean_immigration_period(im_p, year):
        """
        This function cleans the immigration period census data
        Args:
            im_p (pd.DataFrame): The dataframe for immigration period data
            year (int): census year

        Returns:
            im_p: A cleaned pandas dataframe
        """

        if year == 2001:
            col_names = ['LocalArea',
                         'Total immigrant population',
                         '1996 to 2001']
            im_p = im_p[col_names]
            im_p.rename(columns={'1996 to 2001': 'Immigrates'}, inplace=True)

        elif year == 2006:
            col_names = ['LocalArea',
                         'Total immigrant population',
                         '2001 to 2006']
            im_p = im_p[col_names]
            im_p.rename(columns={'2001 to 2006': 'Immigrates'}, inplace=True)

        elif year == 2011:
            col_names = ['LocalArea',
                         'Immigrants',
                         '2006 to 2010']
            im_p = im_p[col_names]
            im_p.rename(columns={'Immigrants': 'Total immigrant population',
                                 '2006 to 2010': 'Immigrates'}, inplace=True)

        elif year == 2016:
            col_names = ['LocalArea', 'Immigrants', '2011 to 2016']
            im_p = im_p[col_names]
            im_p.rename(columns={'Immigrants': 'Total immigrant population',
                                 '2011 to 2016': 'Immigrates'}, inplace=True)

        im_p['Immigrates'] = im_p[
             'Immigrates'] / im_p[
             'Total immigrant population']

        im_p = im_p[['LocalArea', 'Immigrates']]

        return im_p

    def clean_citizenship(citizen, year):
        """
        This function cleans the citizenship census data
        Args:
            citizen (pd.DataFrame): The dataframe for citizenship data
            year (int): census year

        Returns:
            citizen: A cleaned pandas dataframe
        """

        if year == 2011:
            citizen = citizen[citizen['Unnamed: 0'] == 0]
            van_total = citizen.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Unnamed: 0'] = 0
            citizen = citizen.append(van_total, ignore_index=True)

        if year == 2001:
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

        return citizen

    def clean_generation_status(gen, year):
        """
        This function cleans the generational status census data
        Args:
            gen (pd.DataFrame): The dataframe for generational status data
            year (int): census year

        Returns:
            gen: A cleaned pandas dataframe
        """

        for i in gen.columns[3:]:
            gen[i] = gen[i] / gen[gen.columns[2]]

        gen = gen.iloc[:, [1, 3, 4, 5]]

        return gen

    def clean_household_size(house_size, year):
        """
        This function cleans the household size census data
        Args:
            house_size (pd.DataFrame): The dataframe for household size data
            year (int): census year

        Returns:
            house_size: A cleaned pandas dataframe
        """

        col_lis = list(house_size.columns)[3:8]
        for col in col_lis:
            house_size[col] = house_size[col] / house_size['Total households']

        house_size.rename(
            columns={'1 person': '1 person',
                     '2 persons': '2 persons',
                     '3 persons': '3 persons',
                     '4 persons': '4 to 5 persons',
                     '5 or more persons': '6+ persons',
                     '4 to 5 persons': '4 to 5 persons',
                     '6 or more persons': '6+ persons'},
            inplace=True)

        house_size = house_size[['LocalArea', '1 person',
                                 '2 persons', '3 persons',
                                 '4 to 5 persons',
                                 '6+ persons']]

        return house_size

    def clean_household_type(house_type, year):
        """
        This function cleans the household type census data
        Args:
            house_type (pd.DataFrame): The dataframe for household type data
            year (int): census year

        Returns:
            house_type: A cleaned pandas dataframe
        """

        for i in house_type.columns[3:]:
            house_type[i] = house_type[i]/house_type[house_type.columns[2]]

        house_type = house_type.iloc[:, [1, 3, 4, 5]]

        house_type.columns = ['LocalArea',
                              'One-family households',
                              'Multiple-family households',
                              'Non-family households']

        return house_type

    def clean_immigration_age(img_age, year):
        """
        This function cleans the immigration age census data
        Args:
            img_age (pd.DataFrame): The dataframe for immigration age data
            year (int): census year

        Returns:
            img_age: A cleaned pandas dataframe
        """

        img_age.rename(
            columns={'Under 5 years': 'Immigrants under 5 years',
                     '5 to 14 years': 'Immigrants 5 to 14 years',
                     '15 to 24 years': 'Immigrants 15 to 24 years',
                     '25 to 44 years': 'Immigrants 25 to 44 years',
                     '45 years and over': 'Immigrants 45 years and over'},
            inplace=True)

        img_age.drop(columns=['Unnamed: 0'], inplace=True)

        if year == 2011:
            img_age = img_age[img_age['Type'] == 'Total']
            van_total = img_age.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Type'] = 'Total'
            img_age = img_age.append(van_total, ignore_index=True)
            img_age.drop(columns=['Type'], inplace=True)

        col_lis = list(img_age.columns)[2:]
        for col in col_lis:
            img_age[col] = img_age[col]/img_age['Total immigrant population']

        return img_age

    def clean_industry(ind, year):
        """
        This function cleans the work industry census data
        Args:
            ind (pd.DataFrame): The dataframe for industry data
            year (int): census year

        Returns:
            ind: A cleaned pandas dataframe
        """

        col_lis = list(ind.columns)[5:]
        for col in col_lis:
            ind[col] = ind[col]/ind['total']

        ind['Industry - Not applicable'] = ind[
            'Industry - Not applicable'] / ind['total']

        ind.drop(columns=['All industries',
                          'Unnamed: 0',
                          'total'], inplace=True)

        return ind

    def clean_labour_force_status(labour, year):
        """
        This function cleans the labour force status census data
        Args:
            labour (pd.DataFrame): The dataframe for labour force data
            year (int): census year

        Returns:
            labour: A cleaned pandas dataframe
        """

        labour = labour[labour['Type'] == 'Total']
        van_total = labour.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'Total'
        labour = labour.append(van_total, ignore_index=True)

        labour = labour[['LocalArea',
                         'Employment rate',
                         'Unemployment rate']]

        return labour

    def clean_mobility(mob, year):
        """
        This function cleans the population mobility census data
        Args:
            mob (pd.DataFrame): The dataframe for mobility data
            year (int): census year

        Returns:
            mob: A cleaned pandas dataframe
        """

        mob['total'] = mob[
                'Non-movers 1 yr ago'] + mob[
                'Non-migrants 1 yr ago'] + mob[
                'Migrants 1 yr ago']

        mob['Non-movers 1 yr ago'] = mob[
            'Non-movers 1 yr ago'] / mob['total']
        mob['Non-migrants 1 yr ago'] = mob[
            'Non-migrants 1 yr ago'] / mob['total']
        mob['Migrants 1 yr ago'] = mob[
            'Migrants 1 yr ago'] / mob['total']

        mob = mob[['LocalArea',
                   'Non-movers 1 yr ago',
                   'Non-migrants 1 yr ago',
                   'Migrants 1 yr ago']]

        return mob

    def clean_occupation(occ, year):
        """
        This function cleans the occupational census data
        Args:
            occ (pd.DataFrame): The dataframe for occupation data
            year (int): census year

        Returns:
            occ: A cleaned pandas dataframe
        """

        occ['total'] = occ[
            list(occ.columns)[3]] + occ[list(occ.columns)[4]]

        col_lis = list(occ.columns)[4:]
        for col in col_lis:
            occ[col] = occ[col]/occ['total']

        occ = occ[occ.Type == "Total"]
        van_total = occ.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'Total'
        occ = occ.append(van_total, ignore_index=True)

        occ.drop(columns=['Type',
                          'All occupations',
                          'Unnamed: 0',
                          'total'], inplace=True)

        return occ

    def clean_time_worked(tw, year):
        """
        This function cleans the work time census data
        Args:
            house_type (pd.DataFrame): The dataframe for work time data
            tw (int): census year

        Returns:
            tw: A cleaned pandas dataframe
        """

        tw = tw.query('Type == "Total"')
        van_total = tw.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'Total'
        tw = tw.append(van_total, ignore_index=True)

        col_lis = list(tw.columns)[4:6]

        for col in col_lis:
            tw[col] = tw[col]/tw[
                'Population 15 years and over by work activity']

        tw = tw[['LocalArea', 'full time', 'part time']]

        return tw

    def clean_transport_mode(trans, year):
        """
        This function cleans the transport mode census data
        Args:
            trans (pd.DataFrame): The dataframe for transport mode data
            year (int): census year

        Returns:
            trans: A cleaned pandas dataframe
        """

        trans = trans.query('Type == "Total"')
        van_total = trans.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'Total'
        trans = trans.append(van_total, ignore_index=True)

        cols = list(trans.columns)[4:]
        for c in cols:
            trans[c] = trans[c]/trans['Total']

        trans.drop(columns=['Unnamed: 0',
                            'Type',
                            'Total'], inplace=True)

        return trans

    def clean_workplace_status(wp, year):
        """
        This function cleans the workplace status census data
        Args:
            wp (pd.DataFrame): The dataframe for workplace status data
            year (int): census year

        Returns:
            wp: A cleaned pandas dataframe
        """

        wp = wp.query('Type == "Total"')
        van_total = wp.sum()
        van_total['LocalArea'] = 'Metro Vancouver'
        van_total['Type'] = 'Total'
        wp = wp.append(van_total, ignore_index=True)

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

        return wp

    def clean_education(education, year):
        """
        This function cleans the education census data
        Args:
            education (pd.DataFrame): The dataframe for education data
            year (int): census year

        Returns:
            education: A cleaned pandas dataframe
        """

        if year == 2001:
            no_deg = education[
                'population 20 years and over - Less than grade 9'] + education[
                'population 20 years and over - Grades 9 to 13'] + education[
                'population 20 years and over - Without High school diploma or equivalent']

            high = education['population 20 years and over - High school diploma or equivalent']
            trade = education['population 20 years and over - Apprenticeship or trades certificate or diploma']
            college = education[
                'population 20 years and over - College'] + education[
                'population 20 years and over - College without certificate or diploma'] + education[
                'population 20 years and over - College, CEGEP or other non-university certificate or diploma']

            total = education['Total population 20 years and over']

        elif year == 2006:
            no_deg = education['population aged 15 years and over - No certificate, diploma or degree']
            high = education['population aged 15 years and over - High school certificate or equivalent']
            trade = education['population aged 15 years and over - Apprenticeship or trades certificate or diploma']
            college = education['population aged 15 years and over - College, CEGEP or other non-university certificate or diploma']
            total = education['Total population aged 15 years and over']

        elif year in [2011, 2016]:
            no_deg = education['population aged 15 years and over - No certificate, diploma or degree']
            high = education['population aged 15 years and over - High school diploma or equivalent']
            trade = education['population aged 15 years and over - Apprenticeship or trades certificate or diploma']
            college = education['population aged 15 years and over - College, CEGEP or other non-university certificate or diploma']
            total = education['Total population aged 15 years and over']
            if year == 2011:
                education = education.query('Type == "Total"')
                van_total = education.sum()
                van_total['LocalArea'] = 'Metro Vancouver'
                van_total['Type'] = 'Total'
                education = education.append(van_total, ignore_index=True)

        uni = total - no_deg - high - trade - college
        education['No certificate/diploma'] = no_deg/total
        education['High school'] = high/total
        education['Apprenticeship/Trades'] = trade/total
        education['College'] = college/total
        education['University'] = uni/total

        education = education[['LocalArea',
                               'No certificate/diploma',
                               'High school',
                               'Apprenticeship/Trades',
                               'College',
                               'University']]

        return education

    def clean_immigration_birth_place(im_birth, year):
        """
        This function cleans the immigration birth place census data
        Args:
            im_birth (pd.DataFrame): Dataframe for immigrant birth place data
            year (int): census year

        Returns:
            im_birth: A cleaned pandas dataframe
        """

        if year == 2011:
            im_birth = im_birth.query('Type == "Total"')
            van_total = im_birth.sum()
            van_total['LocalArea'] = 'Metro Vancouver'
            van_total['Type'] = 'Total'
            im_birth = im_birth.append(van_total, ignore_index=True)

        col_lis = ['Non-immigrants',
                   'Non-permanent residents',
                   'Immigrants']

        for col in col_lis:
            im_birth[col] = im_birth[col]/im_birth['Total population']

        im_birth = im_birth[['LocalArea',
                             'Non-immigrants',
                             'Non-permanent residents',
                             'Immigrants']]

        return im_birth

    ###########################################################################
    #  MAIN FUNCTION
    ###########################################################################

    list_years = [2001, 2006, 2011, 2016]
    excluded = ["official_language.csv", "worker_class.csv"]
    list_files = ['population_gender']

    # get names for all census data .csv files
    for year in list_years:
        directory = path_in + "_" + str(year)
        for entry in os.scandir(directory):
            if entry.name not in excluded and entry.is_file():
                general_file = os.path.splitext(entry.name)[0]
                file_name = (general_file + "_" + str(year))

                # create list of all main sub-groups
                if general_file not in list_files:
                    list_files.append(general_file)

                # read-in all census data files
                if file_name == "immigration_period_2011":
                    df = pd.read_csv(path_in + "_2016/immigration_period.csv")
                elif file_name == "immigration_age_2001":
                    df = pd.read_csv(path_in + "_2006/immigration_age.csv")
                else:
                    df = pd.read_csv(entry.path)

                # remove non-neighbourhoods from local areas
                df = df[~((df.LocalArea == 'Vancouver CMA') | (
                        df.LocalArea == 'Vancouver CSD'))]
                van_total = df.sum()
                van_total['LocalArea'] = 'Metro Vancouver'
                df = df.append(van_total, ignore_index=True)

                # clean dataframes
                func_name = "clean_" + general_file
                globals()[file_name] = eval(func_name)(df, year)

                # run second cleaning function for population gender data
                if general_file == "population_age_sex":
                    globals()[
                        ('population_gender_' + str(year))] = clean_gender(df, year)

    ###########################################################################
    # SYNTHESIS of census data sets
    ###########################################################################

    # read in local areas boundaries
    total_df = gpd.read_file(area_file)
    total_df.drop(columns=['mapid', 'geometry'], inplace=True)
    total_df.columns = ['LocalArea']
    add_df = pd.DataFrame(data={'LocalArea': 'Metro Vancouver'}, index=[0])
    total_df = total_df.append(add_df, ignore_index=True)
    total_df = pd.concat([total_df]*len(list_years))
    total_df.reset_index(drop=True, inplace=True)
    total_df['Year'] = 0
    i = 0

    for year in list_years:
        total_df.iloc[i:i+23]['Year'] = year
        i += 23
    for topic in list_files:
        all_years = []
        for year in list_years:
            df = eval((topic + "_" + str(year)))
            df['Year'] = year
            all_years.append(df)
        whole = pd.concat(all_years)
        total_df = total_df.merge(whole, on=['LocalArea', 'Year'])
    total_df.to_csv(path_out, index=False)


if __name__ == "__main__":
    main(opt["--path_in"], opt["--path_out"], opt["--area_file"])
