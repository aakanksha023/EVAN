import re
import pandas as pd


def create_census_dict_2016(census_df):
    """
    Cleans up CensusLocalAreaProfiles2016.csv data by splitting different
    tables on the same excel sheet into separate dataframes and stores the
    dataframes into a lookup dictionary.

    This function ignores the 25% sample data stored in the same worksheet.

    Parameters:
    -----------
    census_df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning

    Returns:
    -----------
    dict:
        A lookup dictionary
        keys are given by the first row of the 'Variable' column in census_df
        and corresponding dataframe stored as values.
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
            sub_df = sub_df.set_index('Variable').T.reset_index().rename(columns={'index': 'LocalArea'})

            # clean up names and store dataframes into the dictionary
            census_dict[df.Variable[start].rstrip().lstrip()] = sub_df
            start = s

        start = r+1

    return census_dict


def create_census_dict_2011(census_df):
    """
    Cleans up CensusLocalAreaProfiles2011.csv data by splitting different
    tables on the same excel sheet into separate dataframes and stores the
    dataframes into a lookup dictionary.

    Parameters:
    -----------
    census_df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning

    Returns:
    -----------
    dict:
        A lookup dictionary
        keys are given by the first row of the 'Variable' column in census_df
        and corresponding dataframe stored as values.
    """
    # Rename dataframe columns and remove leading whitespace
    census_df = census_df.dropna(how='all')
    census_df = census_df.rename(columns={census_df.columns[0]: "Variable"})
    census_df.Variable = census_df.Variable.apply(lambda x: x.lstrip())
    
    # Initialise variables for the lookup dictionary
    census_dict = {}
    start = 0
    
    # create a separate dataframe for first word starts with: Total, Median, Average
    re1 = ['total', 'median', 'average']
    subgroup = list(census_df[census_df.Variable.str.contains('|'.join(re1), flags=re.IGNORECASE)].index)
    subgroup = subgroup[1:]
    
    for s in subgroup:
        sub_df = census_df.loc[start:s-1]
        # transpose dataframe and rename column
        sub_df = sub_df.set_index('Variable').T.reset_index().rename(columns={'index': 'LocalArea'})
        
        # clean up names and store dataframes into the dictionary
        census_dict[census_df.Variable[start].rstrip().lstrip()] = sub_df
        start = s
    
    return census_dict


def create_census_dict_2006(df):
     """
    Cleans up CensusLocalAreaProfiles2006.csv data by dsplitting different
    tables on the same excel sheet into separate dataframes and stores the
    dataframes into a lookup dictionary.

    Parameters:
    -----------
    df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning

    Returns:
    -----------
    dict:
        A lookup dictionary
        keys are given by the first row of the 'Variable' column in census_df
        and corresponding dataframe stored as values.
    """


    df = df.dropna(0,'all')
    df = df.rename(columns={'Unnamed: 0': 'Variable'})
    df.Variable = df.Variable.apply(lambda x: x.lstrip())

    census_dict = {}
    start = 0
    re1 = ['Total.*by', 'Population.*by']
    subgroup = list(df[df.Variable.str.contains('|'.join(re1), flags=re.IGNORECASE)].index)
    subgroup = subgroup[1:]
    
    for s in subgroup:
        sub_df = df.loc[start:s-1]
        sub_df = sub_df.set_index('Variable').T.reset_index().rename(columns={'index': 'LocalArea'})
        census_dict[df.Variable[start].rstrip().lstrip()] = sub_df
        start = s


    return census_dict

def create_census_dict_2001(census_df):
    """
    Cleans up the census_2001.csv data by splitting the csv into
    separate dataframes and stores the dataframes into a lookup dictionary.

    Parameters:
    -----------
    census_df: pandas.core.frame.DataFrame
        The pandas dataframe to be performed data cleaning

    Returns:
    -----------
    dict:
        A lookup dictionary
        keys are given by the first row of the 'Variable' column in census_df
        and corresponding dataframe stored as values.
    """
    # rename dataframe columns and remove leading whitespace
    census_df.dropna(0, thresh=25, inplace=True)
    census_df = census_df.rename(columns={'Unnamed: 0': 'Variable'})
    census_df.Variable = census_df.Variable.apply(lambda x: x.lstrip())

    # initialize variables for the lookup dictionary
    census_dict = {}
    start = 0

    # separate dataframe by 'Variables' containing regex expressions:
    re1 = ['total.*by', 'population.*by']
    subgroup = list(census_df[census_df.Variable.str.contains('|'.join(re1), flags=re.IGNORECASE)].index)
    subgroup = subgroup[1:]

    for s in subgroup:
        sub_df = census_df.loc[start:s-1]

        # transpose dataframe and rename column
        sub_df = sub_df.set_index('Variable').T.reset_index().rename(columns={'index': 'LocalArea'})

        # clean up names and store dataframes into the dictionary
        census_dict[census_df.Variable[start].rstrip().lstrip()] = sub_df
        start = s

    return census_dict
