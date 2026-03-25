# -*- coding: utf-8 -*-
import os
import requests
from io import BytesIO
from PIL import Image
import numpy as np

class BaseMapProvider:
    """TOUS les fonds de carte QGIS"""
    
    MAPS = {
        # OpenStreetMap
        'OpenStreetMap': {'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'name': 'OpenStreetMap', 'icon': '🗺️'},
        'OpenStreetMap_HOT': {'url': 'https://tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', 'name': 'Humanitarian', 'icon': '🏥'},
        'OpenStreetMap_DE': {'url': 'https://tile.openstreetmap.de/{z}/{x}/{y}.png', 'name': 'OSM Germany', 'icon': '🇩🇪'},
        
        # Esri
        'Esri_WorldImagery': {'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'name': 'Satellite (Esri)', 'icon': '🛰️'},
        'Esri_WorldStreetMap': {'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', 'name': 'Street Map', 'icon': '🏙️'},
        'Esri_WorldTopoMap': {'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', 'name': 'Topographic', 'icon': '⛰️'},
        'Esri_WorldGrayCanvas': {'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', 'name': 'Gray Canvas', 'icon': '🌫️'},
        
        # Google
        'Google_Maps': {'url': 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 'name': 'Google Maps', 'icon': '📱'},
        'Google_Satellite': {'url': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 'name': 'Google Satellite', 'icon': '🛰️'},
        'Google_Terrain': {'url': 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', 'name': 'Google Terrain', 'icon': '🏔️'},
        
        # Stamen
        'Stamen_Toner': {'url': 'https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png', 'name': 'Toner', 'icon': '⚫'},
        'Stamen_Terrain': {'url': 'https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png', 'name': 'Terrain', 'icon': '🏞️'},
        'Stamen_Watercolor': {'url': 'https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png', 'name': 'Watercolor', 'icon': '🎨'},
        
        # CartoDB
        'CartoDB_Voyager': {'url': 'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', 'name': 'Voyager', 'icon': '🚀'},
        'CartoDB_Dark': {'url': 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', 'name': 'Dark Matter', 'icon': '🌙'},
        
        # Thunderforest
        'OpenTopoMap': {'url': 'https://tile.opentopomap.org/{z}/{x}/{y}.png', 'name': 'OpenTopoMap', 'icon': '🗻'},
        
        # IGN France
        'IGN_Ortho': {'url': 'https://wxs.ign.fr/ortho/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg', 'name': 'IGN Ortho', 'icon': '🇫🇷'},
        'IGN_Plan': {'url': 'https://wxs.ign.fr/plan/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/jpeg', 'name': 'IGN Plan', 'icon': '🗺️'},
    }
    
    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.joman_gis/cache/tiles")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_tile(self, map_name, z, x, y):
        cache_file = os.path.join(self.cache_dir, f"{map_name}_{z}_{x}_{y}.png")
        if os.path.exists(cache_file):
            import matplotlib.image as mpimg
            return mpimg.imread(cache_file)
        
        if map_name not in self.MAPS:
            map_name = 'OpenStreetMap'
        
        url = self.MAPS[map_name]['url'].format(z=z, x=x, y=y)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                img.save(cache_file)
                return np.array(img)
        except Exception as e:
            print(f"Tile error: {e}")
        return None
    
    def list_maps(self):
        return [(k, v['name'], v['icon']) for k, v in self.MAPS.items()]
