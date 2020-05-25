import pandas as pd
import geopandas as gpd
import keplergl

licence_df = pd.read_csv('../data/processed/licence_vis.csv')
dis_parking_df = pd.read_csv('data/processed/disability_parking_vis.csv')
parking_meter_df = pd.read_csv('data/processed/paking_meter_vis.csv')

w2 = keplergl.KeplerGl(height=1000,width=100)
w2.add_data(licence_df, name = "Census")
w2.add_data(parking_meter_df, name = "Parking")
w2.add_data(dis_parking_df, name = "Disability Parking")
w2.save_to_html()