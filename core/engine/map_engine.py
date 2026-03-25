# core/engine/map_engine.py
"""
================================================================================
🗺️ MOTEUR CARTOGRAPHIQUE PROFESSIONNEL - VERSION COMPLÈTE
================================================================================
Version: 2.0.0
Auteur: Lead Dev
Date: 2026

Fonctionnalités :
- Gestion des couches vectorielles et raster
- Styles personnalisables
- Zoom avant/arrière
- Vue d'ensemble
- Sélection d'entités
- Mesure de distance
- Listeners pour événements
- Gestion des projections
- Cache des bornes
- Filtrage par attributs
- Recherche textuelle
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum
import math
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString


class RenderMode(Enum):
    """Modes de rendu disponibles"""
    VECTOR = "vector"
    RASTER = "raster"
    HYBRID = "hybrid"


class Projection(Enum):
    """Projections supportées"""
    WGS84 = "EPSG:4326"
    WEB_MERCATOR = "EPSG:3857"
    UTM_28N = "EPSG:32628"
    UTM_29N = "EPSG:32629"
    LAMBERT_93 = "EPSG:2154"
    
    @staticmethod
    def from_epsg(code: str) -> 'Projection':
        """Crée une projection depuis un code EPSG"""
        for p in Projection:
            if p.value == code:
                return p
        return Projection.WGS84


@dataclass
class MapExtent:
    """Étendue de la carte"""
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    
    @property
    def width(self) -> float:
        return self.xmax - self.xmin
    
    @property
    def height(self) -> float:
        return self.ymax - self.ymin
    
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.xmin + self.xmax) / 2, (self.ymin + self.ymax) / 2)
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def margin(self, ratio: float = 0.05) -> 'MapExtent':
        """Ajoute une marge autour de l'étendue"""
        margin_x = self.width * ratio
        margin_y = self.height * ratio
        return MapExtent(
            self.xmin - margin_x,
            self.ymin - margin_y,
            self.xmax + margin_x,
            self.ymax + margin_y
        )
    
    def contains(self, x: float, y: float) -> bool:
        """Vérifie si un point est dans l'étendue"""
        return (self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax)
    
    def to_list(self) -> List[float]:
        """Convertit en liste [xmin, ymin, xmax, ymax]"""
        return [self.xmin, self.ymin, self.xmax, self.ymax]
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convertit en tuple (xmin, ymin, xmax, ymax)"""
        return (self.xmin, self.ymin, self.xmax, self.ymax)
    
    @classmethod
    def from_list(cls, data: List[float]) -> 'MapExtent':
        """Crée une étendue depuis une liste"""
        if len(data) == 4:
            return cls(data[0], data[1], data[2], data[3])
        return cls(0, 0, 0, 0)
    
    @classmethod
    def from_bounds(cls, bounds: Tuple[float, float, float, float]) -> 'MapExtent':
        """Crée une étendue depuis un tuple de bounds"""
        return cls(bounds[0], bounds[1], bounds[2], bounds[3])


@dataclass
class LayerStyle:
    """Style d'une couche cartographique"""
    color: str = "#4CAF50"
    edge_color: str = "#2E7D32"
    fill_alpha: float = 0.4
    line_width: float = 1.0
    line_style: str = "solid"
    point_size: float = 5.0
    point_marker: str = "o"
    label_color: str = "#FFFFFF"
    label_size: float = 8.0
    label_weight: str = "normal"
    label_halo: bool = True
    visible: bool = True
    min_zoom: int = 0
    max_zoom: int = 20
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'color': self.color,
            'edge_color': self.edge_color,
            'fill_alpha': self.fill_alpha,
            'line_width': self.line_width,
            'line_style': self.line_style,
            'point_size': self.point_size,
            'point_marker': self.point_marker,
            'label_color': self.label_color,
            'label_size': self.label_size,
            'label_weight': self.label_weight,
            'label_halo': self.label_halo,
            'visible': self.visible,
            'min_zoom': self.min_zoom,
            'max_zoom': self.max_zoom
        }
    
    def update(self, **kwargs):
        """Met à jour le style avec les valeurs fournies"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LayerStyle':
        """Crée un style depuis un dictionnaire"""
        style = cls()
        for key, value in data.items():
            if hasattr(style, key):
                setattr(style, key, value)
        return style


class MapLayer(ABC):
    """Classe abstraite pour une couche cartographique"""
    
    def __init__(self, layer_id: str, name: str, path: str = ""):
        self.id = layer_id
        self.name = name
        self.path = path
        self.visible = True
        self.style = LayerStyle()
        self.opacity = 1.0
        self._metadata: Dict[str, Any] = {}
        self._listeners: List[Callable] = []
    
    @abstractmethod
    def get_bounds(self) -> Optional[MapExtent]:
        """Retourne l'étendue de la couche"""
        pass
    
    @abstractmethod
    def render(self, ax, extent: MapExtent, zoom_level: int):
        """Rend la couche sur l'axe matplotlib"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Retourne le type de la couche (vector, raster)"""
        pass
    
    @abstractmethod
    def get_geometry_type(self) -> str:
        """Retourne le type de géométrie (Point, LineString, Polygon, etc.)"""
        pass
    
    def add_metadata(self, key: str, value: Any):
        """Ajoute une métadonnée"""
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default=None) -> Any:
        """Récupère une métadonnée"""
        return self._metadata.get(key, default)
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """Récupère toutes les métadonnées"""
        return self._metadata.copy()
    
    def add_listener(self, callback: Callable):
        """Ajoute un listener pour les événements de la couche"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Supprime un listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify(self, event: str, **kwargs):
        """Notifie les listeners"""
        for callback in self._listeners:
            try:
                callback(self, event, **kwargs)
            except Exception as e:
                print(f"Erreur listener: {e}")


class VectorLayer(MapLayer):
    """Couche vectorielle (points, lignes, polygones)"""
    
    def __init__(self, layer_id: str, name: str, path: str, gdf: gpd.GeoDataFrame, layer_type: str = "vector"):
        super().__init__(layer_id, name, path)
        self.gdf = gdf
        self.type = layer_type
        self.filtered_indices: Optional[List[int]] = None
        self.selected_index: Optional[int] = None
        self._geometry_type = self._detect_geometry_type()
        self._cached_bounds: Optional[MapExtent] = None
    
    def _detect_geometry_type(self) -> str:
        if len(self.gdf) == 0:
            return "Unknown"
        geom = self.gdf.geometry.iloc[0]
        if isinstance(geom, Point):
            return "Point"
        elif isinstance(geom, LineString):
            return "LineString"
        elif isinstance(geom, Polygon):
            return "Polygon"
        return "Unknown"
    
    def get_type(self) -> str:
        return "vector"
    
    def get_geometry_type(self) -> str:
        return self._geometry_type
    
    def get_bounds(self) -> Optional[MapExtent]:
        if self._cached_bounds:
            return self._cached_bounds
        
        if len(self.gdf) == 0:
            return None
        bounds = self.gdf.total_bounds
        self._cached_bounds = MapExtent(bounds[0], bounds[1], bounds[2], bounds[3])
        return self._cached_bounds
    
    def get_data(self) -> gpd.GeoDataFrame:
        """Retourne les données filtrées si applicable"""
        if self.filtered_indices is not None and len(self.filtered_indices) > 0:
            return self.gdf.iloc[self.filtered_indices]
        return self.gdf
    
    def get_feature_count(self) -> int:
        """Retourne le nombre d'entités (filtrées si applicable)"""
        return len(self.get_data())
    
    def get_column_names(self) -> List[str]:
        """Retourne les noms des colonnes"""
        return [col for col in self.gdf.columns if col != 'geometry']
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la couche"""
        from core.analysis.spatial_analysis import SpatialAnalysis
        return SpatialAnalysis.get_statistics(self.gdf)
    
    def filter_by_attribute(self, column: str, operator: str, value: Any) -> List[int]:
        """Filtre les entités par attribut"""
        from core.analysis.spatial_analysis import SpatialAnalysis
        indices = SpatialAnalysis.filter_by_attribute(self.gdf, column, operator, value)
        self.filtered_indices = indices
        self._notify('filter_changed', indices=indices)
        return indices
    
    def clear_filter(self):
        """Efface le filtre actuel"""
        self.filtered_indices = None
        self._notify('filter_cleared')
    
    def search(self, text: str, name_columns: List[str]) -> List[Tuple[int, str, Any]]:
        """Recherche par nom dans les colonnes spécifiées"""
        from core.analysis.spatial_analysis import SpatialAnalysis
        return SpatialAnalysis.search_by_name(self.gdf, text, name_columns)
    
    def select(self, idx: int):
        """Sélectionne une entité"""
        if idx < len(self.gdf):
            self.selected_index = idx
            self._notify('selection_changed', idx=idx)
    
    def clear_selection(self):
        """Efface la sélection"""
        self.selected_index = None
        self._notify('selection_cleared')
    
    def invalidate_cache(self):
        """Invalide le cache des bornes"""
        self._cached_bounds = None
    
    def render(self, ax, extent: MapExtent, zoom_level: int):
        gdf = self.get_data()
        if len(gdf) == 0:
            return
        
        # Vérifier le niveau de zoom
        if zoom_level < self.style.min_zoom or zoom_level > self.style.max_zoom:
            return
        
        # Sélectionner le style selon le type
        if self._geometry_type == "Point":
            gdf.plot(ax=ax, color=self.style.color, 
                    markersize=self.style.point_size,
                    marker=self.style.point_marker,
                    alpha=self.style.fill_alpha)
        elif self._geometry_type == "LineString":
            gdf.plot(ax=ax, color=self.style.color,
                    linewidth=self.style.line_width,
                    linestyle=self.style.line_style,
                    alpha=self.style.fill_alpha)
        else:
            gdf.plot(ax=ax, color=self.style.color,
                    edgecolor=self.style.edge_color,
                    linewidth=self.style.line_width,
                    alpha=self.style.fill_alpha)
        
        # Surbrillance de l'élément sélectionné
        if self.selected_index is not None and self.selected_index < len(gdf):
            selected = gdf.iloc[[self.selected_index]]
            selected.plot(ax=ax, color='#FFFF00', edgecolor='#FFAA00',
                         linewidth=2, alpha=0.8)


class RasterLayer(MapLayer):
    """Couche raster (images satellites)"""
    
    def __init__(self, layer_id: str, name: str, path: str, data):
        super().__init__(layer_id, name, path)
        self.data = data
        self._cached_bounds: Optional[MapExtent] = None
        self.cmap: str = "viridis"
    
    def get_type(self) -> str:
        return "raster"
    
    def get_geometry_type(self) -> str:
        return "Raster"
    
    def get_bounds(self) -> Optional[MapExtent]:
        if self._cached_bounds:
            return self._cached_bounds
        
        try:
            bounds = self.data.bounds
            self._cached_bounds = MapExtent(bounds.left, bounds.bottom, bounds.right, bounds.top)
            return self._cached_bounds
        except Exception as e:
            print(f"Erreur bounds raster: {e}")
            return None
    
    def render(self, ax, extent: MapExtent, zoom_level: int):
        try:
            from rasterio.plot import show
            show(self.data, ax=ax, alpha=self.opacity, cmap=self.cmap)
        except ImportError:
            ax.text(0.5, 0.5, "rasterio non installé", 
                   transform=ax.transAxes, ha='center', va='center',
                   color='white')
        except Exception as e:
            print(f"Erreur rendu raster: {e}")


class MapEngine:
    """Moteur cartographique central"""
    
    def __init__(self):
        self.layers: List[MapLayer] = []
        self.current_extent: Optional[MapExtent] = None
        self.current_zoom: int = 10
        self.projection: Projection = Projection.WGS84
        self.basemap_enabled: bool = False
        self.measure_mode: bool = False
        self.measure_points: List[Tuple[float, float]] = []
        self._listeners: List[Callable] = []
    
    def add_layer(self, layer: MapLayer):
        """Ajoute une couche au moteur"""
        self.layers.append(layer)
        self._notify_listeners('layer_added', layer)
        if self.current_extent is None:
            self.zoom_to_layer(layer.id)
    
    def remove_layer(self, layer_id: str):
        """Supprime une couche"""
        for i, layer in enumerate(self.layers):
            if layer.id == layer_id:
                del self.layers[i]
                self._notify_listeners('layer_removed', layer_id)
                break
    
    def get_layer(self, layer_id: str) -> Optional[MapLayer]:
        for layer in self.layers:
            if layer.id == layer_id:
                return layer
        return None
    
    def get_layers(self) -> List[MapLayer]:
        """Retourne toutes les couches"""
        return self.layers.copy()
    
    def get_visible_layers(self) -> List[MapLayer]:
        """Retourne les couches visibles"""
        return [layer for layer in self.layers if layer.visible]
    
    def get_layer_count(self) -> int:
        return len(self.layers)
    
    def zoom_to_layer(self, layer_id: str):
        """Centre la carte sur une couche"""
        layer = self.get_layer(layer_id)
        if layer:
            extent = layer.get_bounds()
            if extent:
                self.current_extent = extent.margin(0.1)
                self._notify_listeners('extent_changed', self.current_extent)
    
    def zoom_to_extent(self, extent: MapExtent):
        """Zoom sur une étendue spécifique"""
        self.current_extent = extent
        self._notify_listeners('extent_changed', self.current_extent)
    
    def zoom_all(self):
        """Affiche toutes les couches"""
        if not self.layers:
            self.current_extent = MapExtent(-20, 0, 20, 25)  # Vue Afrique Ouest
            self._notify_listeners('extent_changed', self.current_extent)
            return
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        for layer in self.layers:
            extent = layer.get_bounds()
            if extent:
                xmin = min(xmin, extent.xmin)
                ymin = min(ymin, extent.ymin)
                xmax = max(xmax, extent.xmax)
                ymax = max(ymax, extent.ymax)
        
        if xmin != float('inf'):
            self.current_extent = MapExtent(xmin, ymin, xmax, ymax).margin(0.1)
            self._notify_listeners('extent_changed', self.current_extent)
    
    def set_extent(self, extent: MapExtent):
        """Définit l'étendue de la carte"""
        self.current_extent = extent
        self._notify_listeners('extent_changed', extent)
    
    def zoom_in(self, factor: float = 0.8):
        """Zoom avant"""
        if self.current_extent:
            new_extent = MapExtent(
                self.current_extent.xmin + self.current_extent.width * (1 - factor) / 2,
                self.current_extent.ymin + self.current_extent.height * (1 - factor) / 2,
                self.current_extent.xmax - self.current_extent.width * (1 - factor) / 2,
                self.current_extent.ymax - self.current_extent.height * (1 - factor) / 2
            )
            self.current_extent = new_extent
            self._notify_listeners('extent_changed', self.current_extent)
            self.current_zoom += 1
    
    def zoom_out(self, factor: float = 1.25):
        """Zoom arrière"""
        if self.current_extent:
            new_extent = MapExtent(
                self.current_extent.xmin - self.current_extent.width * (factor - 1) / 2,
                self.current_extent.ymin - self.current_extent.height * (factor - 1) / 2,
                self.current_extent.xmax + self.current_extent.width * (factor - 1) / 2,
                self.current_extent.ymax + self.current_extent.height * (factor - 1) / 2
            )
            self.current_extent = new_extent
            self._notify_listeners('extent_changed', self.current_extent)
            self.current_zoom -= 1
    
    def select_feature(self, x: float, y: float) -> Optional[Tuple[MapLayer, int]]:
        """Sélectionne une entité par coordonnées"""
        point = Point(x, y)
        for layer in self.layers:
            if isinstance(layer, VectorLayer) and layer.visible:
                gdf = layer.get_data()
                for idx, row in gdf.iterrows():
                    if row.geometry and row.geometry.contains(point):
                        layer.select(idx)
                        self._notify_listeners('feature_selected', layer, idx, row)
                        return (layer, idx)
        return None
    
    def clear_selection(self):
        """Efface toutes les sélections"""
        for layer in self.layers:
            if isinstance(layer, VectorLayer):
                layer.clear_selection()
        self._notify_listeners('selection_cleared')
    
    def add_measure_point(self, x: float, y: float) -> float:
        """Ajoute un point de mesure et retourne la distance cumulée"""
        self.measure_points.append((x, y))
        if len(self.measure_points) >= 2:
            total = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                total += math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
            self._notify_listeners('measure_updated', total, self.measure_points)
            return total
        return 0
    
    def clear_measure(self):
        """Efface les points de mesure"""
        self.measure_points = []
        self._notify_listeners('measure_cleared')
    
    def toggle_measure_mode(self):
        """Active/désactive le mode mesure"""
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.clear_measure()
        self._notify_listeners('measure_mode_changed', self.measure_mode)
    
    def toggle_basemap(self):
        """Active/désactive le fond de carte"""
        self.basemap_enabled = not self.basemap_enabled
        self._notify_listeners('basemap_changed', self.basemap_enabled)
    
    def add_listener(self, callback: Callable):
        """Ajoute un listener pour les événements du moteur"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """Supprime un listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, event_type: str, *args):
        """Notifie tous les listeners"""
        for callback in self._listeners:
            try:
                callback(event_type, *args)
            except Exception as e:
                print(f"Erreur listener: {e}")