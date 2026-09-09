"""
Script for splitting up cities for paralellized sb exports.
"""

import pandas as pd
import os

# Import the list of cities
df = pd.read_csv('../../cities/meta/cities.csv', 
                   sep = ';',)

# Exclude already done cities
city_ids_done = {'rome_it': "Rome"}
for f in os.listdir("../../dataexports/latest/superblockify_gpkg"):
    cityname = f.split("_", 1)[0]
    city_ids_done[df.loc[df["name_en"] == cityname, "cityid"].iloc[0]] = cityname
for f in os.listdir("./results"):
    if not f.startswith('.'):
        cid = f.split("_", 2)[0]+"_"+f.split("_", 2)[1]
        city_ids_done[cid] = df.loc[df["cityid"] == cid, "name_en"].iloc[0]

df.sort_values(by=['population'], ascending=False, inplace=True)
df = df[~df['cityid'].isin(city_ids_done)]

df.iloc[0::2].to_csv("cities_manuel.csv", sep = ';', index=False)
df.iloc[1::2].to_csv("cities_michael.csv", sep = ';', index=False)