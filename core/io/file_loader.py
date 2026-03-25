# core/io/file_loader.py
"""
================================================================================
📂 CHARGEUR DE FICHIERS - GESTION DES FORMATS
================================================================================
"""

import os
import zipfile
import tempfile
from typing import Tuple, Optional, List
from abc import ABC, abstractmethod
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


class FormatHandler(ABC):
    """Classe abstraite pour un format de fichier"""
    
    @abstractmethod
    def can_handle(self, filename: str) -> bool:
        pass
    
    @abstractmethod
    def load(self, filename: str) -> Tuple[Optional[gpd.GeoDataFrame], Optional[str]]:
        pass


class ShapefileHandler(FormatHandler):
    """Handler pour les Shapefiles"""
    
    def can_handle(self, filename: str) -> bool:
        return filename.lower().endswith('.shp')
    
    def load(self, filename: str):
        try:
            gdf = gpd.read_file(filename)
            return gdf, None
        except Exception as e:
            return None, str(e)


class GeoJSONHandler(FormatHandler):
    """Handler pour les fichiers GeoJSON"""
    
    def can_handle(self, filename: str) -> bool:
        return filename.lower().endswith(('.geojson', '.json'))
    
    def load(self, filename: str):
        try:
            gdf = gpd.read_file(filename)
            return gdf, None
        except Exception as e:
            return None, str(e)


class KMLHandler(FormatHandler):
    """Handler pour les fichiers KML/KMZ"""
    
    def can_handle(self, filename: str) -> bool:
        return filename.lower().endswith(('.kml', '.kmz'))
    
    def load(self, filename: str):
        try:
            if filename.lower().endswith('.kmz'):
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(filename, 'r') as kmz:
                        kmz.extractall(tmpdir)
                        kml_files = [f for f in os.listdir(tmpdir) if f.endswith('.kml')]
                        if kml_files:
                            gdf = gpd.read_file(os.path.join(tmpdir, kml_files[0]), driver='KML')
                            return gdf, None
                    return None, "Aucun fichier KML trouvé"
            else:
                gdf = gpd.read_file(filename, driver='KML')
                return gdf, None
        except Exception as e:
            return None, str(e)


class CSVHandler(FormatHandler):
    """Handler pour les fichiers CSV avec coordonnées"""
    
    def can_handle(self, filename: str) -> bool:
        return filename.lower().endswith(('.csv', '.txt'))
    
    def load(self, filename: str):
        try:
            df = pd.read_csv(filename, nrows=10000)
            
            lat_col = None
            lon_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ['lat', 'latitude', 'y']:
                    lat_col = col
                elif col_lower in ['lon', 'long', 'longitude', 'x']:
                    lon_col = col
            
            if lat_col and lon_col:
                geometry = [Point(x, y) for x, y in zip(df[lon_col], df[lat_col])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                return gdf, None
            else:
                return None, "Aucune colonne de coordonnées trouvée"
        except Exception as e:
            return None, str(e)


class FileLoader:
    """Chargeur de fichiers unifié"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.handlers: List[FormatHandler] = [
            ShapefileHandler(),
            GeoJSONHandler(),
            KMLHandler(),
            CSVHandler(),
        ]
    
    def load(self, filename: str) -> Tuple[Optional[gpd.GeoDataFrame], Optional[str]]:
        """Charge un fichier et retourne un GeoDataFrame"""
        for handler in self.handlers:
            if handler.can_handle(filename):
                gdf, error = handler.load(filename)
                if gdf is not None:
                    return gdf, None
                return None, error
        return None, f"Format non supporté: {os.path.splitext(filename)[1]}"
    
    def get_supported_extensions(self) -> List[str]:
        """Retourne les extensions supportées"""
        return ['.shp', '.geojson', '.json', '.kml', '.kmz', '.csv', '.txt']