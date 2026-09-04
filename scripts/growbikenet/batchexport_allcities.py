"""
Script for exporting some growbikenet data for multiple cities.
"""

import pandas as pd
import os
from growbikenet.functions import slugify
import subprocess
import time
import numpy as np
import datetime

# Import the list of cities
df = pd.read_csv('../../cities/meta/cities.csv', 
                   sep = ';',)


# Get date and hour to use for .txt files
date = datetime.datetime.now()
datestring = date.strftime("%Y%m%d_%H%M%S")


# Create export_status.txt and error_log.txt files
os.makedirs(f"./{datestring}", exist_ok=True)
STATUS_FILE = f"{datestring}/export_status.txt"
with open(STATUS_FILE, "w", encoding="utf-8") as f:
    f.write("city_query\t\tcity_name\t\tordering\t\texisting_network_spacing\t\tseed_point_type\t\tstatus\n")

ERROR_LOG = f"{datestring}/error_log.txt"
with open(ERROR_LOG, "w", encoding="utf-8") as f:
    f.write("city_query\t\tcity_name\t\tordering\t\texisting_network_spacing\t\tseed_point_type\t\ttraceback\n")


# Define function to run batchexport_onecity.py
def export_onecity(city_query, city_id, boundary_file):
    """
    Run batchexport_onecity.py, with suprocess in 'return' mode
    """

    args = [
        "python",
        "batchexport_onecity.py",
        city_query,
        city_id,
        "geojson",
        f"../../cities/cityexport/boundaries/{city_id}.{boundary_file}",
        f"../../cities/cityexport/growable_networks/{city_id}.gpkg",
        f"../../cities/cityexport/bike_networks/{city_id}.gpkg",
        f"../../cities/cityexport/rail_stations/{city_id}.gpkg",
        f"../../cities/cityexport/schools/{city_id}.gpkg",
        "True",
        datestring
    ]

    logs = subprocess.run(
        args,
        text = True
    )

# Get start time for calculating running time
start = time.time()


# Run the loop for all cities
for nominatimstring, city_name, country_code in zip(list(df.nominatim_query), list(df.name_en), list(df.country_code)):
    city_id = slugify(city_name)+"_"+slugify(country_code)
    if type(nominatimstring) is str:
        export_onecity(
            nominatimstring,
            city_id,
            "geojson"
        )
        
    else: # No entry is a nan in a df. Here we need to use a shape file. It must be in the folder cities/boundaries
        if os.path.isfile("../../cities/cityexport/boundaries/"+city_id+".geojson"):
            export_onecity(
                city_name, 
                city_id,
                "geojson"
            )
        else:
            export_onecity(
                city_name, 
                city_id,
                "shp"
            )
    print()


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