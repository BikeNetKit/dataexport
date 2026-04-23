import csv
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox
for custom_tag in ["cycleway", "bicycle", "cycleway:right", "cycleway:left", "cyclestreet"]:
    if custom_tag not in ox.settings.useful_tags_way:
        ox.settings.useful_tags_way.extend(custom_tag)
import shapely
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiLineString, MultiPolygon
import shapely.ops as ops
from shapely.prepared import prep
from itertools import combinations
from slugify import slugify

# Plotting
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.ticker import MaxNLocator



def prepare_network(nominatim_query, proj_crs='3857', network_type='all_public', custom_filter=None, shapefilename=None):
    """Download and prepare a street network from OSM via OSMnx

    Downloads a network with a given network_type and custom_filter using ox.graph_from_place.
    Then, stores the undirected OSM data in gdfs and projects using proj_crs.

    Parameters
    ----------
    nominatim_query : str
        Nominatim query for the city that the analysis should be performed on (usually its name), unless shapefile is not None.
    proj_crs : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator).
    network_type : {“all”, “all_public”, “bike”, “drive”, “drive_service”, “walk”}, default 'all_public'
        What type of street network to retrieve if custom_filter is None.
    custom_filter : (str | list[str] | None)
        A custom ways filter to be used instead of the network_type presets
    shapefile : str, default None
        The filename and path to a shape file of a polygon which is used to fetch the graph from. Overrides nominatim_query.

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected
    g_undir : networkx.classes.multigraph.MultiGraph
        Extracted networkX graph, undirected
    """
    # Fetch street network data from osmnx
    if shapefilename is None:
        g = ox.graph_from_place(
        nominatim_query, network_type=network_type, custom_filter=custom_filter, retain_all=True
        )
    else:
        shp = gpd.read_file(shapefilename)
        polygon = shp.iloc[0].geometry
        g = ox.graph_from_polygon(
        polygon, network_type=network_type, custom_filter=custom_filter, retain_all=True
        )
    g_undir = g.to_undirected().copy() # convert to undirected (dropping OSMnx keys!)

    # Export osmnx data to gdfs
    nodes, edges = nx_to_nodes_edges(g_undir, proj_crs)
    return nodes, edges, g_undir


def nx_to_nodes_edges(G, proj_crs='3857'):
    """Get nodes and projected edges from networkX graph

    Parameters
    ----------
    G : networkx.classes.multigraph.MultiGraph
        networkX graph, undirected
    proj_crs : str, default '3857'
        Coordinate reference system that is used to project osm data. Default is '3857' (WGS 84 / Pseudo-Mercator).

    Returns
    -------
    nodes : geopandas.geodataframe.GeoDataFrame
        Extracted OSM nodes, projected, osmid is index
    edges : geopandas.geodataframe.GeoDataFrame
        Extracted OSM edges, projected
    """
    nodes, edges = ox.graph_to_gdfs(
    G,
    nodes=True,
    edges=True,
    node_geometry=True,
    fill_edge_geometry=True
    )
    
    # Replace after dropping edges with key = 1
    edges = edges.loc[:,:,0].copy()
    # This also means we are dropping the "key" level from edge index (u,v,key becomes: u,v)

    # Project geometries of nodes, edges, seed points
    edges = edges.to_crs(proj_crs)
    nodes = nodes.to_crs(proj_crs)

    # Add osm ID as column to node gdf
    nodes["osmid"] = nodes.index
    return nodes, edges

def fill_holes(cov):
    """Fill holes (= shapely interiors) from a coverage Polygon or MultiPolygon
    """
    holeseq_per_poly = get_holes(cov)
    holes = []
    for hole_per_poly in holeseq_per_poly:
        for hole in hole_per_poly:
            holes.append(hole)
    eps = 0.00000001
    if isinstance(cov, shapely.geometry.multipolygon.MultiPolygon):
        cov_filled = ops.unary_union([poly for poly in cov] + [Polygon(hole).buffer(eps) for hole in holes])
    elif isinstance(cov, shapely.geometry.polygon.Polygon) and not cov.is_empty:
        cov_filled = ops.unary_union([cov] + [Polygon(hole).buffer(eps) for hole in holes])
    return cov_filled

def extract_relevant_polygon(placeid, mp):
    """Return the most relevant polygon of a multipolygon mp, for being considered the city limit.
    Depends on location.
    """
    if isinstance(mp, shapely.geometry.polygon.Polygon):
        return mp
    if placeid == "tokyo": # If Tokyo, take poly with most northern bound, otherwise largest
        p = max(mp.geoms, key=lambda a: a.bounds[-1])
    elif placeid == "reykjavik": # Southern part
        p = min(mp.geoms, key=lambda a: a.bounds[0])
    else:
        p = max(mp.geoms, key=lambda a: a.area)
    return p

def get_holes(cov):
    """Get holes (= shapely interiors) from a coverage Polygon or MultiPolygon
    """
    holes = []
    if isinstance(cov, shapely.geometry.multipolygon.MultiPolygon):
        for pol in cov.geoms: # cov is generally a MultiPolygon, so we iterate through its Polygons
            holes.append(pol.interiors)
    elif isinstance(cov, shapely.geometry.polygon.Polygon) and not cov.is_empty:
        holes.append(cov.interiors)
    return holes