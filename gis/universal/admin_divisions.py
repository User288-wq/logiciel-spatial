# -*- coding: utf-8 -*-
"""
Gestionnaire de découpage administratif
Affiche les régions, départements, communes sur la carte
"""

import geopandas as gpd
import matplotlib.patches as mpatches
from shapely.geometry import Polygon, Point

class AdminDivisions:
    """Gestionnaire de découpage administratif"""
    
    # Niveaux administratifs avec leurs couleurs
    LEVELS = {
        1: {'name': 'Région', 'color': '#4CAF50', 'alpha': 0.3, 'linewidth': 2, 'label_size': 12},
        2: {'name': 'Département', 'color': '#FFA500', 'alpha': 0.4, 'linewidth': 1.5, 'label_size': 10},
        3: {'name': 'Arrondissement', 'color': '#2196F3', 'alpha': 0.5, 'linewidth': 1, 'label_size': 9},
        4: {'name': 'Commune', 'color': '#FFC107', 'alpha': 0.6, 'linewidth': 0.8, 'label_size': 8},
        5: {'name': 'Village', 'color': '#9C27B0', 'alpha': 0.7, 'linewidth': 0.5, 'label_size': 7}
    }
    
    def __init__(self):
        self.divisions = {}
        self.current_gdf = None
        self.current_level = None
    
    def load_divisions(self, gdf, level=1, name_col='name', code_col='code'):
        """Charge des divisions administratives"""
        self.divisions[level] = {
            'gdf': gdf,
            'name_col': name_col,
            'code_col': code_col,
            'visible': True
        }
        self.current_gdf = gdf
        self.current_level = level
        return gdf
    
    def detect_level(self, gdf):
        """Détecte automatiquement le niveau administratif"""
        n = len(gdf)
        if n <= 20:
            return 1
        elif n <= 100:
            return 2
        elif n <= 500:
            return 3
        else:
            return 4
    
    def get_level_style(self, level):
        """Retourne le style pour un niveau donné"""
        if level in self.LEVELS:
            return self.LEVELS[level]
        return self.LEVELS[4]
    
    def render_divisions(self, ax):
        """Affiche les divisions sur la carte"""
        for lvl in self.divisions:
            if self.divisions[lvl]['visible']:
                data = self.divisions[lvl]
                gdf = data['gdf']
                style = self.get_level_style(lvl)
                name_col = data['name_col']
                
                if gdf is not None and len(gdf) > 0:
                    gdf.plot(ax=ax, color=style['color'], alpha=style['alpha'], 
                            edgecolor='white', linewidth=style['linewidth'])
                    
                    if name_col in gdf.columns:
                        for idx, row in gdf.iterrows():
                            if row.geometry and not row.geometry.is_empty:
                                try:
                                    centroid = row.geometry.centroid
                                    label = str(row[name_col])[:25]
                                    ax.text(centroid.x, centroid.y, label,
                                           fontsize=style['label_size'], 
                                           color='#333333', ha='center', va='center',
                                           bbox=dict(boxstyle="round,pad=0.2", 
                                                    facecolor='white', alpha=0.8))
                                except:
                                    pass
    
    def get_hierarchy(self, lat, lon):
        """Trouve la hiérarchie administrative pour un point"""
        point = Point(lon, lat)
        result = []
        
        for level in sorted(self.divisions.keys()):
            gdf = self.divisions[level]['gdf']
            name_col = self.divisions[level]['name_col']
            
            for idx, row in gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    result.append({
                        'level': level,
                        'name': row[name_col] if name_col in row else f'Niveau {level}',
                        'level_name': self.LEVELS[level]['name']
                    })
                    break
        
        return result
    
    def get_divisions_at_level(self, level):
        if level in self.divisions:
            return self.divisions[level]['gdf']
        return None

admin_divisions = AdminDivisions()
