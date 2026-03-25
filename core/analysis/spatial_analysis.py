# core/analysis/spatial_analysis.py
"""
================================================================================
📊 ANALYSE SPATIALE - FONCTIONS D'ANALYSE
================================================================================
"""

import math
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DistanceResult:
    """Résultat d'une mesure de distance"""
    points: List[Tuple[float, float]]
    total_distance_km: float
    segments: List[float]


@dataclass
class BufferResult:
    """Résultat d'une opération de buffer"""
    geometry: Polygon
    area_km2: float
    perimeter_km: float


class SpatialAnalysis:
    """Moteur d'analyse spatiale"""
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calcule la distance entre deux points en km"""
        dx = (p2[0] - p1[0]) * 111
        dy = (p2[1] - p1[1]) * 111
        return math.sqrt(dx*dx + dy*dy)
    
    @staticmethod
    def calculate_total_distance(points: List[Tuple[float, float]]) -> DistanceResult:
        """Calcule la distance totale d'une polyligne"""
        total = 0
        segments = []
        for i in range(len(points)-1):
            dist = SpatialAnalysis.calculate_distance(points[i], points[i+1])
            segments.append(dist)
            total += dist
        return DistanceResult(points, total, segments)
    
    @staticmethod
    def get_statistics(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Retourne les statistiques d'un GeoDataFrame"""
        stats = {
            'count': len(gdf),
            'columns': list(gdf.columns),
            'geometry_type': gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'None',
            'bounds': gdf.total_bounds.tolist() if len(gdf) > 0 else [],
            'crs': str(gdf.crs) if gdf.crs else 'None'
        }
        
        numeric_stats = {}
        for col in gdf.columns:
            if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
                numeric_stats[col] = {
                    'min': gdf[col].min(),
                    'max': gdf[col].max(),
                    'mean': gdf[col].mean(),
                    'std': gdf[col].std()
                }
        stats['numeric_stats'] = numeric_stats
        
        return stats
    
    @staticmethod
    def filter_by_attribute(gdf: gpd.GeoDataFrame, column: str, 
                            operator: str, value: Any) -> List[int]:
        """Filtre les entités par attribut"""
        if operator == '=':
            mask = gdf[column].astype(str) == str(value)
        elif operator == '!=':
            mask = gdf[column].astype(str) != str(value)
        elif operator == '>':
            mask = gdf[column].astype(float) > float(value)
        elif operator == '<':
            mask = gdf[column].astype(float) < float(value)
        elif operator == '>=':
            mask = gdf[column].astype(float) >= float(value)
        elif operator == '<=':
            mask = gdf[column].astype(float) <= float(value)
        elif operator == 'contains':
            mask = gdf[column].astype(str).str.contains(str(value), case=False, na=False)
        else:
            return []
        
        return mask[mask].index.tolist()
    
    @staticmethod
    def search_by_name(gdf: gpd.GeoDataFrame, text: str, 
                       name_columns: List[str]) -> List[Tuple[int, str, Any]]:
        """Recherche par nom dans les colonnes spécifiées"""
        results = []
        text_lower = text.lower()
        
        for col in name_columns:
            if col in gdf.columns:
                for idx, row in gdf.iterrows():
                    name = str(row[col]).lower()
                    if text_lower in name:
                        results.append((idx, col, row[col]))
        
        return results