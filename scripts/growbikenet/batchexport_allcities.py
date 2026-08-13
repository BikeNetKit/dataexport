"""
Script for exporting some growbikenet data for multiple cities.
"""

import pandas as pd
import os
from growbikenet.functions import slugify

df = pd.read_csv('../../cities/european_capitalsand100000pop.csv', 
                   sep = ';',)

for nominatimstring, city_name, country_code in zip(list(df.nominatim_query), list(df.name_en), list(df.country_code)):
    city_id = slugify(city_name)+"_"+slugify(country_code)
    if type(nominatimstring) is str:
        os.system("python batchexport_onecity.py '"+nominatimstring+"' '"+city_id+"' geojson '../../cities/boundaries/"+city_id+".geojson' '../../cities/cityexport/street_networks/"+city_id+".gpkg' '../../cities/cityexport/bike_networks/"+city_id+".gpkg'")
    else: # No entry is a nan in a df. Here we need to use a shape file. It must be in the folder cities/
        os.system("python batchexport_onecity.py '"+city_name+"' '"+city_id+"' geojson '../../cities/boundaries/"+city_id+".geojson' '../../cities/cityexport/street_networks/"+city_id+".gpkg' '../../cities/cityexport/bike_networks/"+city_id+".gpkg'")