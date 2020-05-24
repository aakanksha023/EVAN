# author: Xinwen Wang
# date: 2020-05-21

"""
This script performs data wrangling and sythesis for multiple csv
and saves it to a specified file path. The input licence data needs to 
be the output of 03_clean_wrangle.py script. The ouput will be feeding into
machine learning algorithm and visualization.

Usage: src/04_wrangle_sythesis.py --file_path1=<file_path1> --file_path2=<file_path2> --file_path3=<file_path3> --file_path4=<file_path4> --file_path5=<file_path5> --save_to1=<save_to1> --save_to2=<save_to2> --save_to3=<save_to3> --save_to4=<save_to4>

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
import warnings



opt = docopt(__doc__)


def main(file_path1, file_path2, file_path3, file_path4, file_path5, save_to1, save_to2, save_to3, save_to4):
    
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

    # wrangle for visualization
    parking_meters_df["coord-x"] = parking_meters_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    parking_meters_df["coord-y"] = parking_meters_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][1])
    disability_parking_df["coord-x"] = disability_parking_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][0])
    disability_parking_df["coord-y"] = disability_parking_df['Geom'].apply(lambda p: json.loads(p)['coordinates'][1])

    #filter out point without Geom location
    licence_vis_df = licence_df[~licence_df['Geom'].isnull()]
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


    # save to a new csv
    licence_df.to_csv(save_to1, index=False)
    parking_meters_df.to_csv(save_to2, index=False)
    disability_parking_df.to_csv(save_to3, index=False)
    licence_vis_df.to_csv(save_to4, index=False)


if __name__ == "__main__":
    main(opt["--file_path1"], opt["--file_path2"], opt["--file_path3"], opt["--file_path4"], opt["--file_path5"], opt["--save_to1"], opt["--save_to2"], opt["--save_to3"], opt["--save_to4"])
