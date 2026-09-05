"""
Script for exporting some fixbikenet data for multiple cities.
"""

import pandas as pd
import os
from fixbikenet.functions import slugify
from fixbikenet import settings
import subprocess
import time
import numpy as np
import datetime
import fixbikenet as fbn

print("fixbikenet version: "+fbn.__version__)

settings.silent = True

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
    f.write("cityid\t\tstatus\n")

ERROR_LOG = f"{datestring}/error_log.txt"
with open(ERROR_LOG, "w", encoding="utf-8") as f:
    f.write("cityid\t\ttraceback\n")


# Define function to run batchexport_onecity.py
def export_onecity(city_id):
    """
    Run batchexport_onecity.py, with suprocess in 'return' mode
    """

    args = [
        "python",
        "batchexport_onecity.py",
        city_id,
        datestring
    ]

    logs = subprocess.run(
        args,
        text = True
    )

# Get start time for calculating running time
start = time.time()


# Run the loop for all cities
for city_id in list(df.cityid):
    print(city_id)
    export_onecity(city_id)


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

print("afterwards, run in the folder:")
print("rm *street*")
print("rm *kamenetspodolsky*")
print("rm *soligorsk*")
print("rm *makijivka*")
print("rm *horlivka*")
print("rm *alchevsk*")
