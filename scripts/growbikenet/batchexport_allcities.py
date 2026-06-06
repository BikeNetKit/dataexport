"""
Script for exporting some growbikenet data for multiple cities.
"""

import pandas as pd
import os

df = pd.read_csv('./cities/european_capitals.csv', 
                   sep = ';',)

for nominatimstring, city_name in zip(list(df.nominatim_query), list(df.name_en)):
    if type(nominatimstring) is str:
        os.system("python ./scripts/growbikenet/batchexport_onecity.py '"+nominatimstring+"' "+city_name)
