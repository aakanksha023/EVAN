# author: Xinwen Wang
# date: 2020-05-21

"""
This script performs data wrangling and sythesis for multiple csv
and saves it to a specified file path. The input licence data needs to 
be the output of 03_clean_wrangle.py script. The ouput will be feeding into
machine learning algorithm and visualization.

Usage: src/02_clean_wrangle/04_sythesis.py --file_path=<file_path>  --save_to1=<save_to1> --save_to2=<save_to2> --save_to3=<save_to3> --save_to4=<save_to4>

Options:
--file_path=<file_path>        A txt file storing two-dimensional array, 
                               specifing the file path for input dataset.
--save_to1=<save_to1>           This is the file path the processed training
                               csv will be saved to
--save_to2=<save_to2>           This is the file path the parking meters for visualization
                               will be saved to
--save_to3=<save_to3>           This is the file path the disability parking
                                for visualization will be saved to
--save_to4=<save_to4>           This is the file path the licence data for visualization
                               will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import numpy as np
import zipfile
import json
import re
from datetime import date
from datetime import datetime
import warnings



opt = docopt(__doc__)


def main(file_path, save_to1, save_to2, save_to3, save_to4):
    
    #read files

    with open(file_path, 'r') as file:
        file_path = file.read().replace('\n', '')
    
    file_path = file_path.strip('[]')
    file_path = re.findall(r'\([^\)\(]*\)', file_path)

    file_lis=[]

    for file in file_path:
        file_name = file.strip('()')
        file_lis.append(file_name)
    
    disability_parking_df = pd.read_csv(file_lis[0],sep=';')
    parking_meters_df = pd.read_csv(file_lis[1],sep=';')
    
    licence_df =  pd.read_csv(file_lis[2],low_memory=False)

    #census
    family_2001 = pd.read_csv(file_lis[5])
    family_2006 = pd.read_csv(file_lis[6])
    family_2011 = pd.read_csv(file_lis[7])
    family_2016 = pd.read_csv(file_lis[8])
    #language_2001 = pd.read_csv(file_lis[9])
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
    minority_2001 = pd.read_csv(file_lis[20])
    minority_2006 = pd.read_csv(file_lis[21])
    minority_2011 = pd.read_csv(file_lis[22])
    minority_2016 = pd.read_csv(file_lis[23])
    dwelling_2001 = pd.read_csv(file_lis[24])
    dwelling_2006 = pd.read_csv(file_lis[25])
    dwelling_2011 = pd.read_csv(file_lis[26])
    dwelling_2016 = pd.read_csv(file_lis[27])
    shelter_2001 = pd.read_csv(file_lis[28])
    shelter_2006 = pd.read_csv(file_lis[29])
    shelter_2011 = pd.read_csv(file_lis[30])
    shelter_2016 = pd.read_csv(file_lis[31])
    lone_parent_2001 = pd.read_csv(file_lis[32])
    lone_parent_2006 = pd.read_csv(file_lis[33])
    lone_parent_2011 = pd.read_csv(file_lis[34])
    lone_parent_2016 = pd.read_csv(file_lis[35])
    imgra_period_2001 = pd.read_csv(file_lis[36])
    imgra_period_2006 = pd.read_csv(file_lis[37])
    imgra_period_2011 = pd.read_csv(file_lis[38])
    imgra_period_2016 = pd.read_csv(file_lis[39])




    #suppress warning
    pd.options.mode.chained_assignment = None

    #read from zip file
    vancouver_zip_path = file_lis[3]
    with zipfile.ZipFile(vancouver_zip_path,"r") as z:
        with z.open("14100096.csv") as f:
            vancouver_employment = pd.read_csv(f, header=0, delimiter=",")

    bc_zip_path = file_lis[4]
    with zipfile.ZipFile(bc_zip_path,"r") as z:
        with z.open("14100327.csv") as f:
            bc_employment = pd.read_csv(f, header=0, delimiter=",")
        
    #clean

    #only keeping Geom, and Geo Local Area column 
    disability_parking_df = disability_parking_df[['Geom','Geo Local Area']]
    # groupby Local area to get a count of how many parking in a local area
    area_count_df = disability_parking_df.groupby('Geo Local Area').count()
    area_count_df.rename(columns = {'Geom':'Disability parking'}, inplace = True)
    #this is kept for individual point/for vis
    disability_parking_df = disability_parking_df.merge(area_count_df, on = 'Geo Local Area', how = 'left')

    #same processing as disability dataset
    parking_meters_df = parking_meters_df[['Geom','Geo Local Area']]
    meter_count_df = parking_meters_df.groupby('Geo Local Area').count()
    meter_count_df.rename(columns = {'Geom':'Parking meters'}, inplace = True)
    #this is kept for individual point
    parking_meters_df = parking_meters_df.merge(meter_count_df, on='Geo Local Area', how = 'left')


    #Clean bc employmentd data, only need 1997-2000 as subsitude for vancouver
    bc_unemployment = bc_employment[(bc_employment['GEO']=='British Columbia')&
                  (bc_employment['Labour force characteristics'] == 'Unemployment rate') &
                  (bc_employment['REF_DATE']<2001) &(1996<bc_employment['REF_DATE']) &
                  (bc_employment['UOM']=='Percentage') &
                  (bc_employment['Age group'] == '15 years and over')&
                  (bc_employment['Sex']=='Both sexes') ][['REF_DATE','VALUE']]

    #clean Vancouver data, since BC level only have unemployment, use unemployment rate
    #note unemployment+employment !=1 
    vancouver_unemployment = vancouver_employment[(vancouver_employment['GEO'] == 'Vancouver, British Columbia') & 
                     (vancouver_employment['Labour force characteristics'] == 'Unemployment rate') &
                     (vancouver_employment['Sex'] == 'Both sexes') &
                     (vancouver_employment['UOM'] == 'Percentage') &
                     (vancouver_employment['Age group'] == '15 years and over')][['REF_DATE','VALUE']]

    
    unemployment_rate = pd.concat([bc_unemployment, vancouver_unemployment])

    #for census data

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
        df.reset_index(drop = True, inplace = True)
        df['Year'] = 0
        i = 0
        for year in year_lis:
            df.iloc[i:i+24]['Year'] = year
            i+=24
        return df

    # for family sub-data
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
        family.drop(columns = ['Unnamed: 0','Type'], inplace = True)
        family = fill_missing_year(family , start_year, end_year)
        
        return family


    family_2001 = clean_family(family_2001, 1997, 2002)
    family_2006 = clean_family(family_2006, 2002, 2007)
    family_2011 = clean_family(family_2011, 2007, 2012)
    family_2016 = clean_family(family_2016, 2012, 2020)


    #for language sub-data
    
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
        language = language[language['Type']=='mother tongue - total']
        language.drop(columns = ['Unnamed: 0','Type', 'Total'], inplace = True)
        language = fill_missing_year(language, start_year, end_year)
        return language

    #language_2001 = clean_language(language_2001, 1997, 2002)
    language_2006 = clean_language(language_2006, 2002, 2007)
    language_2011 = clean_language(language_2011, 2007, 2012)
    language_2016 = clean_language(language_2016, 2012, 2020)

    
    #for marital sub-data
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
   
        marital.drop(columns = ['Unnamed: 0'], inplace = True)
        marital = fill_missing_year(marital, start_year, end_year)
        return marital

    
    marital_2001 = clean_marital(marital_2001, 1997, 2002)
    marital_2006 = clean_marital(marital_2006, 2002, 2007)
    marital_2011 = clean_marital(marital_2011, 2007, 2012)
    marital_2016 = clean_marital(marital_2016, 2012, 2020)

    
    #for population sub-data
    def clean_age_sex(age, start_year, end_year):
        """
        This function cleans the marital census data
        Args:
            age (pandas dataframe): The dataframe for population data
            start_year (int): The four digit strat year
            end_year (int): The four digit end year, note end year not included

        Returns:
            age: A cleaned pandas dataframe

        """
        age = age[age['Type']== 'total']
        age.drop(columns = ['Unnamed: 0', 'Type'], inplace = True)
        age = fill_missing_year(age, start_year, end_year)
        return age

    population_2001 = clean_age_sex(population_2001, 1997, 2002)
    population_2006 = clean_age_sex(population_2006, 2002, 2007)
    population_2011 = clean_age_sex(population_2011, 2007, 2012)
    population_2016 = clean_age_sex(population_2016, 2012, 2020)

    
    #for visible minority
    def clean_minority(mino, start_year, end_year):
    
        #convert the number of minority into porpotion
        col_lis = list(mino.columns)[5:]
        for col in col_lis:
            mino[col] = mino[col]/mino['Total visible minority population']
            
        mino.drop(columns = ['Unnamed: 0'], inplace = True)
        mino = fill_missing_year(mino, start_year, end_year)
        return mino

    minority_2001 = clean_minority(minority_2001, 1997, 2002)
    minority_2006 = clean_minority(minority_2006, 2002, 2007)
    minority_2011 = clean_minority(minority_2011, 2007, 2012)
    minority_2016 = clean_minority(minority_2016, 2012, 2020)
    
    # for dwelling
    def clean_dwelling(dwel, start_year, end_year):
        dwel.rename(columns = {'Total':'Total number of dwelling'}, inplace = True)
        dwel.drop(columns = ['Unnamed: 0'], inplace = True)
        dwel = fill_missing_year(dwel, start_year, end_year)
        return dwel
        
        
    dwelling_2001 = clean_dwelling(dwelling_2001, 1997, 2002)
    dwelling_2006 = clean_dwelling(dwelling_2006, 2002, 2007)
    dwelling_2011 = clean_dwelling(dwelling_2011, 2007, 2012)
    dwelling_2016 = clean_dwelling(dwelling_2016, 2012, 2020)

    #shelter tenure
    def clean_shelter(shel, start_year, end_year):
    
        shel.rename(columns = {'Owned':'Owned shelter', 'Rented':'Rented shelter',
                            'Band housing':'Band housing shelter'}, inplace = True)
        shel.drop(columns = ['Unnamed: 0'], inplace = True)
        shel = fill_missing_year(shel, start_year, end_year)
        return shel
    
    shelter_2001 = clean_shelter(shelter_2001, 1997, 2002)
    shelter_2006 = clean_shelter(shelter_2006, 2002, 2007)
    shelter_2011 = clean_shelter(shelter_2011, 2007, 2012)
    shelter_2016 = clean_shelter(shelter_2016, 2012, 2020)

    #lone parent
    def clean_lone_parent(lone, start_year, end_year):
        lone.rename(columns = {'1 child':'1 child lone parent', '2 children': '2 children lone parent',
                            '3 or more children': '3 or more children lone parent'}, inplace = True)
        lone.drop(columns = ['Unnamed: 0'], inplace = True)
        lone = fill_missing_year(lone, start_year, end_year)
        return lone
    
    lone_parent_2001 = clean_lone_parent(lone_parent_2001, 1997, 2002)
    lone_parent_2006 = clean_lone_parent(lone_parent_2006, 2002, 2007)
    lone_parent_2011 = clean_lone_parent(lone_parent_2011, 2007, 2012)
    lone_parent_2016 = clean_lone_parent(lone_parent_2016, 2012, 2020)
    

    #for immigrates_period
    def clean_imgra_period(im_p, start_year, end_year):
        # please note that start year should only be 1997 or 2002 or 2007 or 2012
        im_p.rename(columns = {'Total population':'Total immigration population'}, inplace = True)
        if start_year == 1997:
            col_names = ['Total immigration population', 'Non-immigrants', 
                        'Non-permanent residents', '1991 to 2000']
            im_p = im_p[col_names]
            im_p.rename(columns = {'1991 to 2000':'Immigrates'}, inplace = True)
        elif start_year == 2002:
            col_names = ['Total immigration population', 'Non-immigrants', 
                        'Non-permanent residents', '2001 to 2005']
            im_p = im_p[col_names]
            im_p.rename(columns = {'2001 to 2005':'Immigrates'}, inplace = True)
        elif start_year == 2007:
            col_names = ['Total immigration population', 'Non-immigrants', 
                        'Non-permanent residents', '2006 to 2010']
            im_p = im_p[col_names]
            im_p.rename(columns = {'2006 to 2010':'Immigrates'}, inplace = True)
        elif start_year == 2012:
            col_names = ['Total immigration population', 'Non-immigrants', 
                        'Non-permanent residents', '2011 to 2016']
            im_p = im_p[col_names]
            im_p.rename(columns = {'2011 to 2016':'Immigrates'}, inplace = True)
        else:
            print('Invalid start year. A valid start year should be 1997 or 2002 or 2007 or 2012')
        
        
        im_p = fill_missing_year(im_p, start_year, end_year)
        return im_p
    
    imgra_period_2001 = clean_imgra_period(imgra_period_2001, 1997, 2002)
    imgra_period_2006 = clean_imgra_period(imgra_period_2006, 2002, 2007)
    imgra_period_2011 = clean_imgra_period(imgra_period_2011, 2007, 2012)
    imgra_period_2016 = clean_imgra_period(imgra_period_2016, 2012, 2020)

    #wrangle for visualization(might delete it)
    
    #wangle the issueddate into datetime format
    licence_vis_df = licence_df[~licence_df['IssuedDate'].isnull()]
    date_format = '%Y-%m-%d'
    licence_vis_df['IssuedDate'] = licence_vis_df['IssuedDate'].apply(lambda p: datetime.strptime(p, date_format).strftime("%Y-%m-%d %H:%M:%S"))

    #wrangle the Geom into coordinates
    parking_meters_df["coord-x"] = parking_meters_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    parking_meters_df["coord-y"] = parking_meters_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][1])
    disability_parking_df["coord-x"] = disability_parking_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    disability_parking_df["coord-y"] = disability_parking_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][1])

    #filter out point without Geom location
    licence_vis_df = licence_vis_df[~licence_vis_df['Geom'].isnull()]
    licence_vis_df["coord-x"] = licence_vis_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    licence_vis_df["coord-y"] = licence_vis_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][1])

    #synthesis
    
    #combine two parking
    final_parking_df = meter_count_df.merge(area_count_df, on = 'Geo Local Area', how = 'outer')
    
    #combine with licence
    licence_df.rename(columns = {'LocalArea':'Geo Local Area'}, inplace = True)
    licence_df = licence_df.merge(final_parking_df, on = 'Geo Local Area', how = 'left')

    #change folderyear to be int
    licence_df = licence_df.astype({'FOLDERYEAR': 'int'})
    unemployment_rate.rename(columns = {'REF_DATE':'FOLDERYEAR','VALUE':'Unemployment_rate'}, inplace = True)
    licence_df = licence_df.merge(unemployment_rate, on = 'FOLDERYEAR', how ='left')
    
    #census data
    family = pd.concat([family_2001, family_2006, family_2011, family_2016])
    family.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(family, on = ['Geo Local Area','FOLDERYEAR'], how = 'left')

    #language = pd.concat([language_2001, language_2006, language_2011, language_2016])
    language = pd.concat([language_2006, language_2011, language_2016])
    language.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    #filter out nan values
    language.dropna(axis = 1, inplace = True)
    licence_df = licence_df.merge(language, on = ['Geo Local Area','FOLDERYEAR'], how ='left')

    marital = pd.concat([marital_2001, marital_2006, marital_2011, marital_2016])
    marital.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(marital, on = ['Geo Local Area','FOLDERYEAR'], how ='left')
    
    population = pd.concat([population_2001, population_2006, population_2011, population_2016])
    population.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(population, on = ['Geo Local Area','FOLDERYEAR'], how ='left')

    minority = pd.concat([minority_2001, minority_2006, minority_2011, minority_2016])
    minority.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(minority, on = ['Geo Local Area','FOLDERYEAR'], how ='left')

    dwelling = pd.concat([dwelling_2001, dwelling_2006, dwelling_2011, dwelling_2016])
    dwelling.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(dwelling, on = ['Geo Local Area','FOLDERYEAR'], how ='left')
    
    shelter = pd.concat([shelter_2001, shelter_2006, shelter_2011, shelter_2016])
    shelter.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(shelter, on = ['Geo Local Area','FOLDERYEAR'], how ='left')

    lone_parent = pd.concat([lone_parent_2001, lone_parent_2006, lone_parent_2011, lone_parent_2016])
    lone_parent.rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(lone_parent, on = ['Geo Local Area','FOLDERYEAR'], how ='left')

    imgra_period = pd.concat([imgra_period_2001, imgra_period_2006, imgra_period_2011, imgra_period_2016])
    imgra_period .rename(columns = {'LocalArea': 'Geo Local Area', 'Year':'FOLDERYEAR'}, inplace = True)
    licence_df = licence_df.merge(imgra_period, on = ['Geo Local Area','FOLDERYEAR'], how ='left')




    # save to a new csv
    licence_df.to_csv(save_to1, index=False)
    parking_meters_df.to_csv(save_to2, index=False)
    disability_parking_df.to_csv(save_to3, index=False)
    licence_vis_df.to_csv(save_to4, index=False)


if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to1"], opt["--save_to2"], opt["--save_to3"], opt["--save_to4"])
