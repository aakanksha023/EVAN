# author: Jasmine Qin
# date: 2020-05-27

"""
This script performs feature engineering for a specified csv
and saves it to a specified file path.

Usage: src/03_modelling/06_feature_engineering.py --file_path=<file_path> --save_to=<save_to>

Options:
--file_path=<file_path>        This is the file path of the csv
                               to be performed feature engineering
--save_to=<save_to>            This is the file path the processed
                               csv will be saved to
"""

# load packages


opt = docopt(__doc__)

def historic_mapping(df, col='BusinessType'):
    """
    This function creates mapping rules for historic 
    BusinessType and BusinessSubType. 
    
    Parameters:
    -----------
    df: pandas.core.frame.DataFrame
        The dataframe used to set-up mapping rules
    
    col: str
        The column where historic types need to be cleaned
        
    Returns:
    -----------
    dict: A look-up dictionary
    """
    
    df = df.copy(deep=True).dropna(subset=[col])
    
    contain_historic = df.groupby('BusinessName')[col].apply(
    lambda x: list(x) if x.str.contains('\*').any() else False)

    contain_historic_list = [
        list(set(i)) for i in contain_historic[~(contain_historic == False)].tolist()]
    
    historic_lookup_all = defaultdict(Counter)
    
    for items in contain_historic_list:
        new_types, historic_types = [], []
        for bt in items:
            if 'Historic' not in bt:
                new_types.append(bt)
            else:
                historic_types.append(bt)
        for h in historic_types:
            for n in new_types:
                historic_lookup_all[h][n] += 1
                
    historic_lookup = {}
    for key,value in historic_lookup_all.items():
        historic_lookup[key] = value.most_common()[0][0]
        
    return historic_lookup


def main(file_path, save_to):
    """
    Feature engineering main function.
    """

    df = pd.read_csv(file_path, low_memory=False)
    
    # 1. Remove missing LocalArea
    df = df[df.LocalArea.notnull()]
    
    # 2. Remove previous status != Issued
    df = df[df.Status == 'Issued']

    # 3. Map historic types to current ones
    df = df.replace({'BusinessType': historic_mapping(
        df), 'BusinessSubType': historic_mapping(df, col='BusinessSubType')})
    
    # 4. Group business types
    # INSERT CODE HERE
    
    df = df[num_vars+cat_vars+label]
    
    return df.drop(columns=label), df['label']

    
if __name__ == "__main__":
    main(opt["--file_path"], opt["--save_to"])