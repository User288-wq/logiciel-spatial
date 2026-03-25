# -*- coding: utf-8 -*-
"""
Détecteur universel de pays
"""

class CountryDetector:
    def __init__(self):
        self.current_country = None
        self.current_continent = None
        self.current_gdf = None
    
    def detect(self, gdf):
        self.current_gdf = gdf
        bounds = gdf.total_bounds
        
        # Détection simple par limites
        if bounds[0] > -130 and bounds[2] < -60 and bounds[1] > 24 and bounds[3] < 50:
            self.current_country = 'USA'
            self.current_continent = 'Amérique du Nord'
        elif bounds[0] > -18 and bounds[2] < -11 and bounds[1] > 12 and bounds[3] < 17:
            self.current_country = 'SENEGAL'
            self.current_continent = 'Afrique'
        elif bounds[0] > -5 and bounds[2] < 10 and bounds[1] > 41 and bounds[3] < 52:
            self.current_country = 'FRANCE'
            self.current_continent = 'Europe'
        else:
            self.current_country = 'MONDE'
            self.current_continent = 'Monde'
        
        return self.current_country
    
    def get_country_info(self):
        info = {
            'USA': {'name': 'États-Unis', 'capital': 'Washington DC', 'bounds': (-125, 24, -66, 49), 'color': '#4CAF50', 'continent': 'Amérique du Nord', 'zoom': 4},
            'SENEGAL': {'name': 'Sénégal', 'capital': 'Dakar', 'bounds': (-17.8, 12.3, -11.5, 16.5), 'color': '#FFA500', 'continent': 'Afrique', 'zoom': 7},
            'FRANCE': {'name': 'France', 'capital': 'Paris', 'bounds': (-5, 41, 9, 51), 'color': '#2196F3', 'continent': 'Europe', 'zoom': 6},
            'MONDE': {'name': 'Monde', 'capital': 'N/A', 'bounds': (-180, -90, 180, 90), 'color': '#4CAF50', 'continent': 'Monde', 'zoom': 2}
        }
        return info.get(self.current_country, info['MONDE'])
    
    def get_recommended_style(self):
        info = self.get_country_info()
        return {'color': info['color'], 'edgecolor': '#2E7D32', 'alpha': 0.6, 'linewidth': 1, 'label_color': '#333333', 'label_size': 10}
    
    def get_bounds(self):
        return self.get_country_info()['bounds']
    
    def get_continent(self):
        return self.get_country_info()['continent']
    
    def get_zoom_level(self):
        return self.get_country_info()['zoom']
    
    def format_distance(self, km):
        return f"{km:.1f} km"

country_detector = CountryDetector()
