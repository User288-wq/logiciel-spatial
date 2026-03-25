# -*- coding: utf-8 -*-
import pyproj
from pyproj import CRS, Transformer
import geopandas as gpd

class CRSManager:
    """Gestionnaire de projections comme QGIS"""
    
    PROJECTIONS = {
        'EPSG:4326': {'name': 'WGS 84', 'area': 'Monde', 'type': 'Geographic'},
        'EPSG:3857': {'name': 'Web Mercator', 'area': 'Monde', 'type': 'Projected'},
        'EPSG:2154': {'name': 'RGF93 / Lambert-93', 'area': 'France', 'type': 'Projected'},
        'EPSG:27572': {'name': 'NTF / Lambert zone II', 'area': 'France', 'type': 'Projected'},
        'EPSG:32628': {'name': 'WGS 84 / UTM 28N', 'area': 'Senegal Ouest', 'type': 'Projected'},
        'EPSG:32629': {'name': 'WGS 84 / UTM 29N', 'area': 'Senegal Est', 'type': 'Projected'},
        'EPSG:32728': {'name': 'WGS 84 / UTM 28S', 'area': 'Afrique Sud', 'type': 'Projected'},
        'EPSG:31370': {'name': 'Belgian Lambert 72', 'area': 'Belgique', 'type': 'Projected'},
        'EPSG:2056': {'name': 'CH1903+ / LV95', 'area': 'Suisse', 'type': 'Projected'},
        'EPSG:3347': {'name': 'Canada Lambert', 'area': 'Canada', 'type': 'Projected'},
        'EPSG:4269': {'name': 'NAD83', 'area': 'USA', 'type': 'Geographic'},
        'EPSG:27700': {'name': 'British National Grid', 'area': 'UK', 'type': 'Projected'},
        'EPSG:25832': {'name': 'ETRS89 / UTM 32N', 'area': 'Allemagne', 'type': 'Projected'},
        'EPSG:3395': {'name': 'World Mercator', 'area': 'Monde', 'type': 'Projected'},
    }
    
    def __init__(self):
        self.current = 'EPSG:4326'
    
    def get_info(self, epsg):
        if epsg in self.PROJECTIONS:
            return self.PROJECTIONS[epsg]
        return {'name': epsg, 'area': 'Inconnu', 'type': 'Inconnu'}
    
    def get_all(self):
        """Retourne la liste de toutes les projections"""
        result = []
        for epsg, info in self.PROJECTIONS.items():
            result.append((epsg, info['name'], info['area']))
        return result
    
    def transform(self, gdf, target_epsg):
        try:
            return gdf.to_crs(target_epsg)
        except Exception as e:
            print(f"Erreur reprojection: {e}")
            return gdf
    
    def get_utm_for_point(self, lon, lat):
        zone = int((lon + 180) / 6) + 1
        return f'EPSG:326{zone:02d}' if lat >= 0 else f'EPSG:327{zone:02d}'

crs_manager = CRSManager()
