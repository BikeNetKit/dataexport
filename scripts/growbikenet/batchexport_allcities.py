"""
Script for exporting some growbikenet data for multiple cities.
"""

import pandas as pd
import os
from slugify import slugify

df = pd.read_csv('./cities/european_capitalsand100000pop.csv', 
                   sep = ';',)

for nominatimstring, city_name in zip(list(df.nominatim_query), list(df.name_en)):
    if type(nominatimstring) is str:
        os.system("python ./scripts/growbikenet/batchexport_onecity.py '"+nominatimstring+"' '"+city_name+"'")
    else: # No entry is a nan in a df. Here we need to use a shape file. It must be in the folder cities/
        os.system("python ./scripts/growbikenet/batchexport_onecity.py '"+city_name+"' '"+city_name+"'"+" geojson "+"'./cities/"+slugify(city_name)+".shp'")

