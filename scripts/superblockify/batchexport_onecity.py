"""
Script for creating superblockify results for one city.

Parameters
----------
city_id : str
    ID of the city

Notes
-------
Exports data into two gpkg files.

Examples
--------
>>> python batchexport_onecity.py frederiksberg_dk "Frederiksberg Municipality"
"""

# Main
import superblockify as sb
import sys
import os
import traceback

sb.config.set_log_level("ERROR")

# Variables
city_id = "frederiksberg_dk"
city_query = "Frederiksberg Municipality"

# Variables for batch export
datestring = ""
export_status = False

# Assign inputs to variables
if len(sys.argv) >= 2:
    city_id = sys.argv[1]
if len(sys.argv) >= 3:
    city_query = sys.argv[2]

# The 4th argument (date of export) is given when there is a batch export for more than 1 city
# -> the files are always checked and the information is always logged into .txt files
if len(sys.argv) >= 4: 
    check_files = True 
    datestring = sys.argv[3]
    export_status = True
    STATUS_FILE = f"{datestring}/export_status.txt"
    ERROR_LOG = f"{datestring}/error_log.txt"

try:
    print(city_id + ", residential")
    part = sb.ResidentialPartitioner(
        name=city_id,
        city_name=city_id,
        search_str=city_query,
        unit="time",
    )
    part.run(
        calculate_metrics=True,  # set to False if you are not interested in metrics
        make_plots=False,  # set to False if you are not interested in plots
        replace_max_speeds=False,  # set to true to overwrite the OSM speed limits
        # -> with 15 km/h inside Superblocks and 50 km/h outside
        # If the approach has specific parameters, you can set them here
    )
    sb.save_to_gpkg(part, save_path="./results/"+city_id+"_residential.gpkg")

    print(city_id + ", betweenness")
    part = sb.BetweennessPartitioner(
        name=city_id,
        city_name=city_id,
        search_str=city_query,
        unit="time",
    )
    part.run(
        calculate_metrics=True,  # set to False if you are not interested in metrics
        make_plots=False,  # set to False if you are not interested in plots
        replace_max_speeds=False,  # set to true to overwrite the OSM speed limits
        # -> with 15 km/h inside Superblocks and 50 km/h outside
        # If the approach has specific parameters, you can set them here
    )
    sb.save_to_gpkg(part, save_path="./results/"+city_id+"_betweenness.gpkg")

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
    

