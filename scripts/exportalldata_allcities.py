import pandas as pd
import os

df = pd.read_csv('./cities/european_capitals.csv', 
                   sep = ';',)

for nominatimstring in list(df.nominatim_query):
    if type(nominatimstring) is str:
        os.system("python ./scripts/exportalldata_onecity.py "+nominatimstring)
