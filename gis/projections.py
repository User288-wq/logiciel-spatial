# -*- coding: utf-8 -*-
"""
Système de projections JOMAN GIS
Toutes les projections comme dans QGIS
"""

import pyproj
from pyproj import CRS, Transformer
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString

class JomanProjections:
    """Gestionnaire de projections JOMAN GIS"""
    
    # ==================== PROJECTIONS MONDIALES ====================
    WORLD_PROJECTIONS = {
        'EPSG:4326': {'name': 'WGS 84', 'description': 'Système GPS standard', 'area': 'Monde entier', 'type': 'Géographique'},
        'EPSG:3857': {'name': 'Web Mercator', 'description': 'Google Maps, OpenStreetMap', 'area': 'Monde entier', 'type': 'Projectée'},
        'EPSG:3395': {'name': 'World Mercator', 'description': 'Mercator Monde', 'area': 'Monde entier', 'type': 'Projectée'},
        'EPSG:54004': {'name': 'World Equidistant Cylindrical', 'description': 'Cylindrique équidistante', 'area': 'Monde entier', 'type': 'Projectée'},
        'EPSG:54009': {'name': 'Mollweide', 'description': 'Projection Mollweide', 'area': 'Monde entier', 'type': 'Projectée'},
        'EPSG:54030': {'name': 'Robinson', 'description': 'Projection Robinson', 'area': 'Monde entier', 'type': 'Projectée'},
        'EPSG:54012': {'name': 'Sinusoidal', 'description': 'Projection Sinusoïdale', 'area': 'Monde entier', 'type': 'Projectée'},
    }
    
    # ==================== PROJECTIONS AFRIQUE ====================
    AFRICA_PROJECTIONS = {
        'EPSG:32628': {'name': 'WGS 84 / UTM zone 28N', 'description': 'Sénégal, Mauritanie, Mali Ouest', 'area': 'Afrique de l\'Ouest', 'type': 'UTM'},
        'EPSG:32629': {'name': 'WGS 84 / UTM zone 29N', 'description': 'Sénégal Est, Mali, Burkina Faso', 'area': 'Afrique de l\'Ouest', 'type': 'UTM'},
        'EPSG:32630': {'name': 'WGS 84 / UTM zone 30N', 'description': 'Niger, Nigeria, Tchad', 'area': 'Afrique centrale', 'type': 'UTM'},
        'EPSG:32631': {'name': 'WGS 84 / UTM zone 31N', 'description': 'Cameroun, RCA, Soudan', 'area': 'Afrique centrale', 'type': 'UTM'},
        'EPSG:32632': {'name': 'WGS 84 / UTM zone 32N', 'description': 'Égypte, Libye, Soudan', 'area': 'Afrique du Nord', 'type': 'UTM'},
        'EPSG:32633': {'name': 'WGS 84 / UTM zone 33N', 'description': 'Égypte, Arabie Saoudite', 'area': 'Afrique du Nord', 'type': 'UTM'},
        'EPSG:32728': {'name': 'WGS 84 / UTM zone 28S', 'description': 'Afrique du Sud, Namibie', 'area': 'Afrique australe', 'type': 'UTM'},
        'EPSG:32729': {'name': 'WGS 84 / UTM zone 29S', 'description': 'Afrique du Sud, Botswana', 'area': 'Afrique australe', 'type': 'UTM'},
        'EPSG:32730': {'name': 'WGS 84 / UTM zone 30S', 'description': 'Afrique du Sud, Zimbabwe', 'area': 'Afrique australe', 'type': 'UTM'},
        'EPSG:32731': {'name': 'WGS 84 / UTM zone 31S', 'description': 'Mozambique, Madagascar', 'area': 'Afrique australe', 'type': 'UTM'},
        'EPSG:32732': {'name': 'WGS 84 / UTM zone 32S', 'description': 'Madagascar Est', 'area': 'Afrique australe', 'type': 'UTM'},
        'EPSG:22234': {'name': 'Hartebeesthoek94 / Lo31', 'description': 'Afrique du Sud', 'area': 'Afrique du Sud', 'type': 'Projectée'},
        'EPSG:22235': {'name': 'Hartebeesthoek94 / Lo33', 'description': 'Afrique du Sud', 'area': 'Afrique du Sud', 'type': 'Projectée'},
    }
    
    # ==================== PROJECTIONS AMÉRIQUE ====================
    AMERICA_PROJECTIONS = {
        'EPSG:4269': {'name': 'NAD83', 'description': 'North American Datum 1983', 'area': 'Amérique du Nord', 'type': 'Géographique'},
        'EPSG:4267': {'name': 'NAD27', 'description': 'North American Datum 1927', 'area': 'Amérique du Nord', 'type': 'Géographique'},
        'EPSG:26910': {'name': 'NAD83 / UTM zone 10N', 'description': 'USA Ouest', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26911': {'name': 'NAD83 / UTM zone 11N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26912': {'name': 'NAD83 / UTM zone 12N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26913': {'name': 'NAD83 / UTM zone 13N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26914': {'name': 'NAD83 / UTM zone 14N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26915': {'name': 'NAD83 / UTM zone 15N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26916': {'name': 'NAD83 / UTM zone 16N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26917': {'name': 'NAD83 / UTM zone 17N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26918': {'name': 'NAD83 / UTM zone 18N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:26919': {'name': 'NAD83 / UTM zone 19N', 'description': 'USA', 'area': 'États-Unis', 'type': 'UTM'},
        'EPSG:31982': {'name': 'SIRGAS 2000 / UTM zone 22S', 'description': 'Brésil', 'area': 'Brésil', 'type': 'UTM'},
        'EPSG:31983': {'name': 'SIRGAS 2000 / UTM zone 23S', 'description': 'Brésil', 'area': 'Brésil', 'type': 'UTM'},
        'EPSG:31984': {'name': 'SIRGAS 2000 / UTM zone 24S', 'description': 'Brésil', 'area': 'Brésil', 'type': 'UTM'},
        'EPSG:31985': {'name': 'SIRGAS 2000 / UTM zone 25S', 'description': 'Brésil', 'area': 'Brésil', 'type': 'UTM'},
        'EPSG:5347': {'name': 'POSGAR 2007 / Argentina zone 1', 'description': 'Argentine', 'area': 'Argentine', 'type': 'Projectée'},
        'EPSG:5348': {'name': 'POSGAR 2007 / Argentina zone 2', 'description': 'Argentine', 'area': 'Argentine', 'type': 'Projectée'},
        'EPSG:5349': {'name': 'POSGAR 2007 / Argentina zone 3', 'description': 'Argentine', 'area': 'Argentine', 'type': 'Projectée'},
    }
    
    # ==================== PROJECTIONS EUROPE ====================
    EUROPE_PROJECTIONS = {
        'EPSG:2154': {'name': 'RGF93 / Lambert-93', 'description': 'France métropolitaine', 'area': 'France', 'type': 'Lambert'},
        'EPSG:27572': {'name': 'NTF / Lambert zone II', 'description': 'France (ancien)', 'area': 'France', 'type': 'Lambert'},
        'EPSG:3946': {'name': 'RGF93 / CC46', 'description': 'France zone 6', 'area': 'France', 'type': 'Lambert'},
        'EPSG:3947': {'name': 'RGF93 / CC47', 'description': 'France zone 7', 'area': 'France', 'type': 'Lambert'},
        'EPSG:3948': {'name': 'RGF93 / CC48', 'description': 'France zone 8', 'area': 'France', 'type': 'Lambert'},
        'EPSG:3949': {'name': 'RGF93 / CC49', 'description': 'France zone 9', 'area': 'France', 'type': 'Lambert'},
        'EPSG:3950': {'name': 'RGF93 / CC50', 'description': 'France zone 10', 'area': 'France', 'type': 'Lambert'},
        'EPSG:25832': {'name': 'ETRS89 / UTM zone 32N', 'description': 'Allemagne, Italie', 'area': 'Europe centrale', 'type': 'UTM'},
        'EPSG:25833': {'name': 'ETRS89 / UTM zone 33N', 'description': 'Allemagne, Pologne', 'area': 'Europe centrale', 'type': 'UTM'},
        'EPSG:25834': {'name': 'ETRS89 / UTM zone 34N', 'description': 'Pologne, Suède', 'area': 'Europe du Nord', 'type': 'UTM'},
        'EPSG:25835': {'name': 'ETRS89 / UTM zone 35N', 'description': 'Finlande, Suède', 'area': 'Europe du Nord', 'type': 'UTM'},
        'EPSG:27700': {'name': 'OSGB 1936 / British National Grid', 'description': 'Royaume-Uni', 'area': 'Royaume-Uni', 'type': 'National Grid'},
        'EPSG:31370': {'name': 'Belge 1972 / Belgian Lambert 72', 'description': 'Belgique', 'area': 'Belgique', 'type': 'Lambert'},
        'EPSG:3812': {'name': 'ETRS89 / Belgian Lambert 2008', 'description': 'Belgique', 'area': 'Belgique', 'type': 'Lambert'},
        'EPSG:2056': {'name': 'CH1903+ / LV95', 'description': 'Suisse', 'area': 'Suisse', 'type': 'Projectée'},
        'EPSG:21781': {'name': 'CH1903 / LV03', 'description': 'Suisse (ancien)', 'area': 'Suisse', 'type': 'Projectée'},
        'EPSG:3042': {'name': 'ED50 / UTM zone 30N', 'description': 'Espagne', 'area': 'Espagne', 'type': 'UTM'},
        'EPSG:3043': {'name': 'ED50 / UTM zone 31N', 'description': 'Espagne', 'area': 'Espagne', 'type': 'UTM'},
        'EPSG:32632': {'name': 'WGS 84 / UTM zone 32N', 'description': 'Italie, Allemagne', 'area': 'Europe', 'type': 'UTM'},
        'EPSG:32633': {'name': 'WGS 84 / UTM zone 33N', 'description': 'Europe centrale', 'area': 'Europe', 'type': 'UTM'},
    }
    
    # ==================== PROJECTIONS ASIE ====================
    ASIA_PROJECTIONS = {
        'EPSG:2452': {'name': 'Indian 1960 / UTM zone 48N', 'description': 'Inde', 'area': 'Inde', 'type': 'UTM'},
        'EPSG:32650': {'name': 'WGS 84 / UTM zone 50N', 'description': 'Chine, Japon', 'area': 'Asie de l\'Est', 'type': 'UTM'},
        'EPSG:32651': {'name': 'WGS 84 / UTM zone 51N', 'description': 'Japon, Corée', 'area': 'Asie de l\'Est', 'type': 'UTM'},
        'EPSG:32652': {'name': 'WGS 84 / UTM zone 52N', 'description': 'Japon', 'area': 'Japon', 'type': 'UTM'},
        'EPSG:32653': {'name': 'WGS 84 / UTM zone 53N', 'description': 'Japon', 'area': 'Japon', 'type': 'UTM'},
        'EPSG:32654': {'name': 'WGS 84 / UTM zone 54N', 'description': 'Japon', 'area': 'Japon', 'type': 'UTM'},
        'EPSG:32647': {'name': 'WGS 84 / UTM zone 47N', 'description': 'Chine', 'area': 'Chine', 'type': 'UTM'},
        'EPSG:32648': {'name': 'WGS 84 / UTM zone 48N', 'description': 'Chine', 'area': 'Chine', 'type': 'UTM'},
        'EPSG:32649': {'name': 'WGS 84 / UTM zone 49N', 'description': 'Chine', 'area': 'Chine', 'type': 'UTM'},
        'EPSG:2431': {'name': 'India/n India', 'description': 'Inde', 'area': 'Inde', 'type': 'Projectée'},
        'EPSG:2432': {'name': 'India/n India', 'description': 'Inde', 'area': 'Inde', 'type': 'Projectée'},
        'EPSG:2433': {'name': 'India/n India', 'description': 'Inde', 'area': 'Inde', 'type': 'Projectée'},
        'EPSG:2441': {'name': 'India/s India', 'description': 'Inde du Sud', 'area': 'Inde', 'type': 'Projectée'},
        'EPSG:2442': {'name': 'India/s India', 'description': 'Inde du Sud', 'area': 'Inde', 'type': 'Projectée'},
    }
    
    # ==================== PROJECTIONS OCÉANIE ====================
    OCEANIA_PROJECTIONS = {
        'EPSG:28350': {'name': 'GDA94 / MGA zone 50', 'description': 'Australie Ouest', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:28351': {'name': 'GDA94 / MGA zone 51', 'description': 'Australie', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:28352': {'name': 'GDA94 / MGA zone 52', 'description': 'Australie', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:28353': {'name': 'GDA94 / MGA zone 53', 'description': 'Australie', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:28354': {'name': 'GDA94 / MGA zone 54', 'description': 'Australie', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:28355': {'name': 'GDA94 / MGA zone 55', 'description': 'Australie Est', 'area': 'Australie', 'type': 'UTM'},
        'EPSG:2193': {'name': 'NZGD2000 / New Zealand Transverse Mercator', 'description': 'Nouvelle-Zélande', 'area': 'Nouvelle-Zélande', 'type': 'Projectée'},
    }
    
    # Rassembler toutes les projections
    ALL_PROJECTIONS = {}
    ALL_PROJECTIONS.update(WORLD_PROJECTIONS)
    ALL_PROJECTIONS.update(AFRICA_PROJECTIONS)
    ALL_PROJECTIONS.update(AMERICA_PROJECTIONS)
    ALL_PROJECTIONS.update(EUROPE_PROJECTIONS)
    ALL_PROJECTIONS.update(ASIA_PROJECTIONS)
    ALL_PROJECTIONS.update(OCEANIA_PROJECTIONS)
    
    # Projections UTM complètes (1-60)
    for zone in range(1, 61):
        ALL_PROJECTIONS[f'EPSG:326{zone:02d}'] = {
            'name': f'WGS 84 / UTM zone {zone}N',
            'description': f'UTM zone {zone} Nord',
            'area': 'Monde',
            'type': 'UTM'
        }
        ALL_PROJECTIONS[f'EPSG:327{zone:02d}'] = {
            'name': f'WGS 84 / UTM zone {zone}S',
            'description': f'UTM zone {zone} Sud',
            'area': 'Monde',
            'type': 'UTM'
        }
    
    def __init__(self):
        self.current_crs = 'EPSG:4326'
        self.transformer = None
    
    def get_projection_info(self, epsg_code):
        """Retourne les informations d'une projection"""
        if epsg_code in self.ALL_PROJECTIONS:
            return self.ALL_PROJECTIONS[epsg_code]
        return {
            'name': epsg_code,
            'description': 'Projection personnalisée',
            'area': 'Inconnu',
            'type': 'Inconnu'
        }
    
    def get_all_projections(self):
        """Retourne toutes les projections disponibles"""
        result = []
        for epsg, info in self.ALL_PROJECTIONS.items():
            result.append({
                'epsg': epsg,
                'name': info['name'],
                'description': info['description'],
                'area': info['area'],
                'type': info['type']
            })
        return sorted(result, key=lambda x: x['epsg'])
    
    def get_projections_by_area(self, area):
        """Filtre les projections par région"""
        return [p for p in self.get_all_projections() if area.lower() in p['area'].lower()]
    
    def get_projections_by_type(self, ptype):
        """Filtre les projections par type"""
        return [p for p in self.get_all_projections() if ptype.lower() in p['type'].lower()]
    
    def get_utm_zone(self, lon, lat):
        """Calcule la zone UTM pour un point donné"""
        zone = int((lon + 180) / 6) + 1
        hemisphere = 'N' if lat >= 0 else 'S'
        epsg = f'EPSG:326{zone:02d}' if hemisphere == 'N' else f'EPSG:327{zone:02d}'
        return epsg
    
    def transform_gdf(self, gdf, target_crs):
        """Reprojette un GeoDataFrame"""
        try:
            return gdf.to_crs(target_crs)
        except Exception as e:
            print(f"Erreur reprojection: {e}")
            return gdf
    
    def transform_point(self, x, y, source_crs, target_crs):
        """Reprojette un point"""
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        return transformer.transform(x, y)
    
    def get_proj4_string(self, epsg_code):
        """Retourne la chaîne Proj4"""
        try:
            crs = CRS.from_epsg(int(epsg_code.split(':')[1]))
            return crs.to_proj4()
        except:
            return None
    
    def get_wkt_string(self, epsg_code):
        """Retourne la chaîne WKT"""
        try:
            crs = CRS.from_epsg(int(epsg_code.split(':')[1]))
            return crs.to_wkt()
        except:
            return None

# Instance globale
joman_projections = JomanProjections()
