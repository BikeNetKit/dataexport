"""
Script for exporting some growbikenet data for one city.

Parameters
----------
city_query : str
    Search string for the city that the analysis should be performed on. This is the query used to fetch the data from nominatim. Overruled for data fetching if city_boundary or street_network is set.
city_name : str, default None
    If set, the slugified city_name is used as the filename of the data export. For example, "Athens" will use "athens" in filenames. If set to None, the slugified city_query is used as the filename of the data export. It is useful to set city_name for cities where the city_query is not the city name, for example "Municipality of Athens" vs "Athens".
export_file_format : str, default "geojson"
    File format for the data export. Default "geojson", also possible "gpkg". If exporting as geojson, generates extra files for seed points and city boundary. If exporting as gkpg, these are added all in one file as extra layers.
city_boundary : (str | None), default None
    If not set to None, the study area will be selected from the (Multi)Polygon provided in the city_boundary gpkg file, ideally in unprojected latitude-longitude degrees (EPSG:4326), but EPSG:3857 also works.
street_network : str
    The street network is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that an undirected osmnx street network g has after saved via ox.io.save_graph_geopackage().
bike_network : str
    The existing bike network is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326 with layers nodes and edges, with the structure that an undirected osmnx bike network has after saved via ox.io.save_graph_geopackage().
rail_stations : str 
    The list of rail stations is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326.
schools : str | None, default None
    The list of schools is loaded from this file. Must be a gpkg file in unprojected crs EPSG:4326.
check_files : bool, default False
    If set to False, data is exported regardless if there is already a file with the same name in the "./results" directory

Notes
-------
Exports data into 12 files:
[slug]-growbikenet-[ordering]-[exist_nw]-[seed_point_type].geojson
    Data is saved into the current working directory.
        [slug] is a string id created out of city_name.
        [ordering] is 'betweenness' or 'closeness'.
        [exist_nw] is 'from_scratch' or 'from_bikenw'.
        [seed_point_type] is 'grid_(square|triangle)', 'rail' or 'school'.

Examples
--------
>>> python batchexport_onecity.py Barcelona Barcelona_es geojson ../../cities/cityexport/boundaries/barcelona_es.geojson ../../cities/cityexport/growable_networks/barcelona_es.gpkg ../../cities/cityexport/bike_networks/barcelona_es.gpkg ../../cities/cityexport/rail_stations/barcelona_es.gpkg ../../cities/cityexport/schools/barcelona_es.gpkg False
"""



# WHICH DATA TO EXPORT?
export_seed_point_types = ['auto', 'rail', 'school'] # Full array: ['auto', 'rail', 'school']
export_orderings = ['betweenness', 'closeness'] # Full array: ['betweenness', 'closeness', 'random']
export_existing_network_spacings = [None, 'auto'] # Full array: [None, 'auto']

# Main
import growbikenet as gbn
import sys
from growbikenet.functions import slugify
from growbikenet import settings
from growbikenet import constants
import os
import traceback
import re

# Variables
city_query = "Badalona"
city_name = "badalona_es"
settings.export_file_format = "geojson"
constants._CRS_CALCULATIONS = 'auto'
city_boundary = "../../cities/cityexport/boundaries/badalona_es.geojson"
growable_network = "../../cities/cityexport/growable_networks/badalona_es.gpkg"
bike_network = "../../cities/cityexport/bike_networks/badalona_es.gpkg"
rail_stations = "../../cities/cityexport/rail_stations/badalona_es.gpkg"
schools = "../../cities/cityexport/schools/badalona_es.gpkg"
check_files = False

# Variables for batch export
datestring = ""
export_status = False

# Assign inputs to variables
if len(sys.argv) >= 2:
    city_query = sys.argv[1]
if len(sys.argv) >= 3:
    city_name = sys.argv[2]
if len(sys.argv) >= 4:
    settings.export_file_format = sys.argv[3]
if len(sys.argv) >= 5:
    city_boundary = sys.argv[4]
if len(sys.argv) >= 6:
    growable_network = sys.argv[5]
if len(sys.argv) >= 7:
    bike_network = sys.argv[6]
if len(sys.argv) >= 8:
    rail_stations = sys.argv[7]
if len(sys.argv) >= 9:
    schools = sys.argv[8]
if len(sys.argv) >= 10:
    check_files = sys.argv[9]

