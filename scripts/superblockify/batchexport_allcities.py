"""
Script for exporting some fixbikenet data for multiple cities.
"""

import pandas as pd
import os
import subprocess
import time
import numpy as np
import datetime
import superblockify as sb
from time import sleep

print("superblockify version: "+sb.__version__)

# Import the list of cities
# df = pd.read_csv('../../cities/meta/cities.csv', sep = ';')
df = pd.read_csv('cities_manuel.csv', sep = ';')


# Get date and hour to use for .txt files
date = datetime.datetime.now()
datestring = date.strftime("%Y%m%d_%H%M%S")


# Create export_status.txt and error_log.txt files
os.makedirs(f"./{datestring}", exist_ok=True)
STATUS_FILE = f"{datestring}/export_status.txt"
with open(STATUS_FILE, "w", encoding="utf-8") as f:
    f.write("cityid\t\tstatus\n")

ERROR_LOG = f"{datestring}/error_log.txt"
with open(ERROR_LOG, "w", encoding="utf-8") as f:
    f.write("cityid\t\ttraceback\n")


# Define function to run batchexport_onecity.py
def export_onecity(city_id, city_query):
    """
    Run batchexport_onecity.py, with suprocess in 'return' mode
    """

    args = [
        "python",
        "batchexport_onecity.py",
        city_id,
        city_query,
        datestring
    ]

    logs = subprocess.run(
        args,
        text = True
    )

# Get start time for calculating running time
start = time.time()


# Exclude already done cities
city_ids_done = {}
# for f in os.listdir("../../dataexports/latest/superblockify_gpkg"):
#     cityname = f.split("_", 1)[0]
#     city_ids_done[df.loc[df["name_en"] == cityname, "cityid"].iloc[0]] = cityname
for f in os.listdir("./results"):
    if not f.startswith('.'):
        cid = f.split("_", 2)[0]+"_"+f.split("_", 2)[1]
        try:
            city_ids_done[cid] = df.loc[df["cityid"] == cid, "name_en"].iloc[0]
        except:
            pass

# Run the loop for all cities
for city_id, city_query in zip(list(df.cityid), list(df.nominatim_query)):
    if city_id not in city_ids_done:
        print(city_id)
        export_onecity(str(city_id), str(city_query))
        sleep(1200)


# Calculate running time
end = time.time()
running_time = end - start

days = int(running_time/(24*60*60))
hours = int((running_time - days * (24*60*60)) / (60*60))
minutes = int((running_time - days * (24*60*60) - hours * (60*60)) / (60))
seconds = round(running_time - days * (24*60*60) - hours * (60*60) - minutes * 60, 2)

with open(STATUS_FILE, "a", encoding="utf-8") as f:
    f.write(f"TOTAL RUNNING TIME: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")


# Create environment.yaml
subprocess.run(
        f'conda env export --no-builds | grep -v "^prefix: " > {datestring}/environment.yaml',
        shell = True,
        text = True
    )
