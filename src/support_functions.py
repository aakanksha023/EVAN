import pandas as pd
import re

def create_census_dict_2016(census_df):
    """
    Cleans up CensusLocalAreaProfiles2016.csv data by splitting different tables on the same excel sheet 
    into separate dataframes and stores the dataframes into a lookup dictionary.
    
    This function ignores the 25% sample data which is stored in the same worksheet.
    
    Parameters:
    -----------
    census_df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning
    
    Returns:
    -----------
    dict: A lookup dictionary with the names given by first rows of the 'Variable' column in census_df as keys
        and corresponding dataframe stored as values
    """
    
    # drop 25% sample data
    census_df = census_df[0:census_df.query('ID == "25% Data Below"').index[0]].drop(columns=['ID'])
    
    # first split dataframes by empty lines
    split_null = census_df[census_df.Variable.isnull()].index
    census_dict = {}
    start = 0

    for r in split_null:

        df = census_df.iloc[start:r]
        
        # skip if consecutive nan rows
        if len(df) == 0:
            start = r+1
            continue
        
        # create a separate dataframe for first word starts with:
        re1 = ['total', 'median', 'average']
        subgroup = list(df[df.Variable.str.contains('|'.join(re1), flags=re.IGNORECASE)].index)
        subgroup = subgroup[1:]
        subgroup.append(r)

        # for sub dataframes within one chunk (dataframes not separated by empty lines)
        for s in subgroup:
            sub_df = df.loc[start:s-1]
            
            # transpose dataframe and rename column
            sub_df = sub_df.set_index('Variable').T.reset_index().rename(columns={'index':'LocalArea'})
            
            # clean up names and store dataframes into the dictionary
            census_dict[df.Variable[start].rstrip().lstrip()] = sub_df
            start = s

        start = r+1
        
    return census_dict

def create_census_dict_2011(census_df):
    """
    Cleans up CensusLocalAreaProfiles2011.xls data by splitting different tables on the same excel sheet 
    into separate dataframes and stores the dataframes into a lookup dictionary.
    
    Parameters:
    -----------
    census_df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning
    
    Returns:
    -----------
    dict: A lookup dictionary with the names given by first rows of the 'Variable' column in census_df as keys
        and corresponding dataframe stored as values
    """
    # organize census dataframe
    census_df = census_df.dropna(how='all')
    census_df = census_df.rename(columns={census_df.columns[0]: "Variable" })
    
    # find rows with 'Variable' 0 leading space
    pos = [len(s) - len(s.lstrip()) for s in census_df.Variable]
    pos.append(0)
    start = 0
    census_dict = {}

    # split at rows with 'Variable' 0 leading space
    for r in range(1, len(pos)):
        if pos[r] == 0:

            # if name already exists, combine it with the second row
            if census_df.loc[start].Variable in census_dict.keys():
                name = census_df.loc[start].Variable + census_df.loc[start+1].Variable
            else:
                name = census_df.loc[start].Variable

            census_dict[name] = census_df.loc[start:r-1]
            start = r
            
    return census_dict