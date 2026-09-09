"""
Script for sb execution with local imports.
DOES NOT WORK.
"""

import superblockify as sb
import geopandas as gpd
import osmnx as ox
sb.config.set_log_level("DEBUG")


# The following adapted from https://github.com/BikeNetKit/superblockify/pull/128
from networkx import Graph, is_isomorphic, set_node_attributes, set_edge_attributes, MultiDiGraph
from superblockify.population.tessellation import add_edge_cells
from superblockify.population.approximation import add_edge_population
from superblockify.graph_stats import basic_graph_stats

def preprocess_graph(G: MultiDiGraph, boundary_buffer_dist: float = 100) -> MultiDiGraph:
    """Preprocesses a graph for use with a partitioner.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The graph to preprocess.
    boundary_buffer_dist : float, optional
        The buffer distance to create the boundary around the graph, by default 200 meters.
        
    Returns
    -------
    networkx.MultiDiGraph
        The preprocessed graph.
    """

    # Add edge bearings    
    G = ox.add_edge_bearings(G)    

    # Checks if the graph is projected, if not it projects it to the local UTM.
    if not ox.projection.is_projected(G.graph["crs"]):
        G = ox.project_graph(G)
    
    # A geodataframe is created from the projected graph for extracting the
    # boundary of the graph. And, if missing, extract the lenghts of the geometies 
    edges_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
    names_attribute = edges_gdf.columns

    # Checks if the lenght is missing, e.g. the graph was not created with osmnx, and adds it if necessary
    if "length" not in names_attribute:
        logger.warning(
            "Length attribute is not present in the graph. Calculating lengths from geometry."
        )
        edges_lengths = edges_gdf.geometry.length
        set_edge_attributes(G, edges_lengths.to_dict(), name="length")

    # Checks if the maxspeed attribute is missing, e.g. this is not a graph from OSM data.
    # Adds a default maxspeed of 30 km/h if it is missing, as this is needed for calculating
    # travel times. 
    if "maxspeed" not in names_attribute:
        logger.warning(
            "maxspeed attribute is not present in the graph. Global max speeds are going to be set to 30 km/h."
        )
        set_edge_attributes(G, 30, name="maxspeed")

    # Add speeds and travel times using  osmnx 
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    

    # Create a convex hull of the graph to calculate the area and set the boundary for saving the graph.
    # This is implemented with an if statement to support older versions of geopandas < 1.0.0 
    if hasattr(edges_gdf.geometry, "union_all"):
        edge_union = edges_gdf.geometry.union_all()
    else:
        edge_union = edges_gdf.geometry.unary_union

    # A convex hull is created arround the bufferred edges.
    enclosing_hull = edge_union.convex_hull.buffer(boundary_buffer_dist)
    
    # Assigning the attributes to the graph
    G.graph.update(basic_graph_stats(G, area=enclosing_hull.area))
    G.graph["area"] = enclosing_hull.area
    G.graph['boundary'] = enclosing_hull

    # Adding the edge population data
    add_edge_population(G)

    # Adding tessellation cells to edges
    add_edge_cells(G)

    return G


print("start")
import_path = "../../cities/cityexport/streetbike_networks/"
nodes = gpd.read_file(import_path+"frederiksberg_dk.gpkg", layer='nodes')
edges = gpd.read_file(import_path+"frederiksberg_dk.gpkg", layer='edges')
nodes = nodes.set_index(['osmid'])
edges = edges.set_index(['u', 'v', 'key'])
g = ox.convert.graph_from_gdfs(nodes, edges)
print("loaded")
G_processed = preprocess_graph(g)
print("preprocessed")

part = sb.ResidentialPartitioner(
	name="Frederiksberg",
	city_name="Frederiksberg",
	search_str=None,
	graph=G_processed,
	unit="time",  # "time", "distance", any other edge attribute, or None to count edges
)

