"""
Script for exporting some fixbikenet data for one city.

Parameters
----------
city_id : str
    ID of the city

Notes
-------
Exports data into 4 files.

Examples
--------
>>> python batchexport_onecity.py frederiksberg_dk
"""

# Main
import fixbikenet as fbn
import sys
from fixbikenet import settings
import os
import traceback

# Settings
settings.import_path = '../../cities/cityexport/'
settings.export_file_format = "geojson"

# Variables
city_id = "frederiksberg_dk"

# Variables for batch export
datestring = ""
export_status = False

# Assign inputs to variables
if len(sys.argv) >= 2:
    city_id = sys.argv[1]

# The 3rd argument (date of export) is given when there is a batch export for more than 1 city
# -> the files are always checked and the information is always logged into .txt files
if len(sys.argv) >= 3: 
    check_files = True 
    datestring = sys.argv[2]
    export_status = True
    STATUS_FILE = f"{datestring}/export_status.txt"
    ERROR_LOG = f"{datestring}/error_log.txt"

try:
    fbn.fixbikenet(
        city_id,
        import_files = {
            'city_boundary': 'boundaries/'+city_id+'.geojson',
            'street_network': 'streetbike_networks/'+city_id+'.gpkg',
        },
    )

    if export_status:
        with open(STATUS_FILE, "a", encoding="utf-8") as f:
            f.write("\t\t".join(str(x) for x in [city_id, "✅"])+ "\n")

except Exception as e:
    status_error = f"{type(e).__name__}: {e}"
    traceback_error = traceback.format_exc()
    if export_status:
        with open(STATUS_FILE, "a", encoding="utf-8") as f:
            f.write("\t\t".join(str(x) for x in [city_id])+ "\n")
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write("\t\t".join(str(x) for x in [city_id])+ "\n")
    else:
        print(f"{status_error}")
        print(traceback_error)
    

