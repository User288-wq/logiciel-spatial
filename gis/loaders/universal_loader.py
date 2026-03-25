# -*- coding: utf-8 -*-
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

class UniversalLoader:
    VECTOR_FORMATS = ['.shp', '.geojson', '.json', '.kml', '.kmz', '.gpkg', '.gpx', '.csv']
    
    @staticmethod
    def load(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.shp', '.geojson', '.json', '.gpkg']:
            return gpd.read_file(file_path)
        elif ext in ['.kml', '.kmz']:
            return gpd.read_file(file_path, driver='KML')
        elif ext == '.gpx':
            gdf = gpd.read_file(file_path, driver='GPX', layer='tracks')
            if gdf.empty:
                gdf = gpd.read_file(file_path, driver='GPX', layer='points')
            return gdf
        elif ext == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8')
            lat_col = next((c for c in df.columns if c.lower() in ['lat','latitude','y']), None)
            lon_col = next((c for c in df.columns if c.lower() in ['lon','longitude','x']), None)
            if lat_col and lon_col:
                geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
                return gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            return df
        raise Exception(f"Format non supporté: {ext}")

loader = UniversalLoader()
