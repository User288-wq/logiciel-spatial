# -*- coding: utf-8 -*-
import os
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import matplotlib.image as mpimg

class BaseMapProvider:
    MAPS = {
        'OpenStreetMap': {'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'name': 'OpenStreetMap', 'icon': '🗺️', 'attribution': '© OpenStreetMap'},
        'Satellite': {'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'name': 'Satellite', 'icon': '🛰️', 'attribution': '© Esri'},
        'Topographic': {'url': 'https://tile.opentopomap.org/{z}/{x}/{y}.png', 'name': 'Topographic', 'icon': '⛰️', 'attribution': '© OpenTopoMap'},
        'Dark': {'url': 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png', 'name': 'Dark', 'icon': '🌙', 'attribution': '© Stadia'},
        'Light': {'url': 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png', 'name': 'Light', 'icon': '☀️', 'attribution': '© Stadia'},
        'Humanitarian': {'url': 'https://tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', 'name': 'Humanitarian', 'icon': '🏥', 'attribution': '© HOT OSM'},
        'Google Maps': {'url': 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', 'name': 'Google Maps', 'icon': '📱', 'attribution': '© Google'},
        'Google Satellite': {'url': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 'name': 'Google Satellite', 'icon': '🛰️', 'attribution': '© Google'}
    }
    
    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.joman_gis/cache/tiles")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_tile(self, map_name, z, x, y):
        cache_file = os.path.join(self.cache_dir, f"{map_name}_{z}_{x}_{y}.png")
        if os.path.exists(cache_file):
            return mpimg.imread(cache_file)
        url = self.MAPS[map_name]['url'].format(z=z, x=x, y=y)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(cache_file)
                return np.array(img)
        except:
            pass
        return None
    
    def list_maps(self):
        return [(k, v['name'], v['icon']) for k, v in self.MAPS.items()]
