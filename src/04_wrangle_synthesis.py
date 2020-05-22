# author: Xinwen Wang
# date: 2020-05-21

"""
This script performs data wrangling and sythesis for multiple csv
and saves it to a specified file path. The input licence data needs to 
be the output of 03_clean_wrangle.py script

Usage: src/04_wrangle_sythesis.py --file_path1=<file_path1> --file_path2=<file_path2> --file_path3=<file_path3> --file_path4=<file_path4> --file_path5=<file_path5> --save_to=<save_to>

Options:
--file_path1=<file_path1>        This is the file path for the raw
                                parking meter dataset
--file_path2=<file_path2>        This is the file path of the raw
                                disability parking dataset
--file_path3=<file_path3>        This is the file path for the cleaned
                                licence dataset
--file_path4=<file_path4>       This is the file path for the raw bc employment
--file_path5=<file_path5>       This is the file path for the raw
                                Vancouver employment data 
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages
from docopt import docopt
import pandas as pd
import numpy as np
import zipfile
import warnings



opt = docopt(__doc__)


def main(file_path1, file_path2, file_path3, file_path4, file_path5, save_to):
    
    parking_meters_df = pd.read_csv(file_path1,sep=';')
    disability_parking_df = pd.read_csv(file_path2,sep=';')
    licence_df =  pd.read_csv(file_path3,low_memory=False)

    #read from zip file
    vancouver_zip_path = file_path4
    with zipfile.ZipFile(vancouver_zip_path,"r") as z:
        with z.open("14100096.csv") as f:
            vancouver_employment = pd.read_csv(f, header=0, delimiter=",")

    bc_zip_path = file_path5
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

    #synthesis
    
    #combine two parking
    final_parking_df = meter_count_df.merge(area_count_df, on = 'Geo Local Area')
    
    #combine with licence
    licence_df.rename(columns = {'LocalArea':'Geo Local Area'}, inplace = True)
    licence_df = licence_df.merge(final_parking_df, on = 'Geo Local Area')

    #change folderyear to be int
    licence_df = licence_df.astype({'FOLDERYEAR': 'int'})
    unemployment_rate.rename(columns = {'REF_DATE':'FOLDERYEAR','VALUE':'Unemployment_rate'}, inplace = True)
    licence_df = licence_df.merge(unemployment_rate, on = 'FOLDERYEAR', how ='left')

    # save to a new csv
    licence_df.to_csv(save_to, index=False)


if __name__ == "__main__":
    main(opt["--file_path1"], opt["--file_path2"], opt["--file_path3"], opt["--file_path4"], opt["--file_path5"], opt["--save_to"])