# The 11th argument (date of export) is given when there is a batch export for more than 1 city
# -> the files are always checked and the information is always logged into .txt files
if len(sys.argv) >= 11: 
    check_files = True 
    datestring = sys.argv[10]
    export_status = True
    STATUS_FILE = f"{datestring}/export_status.txt"
    ERROR_LOG = f"{datestring}/error_log.txt"


# Retrieve the list of already generated files
if check_files == True:
    results_dir = "./results"
    if os.path.exists(results_dir):
        files = sorted(os.listdir(os.fsencode(results_dir)))
        generated_files = [os.fsdecode(file) for file in files]
    else:
        generated_files = []


# Initialise city_name and import_files
city_name = slugify(city_name)
import_files={"city_boundary": city_boundary, "growable_network": growable_network}

for seed_point_type in export_seed_point_types: # [auto, rail , school]

    # Adjust the input and name of [seed_point_type]
    if seed_point_type == 'auto':
        seed_point_type_input = 'auto'
        import_files.pop('seed_points', None)
    elif seed_point_type == 'rail':
        seed_point_type_input = 'file'
        settings.seed_point_type_name = 'rail'
        import_files['seed_points'] = rail_stations
    elif seed_point_type == 'school':
        seed_point_type_input = 'file'
        settings.seed_point_type_name = 'school'
        import_files['seed_points'] = schools


    for ordering in export_orderings: # [betweenness, closeness]

        for existing_network_spacing in export_existing_network_spacings: # [None, auto]

            if seed_point_type == 'auto' and existing_network_spacing == 'auto':
                seed_point_linking = 'triangulate_delaunay'
            else:
                seed_point_linking = 'auto'


            # Determine the name of [exnw_string] and if to include the bike_network
            if existing_network_spacing:
                exnw_string = "from_bikenw"
                import_files['bike_network'] = bike_network
            else:
                exnw_string = "from_scratch"
                import_files.pop('bike_network', None)


            # Check if there is already a file for this setup (if check_file is True)
            if check_files == True:
                if seed_point_type == "auto":
                    pattern = re.compile(
                        rf"{re.escape(city_name)}-growbikenet-{re.escape(ordering)}-"
                        rf"{re.escape(exnw_string)}-grid_(square|triangle)\.{re.escape(settings.export_file_format)}"
                    )
                    found_file = any(pattern.fullmatch(f) for f in generated_files)
                else:
                    fname = f"{city_name}-growbikenet-{ordering}-{exnw_string}-{seed_point_type}.{settings.export_file_format}"
                    found_file = fname in generated_files
            else:
                found_file = False
            


            if found_file:
                print(f"Found file for: {city_name}, {ordering}, {exnw_string}, {seed_point_type}")
                if export_status:
                    with open(STATUS_FILE, "a", encoding="utf-8") as f:
                        f.write("\t\t".join(str(x) for x in [city_query, city_name, ordering, existing_network_spacing, seed_point_type, "✅"]) + "\n")

            else:
                print(f"No file for: {city_name}, {ordering}, {exnw_string}, {seed_point_type}")

                try:
                    constants._CRS_CALCULATIONS = 'auto'
                    gbn.growbikenet(
                        city_query,
                        ordering=ordering,
                        seed_point_type=seed_point_type_input,
                        seed_point_linking=seed_point_linking,
                        export_data=True,
                        export_plots=False,
                        existing_network_spacing=existing_network_spacing,
                        city_id=city_name,
                        import_files=import_files,
                    )
                    if export_status:
                        with open(STATUS_FILE, "a", encoding="utf-8") as f:
                            f.write("\t\t".join(str(x) for x in [city_query, city_name, ordering, existing_network_spacing, seed_point_type, "✅"])+ "\n")

                except Exception as e:
                    status_error = f"{type(e).__name__}: {e}"
                    traceback_error = traceback.format_exc()
                    if export_status:
                        with open(STATUS_FILE, "a", encoding="utf-8") as f:
                            f.write("\t\t".join(str(x) for x in [city_query, city_name, ordering, existing_network_spacing, seed_point_type, status_error])+ "\n")
                        with open(ERROR_LOG, "a", encoding="utf-8") as f:
                            f.write("\t\t".join(str(x) for x in [city_query, city_name, ordering, existing_network_spacing, seed_point_type, traceback_error])+ "\n")
                    else:
                        print(f"{status_error}")
                        print(traceback_error)
    

# Temporary hack to replace generated with real city boundary
# For cities that have only shape files like Copenhagen, this does not work!
import shutil
shutil.copyfile(city_boundary, "./results/"+city_name+"-city_boundary.geojson")

