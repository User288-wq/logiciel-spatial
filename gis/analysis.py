# -*- coding: utf-8 -*-
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union

class GeoprocessingTools:
    """Outils de géotraitement (comme QGIS)"""
    
    @staticmethod
    def buffer(gdf, distance, dissolve=False):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.buffer(distance)
        if dissolve:
            dissolved = unary_union(result.geometry)
            result = gpd.GeoDataFrame({'id': [0], 'geometry': [dissolved]}, crs=gdf.crs)
        return result
    
    @staticmethod
    def intersect(gdf1, gdf2):
        return gpd.overlay(gdf1, gdf2, how='intersection')
    
    @staticmethod
    def union(gdf1, gdf2):
        return gpd.overlay(gdf1, gdf2, how='union')
    
    @staticmethod
    def difference(gdf1, gdf2):
        return gpd.overlay(gdf1, gdf2, how='difference')
    
    @staticmethod
    def clip(gdf, mask):
        if isinstance(mask, gpd.GeoDataFrame):
            mask_geom = unary_union(mask.geometry)
        else:
            mask_geom = mask
        clipped = gdf[gdf.geometry.intersects(mask_geom)].copy()
        clipped['geometry'] = clipped.geometry.intersection(mask_geom)
        return clipped[~clipped.geometry.is_empty]
    
    @staticmethod
    def dissolve(gdf, by=None):
        return gdf.dissolve(by=by) if by else gdf.dissolve()
    
    @staticmethod
    def centroid(gdf):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.centroid
        return result
    
    @staticmethod
    def convex_hull(gdf):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.convex_hull
        return result
    
    @staticmethod
    def bounding_box(gdf):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.envelope
        return result
    
    @staticmethod
    def simplify(gdf, tolerance):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.simplify(tolerance)
        return result

class AnalysisTools:
    """Outils d'analyse spatiale"""
    
    @staticmethod
    def nearest_neighbor(gdf1, gdf2, k=1):
        from scipy.spatial import KDTree
        points1 = np.array([(p.x, p.y) for p in gdf1.geometry.centroid])
        points2 = np.array([(p.x, p.y) for p in gdf2.geometry.centroid])
        tree = KDTree(points2)
        return tree.query(points1, k=k)
    
    @staticmethod
    def count_points_in_polygon(points_gdf, polygons_gdf):
        result = polygons_gdf.copy()
        result['point_count'] = 0
        for idx, polygon in polygons_gdf.iterrows():
            count = points_gdf[points_gdf.geometry.within(polygon.geometry)].shape[0]
            result.at[idx, 'point_count'] = count
        return result
    
    @staticmethod
    def heatmap(points_gdf, cell_size=0.01, radius=0.05):
        bounds = points_gdf.total_bounds
        xmin, ymin, xmax, ymax = bounds
        x_cells = int((xmax - xmin) / cell_size)
        y_cells = int((ymax - ymin) / cell_size)
        heatmap_data = []
        for i in range(x_cells):
            for j in range(y_cells):
                x = xmin + i * cell_size + cell_size/2
                y = ymin + j * cell_size + cell_size/2
                point = Point(x, y)
                count = points_gdf[points_gdf.geometry.distance(point) <= radius].shape[0]
                if count > 0:
                    heatmap_data.append({'x': x, 'y': y, 'intensity': count, 'geometry': point})
        return gpd.GeoDataFrame(heatmap_data, crs=points_gdf.crs)
    
    @staticmethod
    def calculate_area(gdf):
        gdf = gdf.copy()
        gdf['area'] = gdf.geometry.area
        return gdf
    
    @staticmethod
    def calculate_length(gdf):
        gdf = gdf.copy()
        gdf['length'] = gdf.geometry.length
        return gdf

class DataManagementTools:
    """Outils de gestion des données"""
    
    @staticmethod
    def merge_layers(gdf_list):
        return pd.concat(gdf_list, ignore_index=True)
    
    @staticmethod
    def reproject(gdf, target_crs):
        return gdf.to_crs(target_crs)
    
    @staticmethod
    def extract_by_attribute(gdf, field, value, operator='='):
        if operator == '=':
            return gdf[gdf[field] == value]
        elif operator == '!=':
            return gdf[gdf[field] != value]
        elif operator == '>':
            return gdf[gdf[field] > value]
        elif operator == '<':
            return gdf[gdf[field] < value]
        return gdf
    
    @staticmethod
    def add_field(gdf, field_name, default_value=None):
        gdf = gdf.copy()
        gdf[field_name] = default_value
        return gdf
    
    @staticmethod
    def drop_field(gdf, field_name):
        return gdf.drop(columns=[field_name])
