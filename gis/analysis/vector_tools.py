# -*- coding: utf-8 -*-
import geopandas as gpd
import pandas as pd

class VectorTools:
    """Outils vectoriels QGIS"""
    
    @staticmethod
    def merge_layers(gdf_list):
        return pd.concat(gdf_list, ignore_index=True)
    
    @staticmethod
    def reproject(gdf, target_crs):
        return gdf.to_crs(target_crs)
    
    @staticmethod
    def extract_by_attribute(gdf, field, value, operator='='):
        if operator == '=': return gdf[gdf[field] == value]
        elif operator == '!=': return gdf[gdf[field] != value]
        elif operator == '>': return gdf[gdf[field] > value]
        elif operator == '<': return gdf[gdf[field] < value]
        elif operator == '>=': return gdf[gdf[field] >= value]
        elif operator == '<=': return gdf[gdf[field] <= value]
        elif operator == 'like': return gdf[gdf[field].str.contains(value, na=False)]
        return gdf
    
    @staticmethod
    def extract_by_location(gdf, mask, predicate='intersects'):
        if predicate == 'intersects':
            return gdf[gdf.geometry.intersects(unary_union(mask.geometry))]
        elif predicate == 'contains':
            return gdf[gdf.geometry.contains(unary_union(mask.geometry))]
        elif predicate == 'within':
            return gdf[gdf.geometry.within(unary_union(mask.geometry))]
        return gdf
    
    @staticmethod
    def select_by_expression(gdf, expression):
        return gdf.query(expression)
    
    @staticmethod
    def add_field(gdf, field_name, field_type='string', default_value=None):
        gdf = gdf.copy()
        if field_type == 'int':
            gdf[field_name] = default_value if default_value else 0
        elif field_type == 'float':
            gdf[field_name] = default_value if default_value else 0.0
        else:
            gdf[field_name] = default_value if default_value else ''
        return gdf
    
    @staticmethod
    def delete_field(gdf, field_name):
        return gdf.drop(columns=[field_name])
    
    @staticmethod
    def rename_field(gdf, old_name, new_name):
        return gdf.rename(columns={old_name: new_name})
    
    @staticmethod
    def calculate_field(gdf, field_name, expression):
        gdf = gdf.copy()
        gdf[field_name] = gdf.eval(expression)
        return gdf
    
    @staticmethod
    def join_by_attribute(gdf1, gdf2, left_field, right_field, how='left'):
        return gdf1.merge(gdf2, left_on=left_field, right_on=right_field, how=how)
    
    @staticmethod
    def join_by_location(gdf1, gdf2, predicate='intersects', how='inner'):
        return gpd.sjoin(gdf1, gdf2, how=how, predicate=predicate)
    
    @staticmethod
    def fix_geometries(gdf):
        from shapely.validation import make_valid
        gdf = gdf.copy()
        gdf['geometry'] = gdf.geometry.apply(lambda g: make_valid(g) if not g.is_valid else g)
        return gdf
    
    @staticmethod
    def remove_duplicates(gdf):
        return gdf.drop_duplicates()
    
    @staticmethod
    def sort_by_field(gdf, field, ascending=True):
        return gdf.sort_values(by=field, ascending=ascending)
