# -*- coding: utf-8 -*-
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union, cascaded_union, polygonize
from shapely.affinity import scale, translate, rotate

class GeoprocessingTools:
    """TOUS les outils de géotraitement QGIS"""
    
    @staticmethod
    def buffer(gdf, distance, dissolve=False, end_cap_style='round', join_style='round'):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.buffer(distance, cap_style=2 if end_cap_style=='square' else 1, join_style=1)
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
    def symmetric_difference(gdf1, gdf2):
        return gpd.overlay(gdf1, gdf2, how='symmetric_difference')
    
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
    def dissolve(gdf, by=None, aggfunc='first'):
        return gdf.dissolve(by=by, aggfunc=aggfunc) if by else gdf.dissolve()
    
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
    def envelope(gdf):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.envelope
        return result
    
    @staticmethod
    def simplify(gdf, tolerance, preserve_topology=True):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=preserve_topology)
        return result
    
    @staticmethod
    def boundary(gdf):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.boundary
        return result
    
    @staticmethod
    def node(gdf):
        """Extrait les nœuds (points d'intersection)"""
        lines = unary_union(gdf.geometry)
        points = []
        for geom in lines.geoms if hasattr(lines, 'geoms') else [lines]:
            coords = list(geom.coords)
            points.extend([Point(c) for c in coords])
        return gpd.GeoDataFrame(geometry=points, crs=gdf.crs)
    
    @staticmethod
    def explode(gdf):
        """Explose les multi-géométries"""
        return gdf.explode(index_parts=True).reset_index(drop=True)
    
    @staticmethod
    def collect(gdf):
        """Collecte en multi-géométrie"""
        return unary_union(gdf.geometry)
    
    @staticmethod
    def rotate(gdf, angle, origin='center'):
        result = gdf.copy()
        if origin == 'center':
            centroid = unary_union(gdf.geometry).centroid
            result['geometry'] = gdf.geometry.rotate(angle, origin=centroid)
        else:
            result['geometry'] = gdf.geometry.rotate(angle, origin=origin)
        return result
    
    @staticmethod
    def scale(gdf, xfact, yfact, origin='center'):
        result = gdf.copy()
        if origin == 'center':
            centroid = unary_union(gdf.geometry).centroid
            result['geometry'] = gdf.geometry.scale(xfact, yfact, origin=centroid)
        else:
            result['geometry'] = gdf.geometry.scale(xfact, yfact, origin=origin)
        return result
    
    @staticmethod
    def translate(gdf, xoff, yoff):
        result = gdf.copy()
        result['geometry'] = gdf.geometry.translate(xoff, yoff)
        return result
