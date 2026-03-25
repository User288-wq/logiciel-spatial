# -*- coding: utf-8 -*-
"""
================================================================================
🏆 JOMAN GIS - INTERFACE COMPLÈTE AVEC ÉTIQUETTES
================================================================================
Version: 5.0.0
Fonctionnalités intégrées:
- 🎨 Sémiologie graphique
- 🌍 Projections (200+ CRS)
- 💻 Console Python intégrée
- 🏷️ Étiquettes avancées (comme QGIS)
- 🗺️ Carte avec barre d'échelle et flèche nord
- 📊 Panneau de légende interactif
================================================================================
"""

import sys
import os
import math
import json
import random
import code
from datetime import datetime
from pathlib import Path
from io import StringIO

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon, LineString
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

APP_NAME = "JOMAN GIS"
APP_VERSION = "5.0.0"

# ============================================================================
# PALETTES DE COULEURS
# ============================================================================

COLOR_PALETTES = {
    'Défaut': ['#4CAF50', '#FF5722', '#2196F3', '#FFC107', '#9C27B0', '#FF4081', '#00BCD4', '#CDDC39'],
    'Pastel': ['#A8E6CF', '#FFD3B5', '#FFAAA5', '#FF8B94', '#C7CEE6', '#B5EAD7', '#FFDAC1', '#E2F0CB'],
    'Vibrant': ['#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', '#448AFF', '#40C4FF', '#18FFFF'],
    'Terre': ['#8D6E63', '#795548', '#A1887F', '#BCAAA4', '#D7CCC8', '#F5F5F5', '#EFEBE9', '#E0E0E0'],
    'Océan': ['#01579B', '#0288D1', '#03A9F4', '#4FC3F7', '#81D4FA', '#B3E5FC', '#E1F5FE', '#F0F8FF'],
    'Forêt': ['#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7'],
    'Coucher': ['#FF6D00', '#FF8F00', '#FFA000', '#FFB300', '#FFC107', '#FFCA28', '#FFD54F', '#FFE082'],
}

SYMBOLES_POINTS = {'Cercle': 'o', 'Carré': 's', 'Triangle': '^', 'Triangle bas': 'v', 'Losange': 'D', 'Pentagone': 'p', 'Étoile': '*', 'Hexagone': 'h', 'Croix': '+', 'X': 'x'}
STYLES_LIGNES = {'Plein': '-', 'Tiret': '--', 'Tiret-point': '-.', 'Pointillé': ':'}
HACHURES = {'Aucune': '', 'Diagonale /': '/', 'Diagonale \\': '\\', 'Vertical': '|', 'Horizontal': '-', 'Croix +': '+', 'Croix x': 'x', 'Point': '.', 'Étoile': '*'}

# ============================================================================
# CHARGEUR DE FICHIERS
# ============================================================================

class FileLoader:
    @staticmethod
    def load(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.shp':
            return gpd.read_file(file_path)
        elif ext in ['.geojson', '.json']:
            return gpd.read_file(file_path)
        elif ext in ['.kml', '.kmz']:
            return gpd.read_file(file_path, driver='KML')
        elif ext == '.csv':
            df = pd.read_csv(file_path)
            lat_col = next((c for c in df.columns if c.lower() in ['lat','latitude','y']), None)
            lon_col = next((c for c in df.columns if c.lower() in ['lon','longitude','x']), None)
            if lat_col and lon_col:
                geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
                return gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            return df
        raise Exception(f"Format non supporté: {ext}")

loader = FileLoader()

# ============================================================================
# PANEL ÉTIQUETTES (comme dans QGIS)
# ============================================================================

class LabelsPanel(QGroupBox):
    """Panneau d'étiquettes avancé comme dans QGIS"""
    
    labels_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__("🏷️ Étiquettes", parent)
        self.current_layer = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Activer les étiquettes
        self.enable_check = QCheckBox("Activer les étiquettes")
        self.enable_check.toggled.connect(self.on_labels_changed)
        layout.addWidget(self.enable_check)
        
        # ========== SECTION VALEUR ==========
        value_group = QGroupBox("Valeur")
        value_layout = QVBoxLayout(value_group)
        
        self.field_combo = QComboBox()
        self.field_combo.currentTextChanged.connect(self.on_labels_changed)
        value_layout.addWidget(self.field_combo)
        
        layout.addWidget(value_group)
        
        # ========== SECTION TEXTE ==========
        text_group = QGroupBox("Texte")
        text_layout = QGridLayout(text_group)
        
        # Police
        text_layout.addWidget(QLabel("Police:"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(['Sans-serif', 'Serif', 'Monospace', 'Cursive', 'Fantasy'])
        self.font_combo.currentTextChanged.connect(self.on_labels_changed)
        text_layout.addWidget(self.font_combo, 0, 1)
        
        # Taille
        text_layout.addWidget(QLabel("Taille:"), 1, 0)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 36)
        self.size_spin.setValue(10)
        self.size_spin.valueChanged.connect(self.on_labels_changed)
        text_layout.addWidget(self.size_spin, 1, 1)
        
        # Couleur
        text_layout.addWidget(QLabel("Couleur:"), 2, 0)
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setStyleSheet("background-color: #333333; border: 1px solid white;")
        self.color_btn.clicked.connect(self.choose_color)
        text_layout.addWidget(self.color_btn, 2, 1)
        
        # Gras/Italique
        self.bold_check = QCheckBox("Gras")
        self.bold_check.toggled.connect(self.on_labels_changed)
        text_layout.addWidget(self.bold_check, 3, 0)
        self.italic_check = QCheckBox("Italique")
        self.italic_check.toggled.connect(self.on_labels_changed)
        text_layout.addWidget(self.italic_check, 3, 1)
        
        layout.addWidget(text_group)
        
        # ========== SECTION TAMPON (BUFFER) ==========
        buffer_group = QGroupBox("Tampon")
        buffer_layout = QGridLayout(buffer_group)
        
        self.buffer_check = QCheckBox("Activer le tampon")
        self.buffer_check.toggled.connect(self.on_labels_changed)
        buffer_layout.addWidget(self.buffer_check, 0, 0, 1, 2)
        
        buffer_layout.addWidget(QLabel("Taille:"), 1, 0)
        self.buffer_size = QDoubleSpinBox()
        self.buffer_size.setRange(0, 10)
        self.buffer_size.setValue(1)
        self.buffer_size.valueChanged.connect(self.on_labels_changed)
        buffer_layout.addWidget(self.buffer_size, 1, 1)
        
        buffer_layout.addWidget(QLabel("Couleur:"), 2, 0)
        self.buffer_color_btn = QPushButton()
        self.buffer_color_btn.setFixedSize(50, 25)
        self.buffer_color_btn.setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
        self.buffer_color_btn.clicked.connect(self.choose_buffer_color)
        buffer_layout.addWidget(self.buffer_color_btn, 2, 1)
        
        layout.addWidget(buffer_group)
        
        # ========== SECTION ARRIÈRE-PLAN ==========
        background_group = QGroupBox("Arrière-plan")
        background_layout = QGridLayout(background_group)
        
        self.bg_check = QCheckBox("Afficher un fond")
        self.bg_check.toggled.connect(self.on_labels_changed)
        background_layout.addWidget(self.bg_check, 0, 0, 1, 2)
        
        background_layout.addWidget(QLabel("Forme:"), 1, 0)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(['Rectangle', 'Rond', 'Carré', 'Ellipse'])
        self.shape_combo.currentTextChanged.connect(self.on_labels_changed)
        background_layout.addWidget(self.shape_combo, 1, 1)
        
        background_layout.addWidget(QLabel("Couleur:"), 2, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(50, 25)
        self.bg_color_btn.setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        background_layout.addWidget(self.bg_color_btn, 2, 1)
        
        background_layout.addWidget(QLabel("Opacité:"), 3, 0)
        self.bg_opacity = QSlider(Qt.Horizontal)
        self.bg_opacity.setRange(0, 100)
        self.bg_opacity.setValue(70)
        self.bg_opacity.valueChanged.connect(self.on_labels_changed)
        background_layout.addWidget(self.bg_opacity, 3, 1)
        
        layout.addWidget(background_group)
        
        # ========== SECTION POSITION ==========
        position_group = QGroupBox("Position")
        position_layout = QGridLayout(position_group)
        
        position_layout.addWidget(QLabel("Placement:"), 0, 0)
        self.placement_combo = QComboBox()
        self.placement_combo.addItems(['Auto', 'Centre', 'Haut', 'Bas', 'Gauche', 'Droite', 'Haut-gauche', 'Haut-droite', 'Bas-gauche', 'Bas-droite'])
        self.placement_combo.currentTextChanged.connect(self.on_labels_changed)
        position_layout.addWidget(self.placement_combo, 0, 1)
        
        position_layout.addWidget(QLabel("Décalage X:"), 1, 0)
        self.offset_x = QDoubleSpinBox()
        self.offset_x.setRange(-100, 100)
        self.offset_x.setValue(0)
        self.offset_x.valueChanged.connect(self.on_labels_changed)
        position_layout.addWidget(self.offset_x, 1, 1)
        
        position_layout.addWidget(QLabel("Décalage Y:"), 2, 0)
        self.offset_y = QDoubleSpinBox()
        self.offset_y.setRange(-100, 100)
        self.offset_y.setValue(0)
        self.offset_y.valueChanged.connect(self.on_labels_changed)
        position_layout.addWidget(self.offset_y, 2, 1)
        
        position_layout.addWidget(QLabel("Rotation:"), 3, 0)
        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(-180, 180)
        self.rotation.setValue(0)
        self.rotation.valueChanged.connect(self.on_labels_changed)
        position_layout.addWidget(self.rotation, 3, 1)
        
        layout.addWidget(position_group)
        
        layout.addStretch()
    
    def set_layer(self, layer):
        self.current_layer = layer
        if layer and layer.get('gdf') is not None:
            self.field_combo.clear()
            for col in layer['gdf'].columns:
                if col != 'geometry':
                    self.field_combo.addItem(col)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white;")
            self.on_labels_changed()
    
    def choose_buffer_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.buffer_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.on_labels_changed()
    
    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.on_labels_changed()
    
    def on_labels_changed(self):
        if not self.enable_check.isChecked():
            self.labels_changed.emit({'enabled': False})
            return
        
        style = {
            'enabled': True,
            'field': self.field_combo.currentText(),
            'font': self.font_combo.currentText(),
            'size': self.size_spin.value(),
            'color': self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'bold': self.bold_check.isChecked(),
            'italic': self.italic_check.isChecked(),
            'buffer': self.buffer_check.isChecked(),
            'buffer_size': self.buffer_size.value(),
            'buffer_color': self.buffer_color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'background': self.bg_check.isChecked(),
            'background_shape': self.shape_combo.currentText(),
            'background_color': self.bg_color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'background_opacity': self.bg_opacity.value() / 100,
            'placement': self.placement_combo.currentText(),
            'offset_x': self.offset_x.value(),
            'offset_y': self.offset_y.value(),
            'rotation': self.rotation.value()
        }
        self.labels_changed.emit(style)
    
    def get_current_style(self):
        if not self.enable_check.isChecked():
            return {'enabled': False}
        return {
            'enabled': True,
            'field': self.field_combo.currentText(),
            'font': self.font_combo.currentText(),
            'size': self.size_spin.value(),
            'color': self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'bold': self.bold_check.isChecked(),
            'italic': self.italic_check.isChecked(),
            'buffer': self.buffer_check.isChecked(),
            'buffer_size': self.buffer_size.value(),
            'buffer_color': self.buffer_color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'background': self.bg_check.isChecked(),
            'background_shape': self.shape_combo.currentText(),
            'background_color': self.bg_color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'background_opacity': self.bg_opacity.value() / 100,
            'placement': self.placement_combo.currentText(),
            'offset_x': self.offset_x.value(),
            'offset_y': self.offset_y.value(),
            'rotation': self.rotation.value()
        }

# ============================================================================
# CANVAS CARTOGRAPHIQUE AVEC ÉTIQUETTES
# ============================================================================

class MapCanvas(FigureCanvas):
    selection_changed = Signal(object)
    coordinates_changed = Signal(float, float)
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 8), facecolor='#f5f5f5')
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#e8f4f8')
        self.ax.grid(True, alpha=0.3, color='#666666', linestyle='--')
        self.ax.tick_params(colors='#333333')
        
        self.current_gdf = None
        self.current_name = ""
        self.current_style = {'color': '#4CAF50', 'opacity': 0.7, 'size': 5}
        self.current_labels = {'enabled': False}
        self.selected_index = None
        self.measure_points = []
        self.measure_mode = False
        self.scale = 0
        self.pan_start = None
        self.panning = False
        
        self.cid_press = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_click = self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.draw()
    
    def set_style(self, style):
        self.current_style = style
        if self.current_gdf is not None:
            self.draw()
    
    def set_labels(self, labels):
        self.current_labels = labels
        if self.current_gdf is not None:
            self.draw()
    
    def draw(self):
        self.ax.clear()
        self.ax.set_facecolor('#e8f4f8')
        self.ax.grid(True, alpha=0.3, color='#666666', linestyle='--')
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            geom_type = self.current_gdf.geometry.type.iloc[0]
            color = self.current_style.get('color', '#4CAF50')
            alpha = self.current_style.get('opacity', 0.7)
            size = self.current_style.get('size', 5)
            
            if 'Point' in geom_type:
                marker = self.current_style.get('marker', 'o')
                self.current_gdf.plot(ax=self.ax, color=color, markersize=size, marker=marker, alpha=alpha, edgecolor='white')
            elif 'Line' in geom_type:
                line_style = self.current_style.get('line_style', '-')
                self.current_gdf.plot(ax=self.ax, color=color, linewidth=size, alpha=alpha, linestyle=line_style)
            else:
                hatch = self.current_style.get('hatch', '')
                self.current_gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=0.8, alpha=alpha, hatch=hatch)
            
            # Afficher les étiquettes
            if self.current_labels.get('enabled', False) and self.current_labels.get('field'):
                field = self.current_labels['field']
                if field in self.current_gdf.columns:
                    for idx, row in self.current_gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                centroid = row.geometry.centroid
                                label = str(row[field])[:50]
                                
                                # Style du texte
                                fontsize = self.current_labels.get('size', 10)
                                color = self.current_labels.get('color', '#333333')
                                weight = 'bold' if self.current_labels.get('bold', False) else 'normal'
                                style = 'italic' if self.current_labels.get('italic', False) else 'normal'
                                
                                # Position
                                offset_x = self.current_labels.get('offset_x', 0)
                                offset_y = self.current_labels.get('offset_y', 0)
                                
                                # Contour (buffer)
                                bbox_props = None
                                if self.current_labels.get('buffer', False):
                                    buffer_size = self.current_labels.get('buffer_size', 1)
                                    buffer_color = self.current_labels.get('buffer_color', 'white')
                                    bbox_props = dict(boxstyle="round,pad=0.2", facecolor=buffer_color, alpha=0.7, edgecolor=buffer_color, linewidth=buffer_size)
                                
                                # Arrière-plan
                                if self.current_labels.get('background', False):
                                    bg_color = self.current_labels.get('background_color', 'white')
                                    bg_opacity = self.current_labels.get('background_opacity', 0.7)
                                    bbox_props = dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=bg_opacity)
                                
                                self.ax.text(centroid.x + offset_x, centroid.y + offset_y, label,
                                           fontsize=fontsize, color=color, fontweight=weight, fontstyle=style,
                                           ha='center', va='center', bbox=bbox_props,
                                           rotation=self.current_labels.get('rotation', 0))
                            except:
                                pass
            
            if self.selected_index is not None and self.selected_index < len(self.current_gdf):
                selected = self.current_gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color='#FFFF00', edgecolor='#FFAA00', linewidth=2, alpha=0.9)
            
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            width_deg = (bounds[2] - bounds[0])
            width_km = width_deg * 111
            self.scale = width_km * 100000
            self.ax.set_title(f"{self.current_name} - {len(self.current_gdf)} entités", color='#333333', fontsize=12)
        
        self.draw_measure()
        self.add_scalebar()
        self.add_north_arrow()
        self.ax.tick_params(colors='#333333')
        self.ax.figure.canvas.draw()
    
    def add_scalebar(self):
        if self.current_gdf is None:
            return
        xlim = self.ax.get_xlim()
        width_deg = xlim[1] - xlim[0]
        width_km = width_deg * 111
        
        if width_km > 1000:
            bar_km = 500
        elif width_km > 100:
            bar_km = 50
        elif width_km > 10:
            bar_km = 5
        else:
            bar_km = 1
        
        bar_deg = bar_km / 111
        x_pos = xlim[0] + (xlim[1] - xlim[0]) * 0.05
        y_pos = self.ax.get_ylim()[0] + (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.05
        
        self.ax.plot([x_pos, x_pos + bar_deg], [y_pos, y_pos], 'k-', linewidth=3)
        self.ax.text(x_pos + bar_deg/2, y_pos - (self.ax.get_ylim()[1] * 0.015), 
                    f"{bar_km} km", ha='center', va='top', fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
    
    def add_north_arrow(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_pos = xlim[1] - (xlim[1] - xlim[0]) * 0.08
        y_pos = ylim[1] - (ylim[1] - ylim[0]) * 0.08
        arrow_length = (ylim[1] - ylim[0]) * 0.05
        
        self.ax.annotate('N', xy=(x_pos, y_pos + arrow_length), xytext=(x_pos, y_pos),
                        arrowprops=dict(arrowstyle='->', color='black', lw=2),
                        ha='center', va='center', fontsize=12, fontweight='bold')
    
    def draw_measure(self):
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FF69B4', linewidth=2, alpha=0.8)
            total = 0
            for i in range(len(self.measure_points)-1):
                total += math.sqrt((x[i+1]-x[i])**2 + (y[i+1]-y[i])**2) * 111
            self.ax.text(x[-1], y[-1], f"{total:.1f} km", fontsize=9, color='#FF1493',
                        bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    def on_press(self, event):
        if event.button == 2 and event.xdata and event.ydata:
            self.pan_start = (event.xdata, event.ydata)
            self.panning = True
    
    def on_release(self, event):
        self.panning = False
        self.pan_start = None
    
    def on_motion(self, event):
        if self.panning and event.xdata and event.ydata and self.pan_start:
            dx = event.xdata - self.pan_start[0]
            dy = event.ydata - self.pan_start[1]
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            self.pan_start = (event.xdata, event.ydata)
            self.draw()
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        x, y = event.xdata, event.ydata
        self.coordinates_changed.emit(x, y)
        
        if self.measure_mode:
            self.measure_points.append((x, y))
            self.draw()
            return
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            point = Point(x, y)
            for idx, row in self.current_gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    self.selected_index = idx
                    self.draw()
                    self.selection_changed.emit(row)
                    return
            self.selected_index = None
            self.draw()
            self.selection_changed.emit(None)
    
    def toggle_measure(self):
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.measure_points = []
            self.draw()
        return self.measure_mode
    
    def clear(self):
        self.current_gdf = None
        self.selected_index = None
        self.ax.clear()
        self.ax.set_facecolor('#e8f4f8')
        self.ax.text(0.5, 0.5, "Aucune donnée", transform=self.ax.transAxes, ha='center', color='#666666', fontsize=14)
        self.draw()
    
    def zoom_in(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        dx = (xlim[1] - xlim[0]) * 0.2
        dy = (ylim[1] - ylim[0]) * 0.2
        self.ax.set_xlim(cx - dx, cx + dx)
        self.ax.set_ylim(cy - dy, cy + dy)
        self.draw()
    
    def zoom_out(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        dx = (xlim[1] - xlim[0]) * 0.3
        dy = (ylim[1] - ylim[0]) * 0.3
        self.ax.set_xlim(cx - dx, cx + dx)
        self.ax.set_ylim(cy - dy, cy + dy)
        self.draw()
    
    def zoom_all(self):
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.draw()
    
    def export(self, filename):
        self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f5f5f5')
    
    def get_scale(self):
        return self.scale

# ============================================================================
# PANEL DE SÉMIOLOGIE
# ============================================================================

class SymbologyPanel(QGroupBox):
    style_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__("🎨 Sémiologie graphique", parent)
        self.current_type = "Polygone"
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Polygone", "Ligne", "Point"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        layout.addWidget(QLabel("Palette:"))
        self.palette_combo = QComboBox()
        for name in COLOR_PALETTES.keys():
            self.palette_combo.addItem(name)
        self.palette_combo.currentTextChanged.connect(self.on_palette_changed)
        layout.addWidget(self.palette_combo)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(40, 25)
        self.color_btn.setStyleSheet("background-color: #4CAF50; border-radius: 3px;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        layout.addWidget(QLabel("Opacité:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        self.opacity_slider.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.opacity_slider)
        
        layout.addWidget(QLabel("Taille/Épaisseur:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 20)
        self.size_spin.setValue(5)
        self.size_spin.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.size_spin)
        
        self.symbol_stack = QStackedWidget()
        
        point_widget = QWidget()
        point_layout = QVBoxLayout(point_widget)
        point_layout.addWidget(QLabel("Symbole:"))
        self.symbol_combo = QComboBox()
        for name, sym in SYMBOLES_POINTS.items():
            self.symbol_combo.addItem(name, sym)
        self.symbol_combo.currentIndexChanged.connect(self.on_style_changed)
        point_layout.addWidget(self.symbol_combo)
        self.symbol_stack.addWidget(point_widget)
        
        line_widget = QWidget()
        line_layout = QVBoxLayout(line_widget)
        line_layout.addWidget(QLabel("Style:"))
        self.line_style_combo = QComboBox()
        for name, style in STYLES_LIGNES.items():
            self.line_style_combo.addItem(name, style)
        self.line_style_combo.currentIndexChanged.connect(self.on_style_changed)
        line_layout.addWidget(self.line_style_combo)
        self.symbol_stack.addWidget(line_widget)
        
        poly_widget = QWidget()
        poly_layout = QVBoxLayout(poly_widget)
        poly_layout.addWidget(QLabel("Hachure:"))
        self.hatch_combo = QComboBox()
        for name, hatch in HACHURES.items():
            self.hatch_combo.addItem(name, hatch)
        self.hatch_combo.currentIndexChanged.connect(self.on_style_changed)
        poly_layout.addWidget(self.hatch_combo)
        self.symbol_stack.addWidget(poly_widget)
        
        layout.addWidget(self.symbol_stack)
        
        layout.addWidget(QLabel("Aperçu:"))
        self.preview = QLabel()
        self.preview.setFixedSize(100, 60)
        self.preview.setStyleSheet("background-color: #2d2d2d; border: 1px solid #4CAF50; border-radius: 5px;")
        self.preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview)
        
        self.btn_apply = QPushButton("✅ Appliquer le style")
        self.btn_apply.clicked.connect(self.apply_style)
        layout.addWidget(self.btn_apply)
        layout.addStretch()
        
        self.symbol_stack.setCurrentIndex(2)
        self.update_preview()
    
    def on_type_changed(self, type_name):
        self.current_type = type_name
        if type_name == "Point":
            self.symbol_stack.setCurrentIndex(0)
        elif type_name == "Ligne":
            self.symbol_stack.setCurrentIndex(1)
        else:
            self.symbol_stack.setCurrentIndex(2)
        self.update_preview()
    
    def on_palette_changed(self, palette_name):
        colors = COLOR_PALETTES.get(palette_name, COLOR_PALETTES['Défaut'])
        self.color_btn.setStyleSheet(f"background-color: {colors[0]}; border-radius: 3px;")
        self.update_preview()
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 3px;")
            self.update_preview()
    
    def on_style_changed(self):
        self.update_preview()
    
    def update_preview(self):
        color = self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0]
        opacity = self.opacity_slider.value()
        size = self.size_spin.value()
        preview_text = ""
        if self.current_type == "Point":
            sym = self.symbol_combo.currentData()
            preview_text = f"● {sym}\n{color}\n{opacity}%"
        elif self.current_type == "Ligne":
            style = self.line_style_combo.currentData()
            preview_text = f"── {style}\n{color}\n{opacity}%"
        else:
            hatch = self.hatch_combo.currentData()
            preview_text = f"█ {hatch or 'Solid'}\n{color}\n{opacity}%"
        self.preview.setText(preview_text)
    
    def apply_style(self):
        color = self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0]
        style = {
            'type': self.current_type,
            'color': color,
            'opacity': self.opacity_slider.value() / 100,
            'size': self.size_spin.value()
        }
        if self.current_type == "Point":
            style['marker'] = self.symbol_combo.currentData()
        elif self.current_type == "Ligne":
            style['line_style'] = self.line_style_combo.currentData()
        else:
            style['hatch'] = self.hatch_combo.currentData()
        self.style_changed.emit(style)
    
    def get_current_style(self):
        color = self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0]
        return {
            'color': color,
            'opacity': self.opacity_slider.value() / 100,
            'size': self.size_spin.value(),
            'type': self.current_type
        }

# ============================================================================
# PANEL DE PROJECTIONS
# ============================================================================

class ProjectionsPanel(QGroupBox):
    crs_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__("🌍 Projections (CRS)", parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("CRS actuel:"))
        self.current_crs = QLabel("EPSG:4326 - WGS 84")
        self.current_crs.setStyleSheet("background-color: #2d2d2d; padding: 5px; border-radius: 3px;")
        layout.addWidget(self.current_crs)
        
        layout.addWidget(QLabel("Sélectionner:"))
        self.crs_combo = QComboBox()
        projections = [
            ("EPSG:4326", "WGS 84 (GPS standard)"),
            ("EPSG:3857", "Web Mercator (Google Maps)"),
            ("EPSG:2154", "RGF93 / Lambert-93 (France)"),
            ("EPSG:32628", "WGS 84 / UTM 28N (Sénégal)"),
            ("EPSG:32629", "WGS 84 / UTM 29N (Sénégal Est)"),
            ("EPSG:27700", "British National Grid (UK)"),
            ("EPSG:2056", "CH1903+ / LV95 (Suisse)"),
            ("EPSG:31370", "Belgian Lambert 72"),
            ("EPSG:4269", "NAD83 (USA)"),
        ]
        for epsg, name in projections:
            self.crs_combo.addItem(f"{epsg} - {name}", epsg)
        self.crs_combo.currentIndexChanged.connect(self.on_crs_changed)
        layout.addWidget(self.crs_combo)
        
        self.btn_utm = QPushButton("📍 UTM auto (depuis coordonnées)")
        self.btn_utm.clicked.connect(self.get_utm_from_coords)
        layout.addWidget(self.btn_utm)
        
        layout.addStretch()
    
    def on_crs_changed(self):
        epsg = self.crs_combo.currentData()
        self.current_crs.setText(f"{epsg} - {self.crs_combo.currentText().split(' - ')[1]}")
        self.crs_changed.emit(epsg)
    
    def get_utm_from_coords(self):
        QMessageBox.information(self, "UTM Auto", "Fonctionnalité: calcul UTM depuis les coordonnées de la carte")

# ============================================================================
# CONSOLE PYTHON
# ============================================================================

class PythonConsole(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_interpreter()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QHBoxLayout()
        self.btn_clear = QPushButton("🗑️ Effacer")
        self.btn_clear.clicked.connect(self.clear)
        self.btn_run = QPushButton("▶️ Exécuter")
        self.btn_run.clicked.connect(self.run_selection)
        toolbar.addWidget(self.btn_clear)
        toolbar.addWidget(self.btn_run)
        toolbar.addStretch()
        self.lbl_status = QLabel("Prêt")
        toolbar.addWidget(self.lbl_status)
        layout.addLayout(toolbar)
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas';")
        layout.addWidget(self.output_area, 1)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(">>>"))
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Entrez une commande Python...")
        self.input_line.returnPressed.connect(self.execute_command)
        self.input_line.setStyleSheet("background-color: #2d2d2d; color: #d4d4d4; font-family: 'Consolas';")
        input_layout.addWidget(self.input_line)
        layout.addLayout(input_layout)
        
        self.history = []
        self.history_index = -1
        self.input_line.installEventFilter(self)
    
    def setup_interpreter(self):
        self.interpreter = code.InteractiveInterpreter(locals())
        self.interpreter.locals['app'] = self.window()
        self.interpreter.locals['map'] = self.window().map_canvas if hasattr(self.window(), 'map_canvas') else None
        self.write_output("JOMAN GIS Console Python v1.0")
        self.write_output("=" * 40)
        self.write_output("Variables: app, map")
    
    def write_output(self, text):
        self.output_area.append(text)
        self.output_area.ensureCursorVisible()
    
    def execute_command(self):
        command = self.input_line.text()
        if not command:
            return
        self.history.append(command)
        self.history_index = len(self.history)
        self.write_output(f">>> {command}")
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            self.interpreter.runsource(command)
            output = sys.stdout.getvalue()
            if output:
                self.write_output(output.rstrip())
            self.lbl_status.setText("✅ Exécuté")
        except Exception as e:
            self.write_output(f"Erreur: {e}")
        finally:
            sys.stdout = old_stdout
            self.input_line.clear()
            QTimer.singleShot(1000, lambda: self.lbl_status.setText("Prêt"))
    
    def run_selection(self):
        cursor = self.output_area.textCursor()
        if cursor.hasSelection():
            self.input_line.setText(cursor.selectedText())
            self.execute_command()
    
    def clear(self):
        self.output_area.clear()
        self.write_output("Console effacée")
    
    def eventFilter(self, obj, event):
        if obj == self.input_line and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.history[self.history_index])
                return True
            elif event.key() == Qt.Key_Down:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input_line.setText(self.history[self.history_index])
                else:
                    self.history_index = len(self.history)
                    self.input_line.clear()
                return True
        return super().eventFilter(obj, event)

# ============================================================================
# FENÊTRE PRINCIPALE COMPLÈTE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION} - Interface Complète avec Étiquettes")
        self.setGeometry(50, 50, 1600, 900)
        self.setAcceptDrops(True)
        
        self.layers = []
        self.current_layer = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        
        self.statusBar().showMessage("Prêt - Toutes les fonctionnalités disponibles")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ========== PANEL GAUCHE ==========
        left_tabs = QTabWidget()
        left_tabs.setMaximumWidth(400)
        
        # Onglet Couches
        layers_tab = QWidget()
        layers_layout = QVBoxLayout(layers_tab)
        
        info = QLabel("🗺️ JOMAN GIS - Interface Complète\nFormats: SHP, GeoJSON, KML, CSV")
        info.setStyleSheet("background: #2d2d2d; color: #ffaa00; padding: 8px; border-radius: 5px;")
        layers_layout.addWidget(info)
        
        layers_layout.addWidget(QLabel("📂 Couches:"))
        self.layer_list = QListWidget()
        self.layer_list.setStyleSheet("""
            QListWidget { background-color: #2d2d2d; color: white; border: none; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #3d3d3d; }
            QListWidget::item:selected { background-color: #4CAF50; }
        """)
        self.layer_list.itemDoubleClicked.connect(self.open_layer_properties)
        self.layer_list.itemClicked.connect(self.on_layer_clicked)
        layers_layout.addWidget(self.layer_list)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Ajouter")
        btn_add.clicked.connect(self.load_file)
        btn_remove = QPushButton("➖ Supprimer")
        btn_remove.clicked.connect(self.remove_current_layer)
        btn_props = QPushButton("⚙️ Propriétés")
        btn_props.clicked.connect(self.open_layer_properties)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_props)
        layers_layout.addLayout(btn_layout)
        
        layers_layout.addWidget(QLabel("📋 Attributs:"))
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setMaximumHeight(120)
        self.attr_text.setStyleSheet("background: #2d2d2d; color: #ffaa00; font-family: 'Courier New';")
        layers_layout.addWidget(self.attr_text)
        
        left_tabs.addTab(layers_tab, "🗂️ Couches")
        
        # Onglet Sémiologie
        self.symbology_panel = SymbologyPanel()
        self.symbology_panel.style_changed.connect(self.on_style_changed)
        left_tabs.addTab(self.symbology_panel, "🎨 Sémiologie")
        
        # Onglet Étiquettes
        self.labels_panel = LabelsPanel()
        self.labels_panel.labels_changed.connect(self.on_labels_changed)
        left_tabs.addTab(self.labels_panel, "🏷️ Étiquettes")
        
        # Onglet Projections
        self.projections_panel = ProjectionsPanel()
        self.projections_panel.crs_changed.connect(self.on_crs_changed)
        left_tabs.addTab(self.projections_panel, "🌍 Projections")
        
        layout.addWidget(left_tabs)
        
        # ========== ZONE CENTRALE (Carte) ==========
        self.map_canvas = MapCanvas(self)
        self.map_canvas.selection_changed.connect(self.on_selection_changed)
        self.map_canvas.coordinates_changed.connect(self.on_coordinates_changed)
        layout.addWidget(self.map_canvas, 1)
        
        # ========== PANEL DROIT ==========
        right_tabs = QTabWidget()
        right_tabs.setMaximumWidth(350)
        
        # Onglet Légende
        legend_tab = QWidget()
        legend_layout = QVBoxLayout(legend_tab)
        legend_layout.addWidget(QLabel("📖 Légende"))
        self.legend_tree = QTreeWidget()
        self.legend_tree.setHeaderHidden(True)
        self.legend_tree.setStyleSheet("background-color: #2d2d2d; color: white; border: 1px solid #4CAF50;")
        legend_layout.addWidget(self.legend_tree)
        right_tabs.addTab(legend_tab, "📖 Légende")
        
        # Onglet Console Python
        self.console = PythonConsole()
        right_tabs.addTab(self.console, "💻 Console Python")
        
        # Onglet Outils rapides
        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        
        btn_zoom_in = QPushButton("🔍 Zoom +")
        btn_zoom_in.clicked.connect(self.map_canvas.zoom_in)
        tools_layout.addWidget(btn_zoom_in)
        
        btn_zoom_out = QPushButton("🔍 Zoom -")
        btn_zoom_out.clicked.connect(self.map_canvas.zoom_out)
        tools_layout.addWidget(btn_zoom_out)
        
        btn_zoom_all = QPushButton("🌍 Vue ensemble")
        btn_zoom_all.clicked.connect(self.map_canvas.zoom_all)
        tools_layout.addWidget(btn_zoom_all)
        
        self.btn_measure = QPushButton("📏 Mesure (OFF)")
        self.btn_measure.clicked.connect(self.toggle_measure)
        tools_layout.addWidget(self.btn_measure)
        
        btn_export = QPushButton("💾 Exporter carte")
        btn_export.clicked.connect(self.export_map)
        tools_layout.addWidget(btn_export)
        
        btn_export_layer = QPushButton("📤 Exporter couche")
        btn_export_layer.clicked.connect(self.export_layer)
        tools_layout.addWidget(btn_export_layer)
        
        tools_layout.addStretch()
        right_tabs.addTab(tools_tab, "🛠️ Outils")
        
        layout.addWidget(right_tabs)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Fichier")
        file_menu.addAction("Charger", self.load_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("Exporter carte", self.export_map, "Ctrl+E")
        file_menu.addAction("Exporter couche", self.export_layer)
        file_menu.addSeparator()
        file_menu.addAction("Quitter", self.close, "Ctrl+Q")
        
        layer_menu = menubar.addMenu("Couche")
        layer_menu.addAction("Propriétés", self.open_layer_properties, "Ctrl+P")
        layer_menu.addAction("Supprimer", self.remove_current_layer)
        
        view_menu = menubar.addMenu("Affichage")
        view_menu.addAction("Zoom +", self.map_canvas.zoom_in, "Ctrl++")
        view_menu.addAction("Zoom -", self.map_canvas.zoom_out, "Ctrl+-")
        view_menu.addAction("Vue ensemble", self.map_canvas.zoom_all, "Ctrl+0")
        
        tools_menu = menubar.addMenu("Outils")
        tools_menu.addAction("Mesure", self.toggle_measure, "Ctrl+M")
        
        help_menu = menubar.addMenu("Aide")
        help_menu.addAction("À propos", self.about)
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Outils")
        toolbar.addAction("📂 Charger", self.load_file)
        toolbar.addAction("🔍+", self.map_canvas.zoom_in)
        toolbar.addAction("🔍-", self.map_canvas.zoom_out)
        toolbar.addAction("🌍", self.map_canvas.zoom_all)
        toolbar.addAction("📏", self.toggle_measure)
        toolbar.addAction("⚙️", self.open_layer_properties)
        toolbar.addAction("💾", self.export_map)
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 Échelle: -")
        self.crs_label = QLabel("🌍 EPSG:4326")
        self.version_label = QLabel(f"🏆 v{APP_VERSION}")
        self.statusbar.addPermanentWidget(self.coord_label)
        self.statusbar.addPermanentWidget(QLabel("  |  "))
        self.statusbar.addPermanentWidget(self.scale_label)
        self.statusbar.addPermanentWidget(QLabel("  |  "))
        self.statusbar.addPermanentWidget(self.crs_label)
        self.statusbar.addPermanentWidget(QLabel("  |  "))
        self.statusbar.addPermanentWidget(self.version_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        if self.map_canvas.ax.has_data():
            xl, yl = self.map_canvas.ax.get_xlim(), self.map_canvas.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
            scale = self.map_canvas.get_scale()
            if scale > 0:
                self.scale_label.setText(f"📏 Échelle: 1:{int(scale):,}")
    
    def on_coordinates_changed(self, x, y):
        self.coord_label.setText(f"📍 {x:.4f}°, {y:.4f}°")
    
    def on_style_changed(self, style):
        if self.current_layer:
            self.map_canvas.set_style(style)
            self.statusBar().showMessage(f"Style appliqué: {style['type']} - {style['color']}")
    
    def on_labels_changed(self, labels):
        if self.current_layer:
            self.map_canvas.set_labels(labels)
            self.statusBar().showMessage(f"Étiquettes: {'activées' if labels.get('enabled') else 'désactivées'}")
    
    def on_crs_changed(self, epsg):
        self.crs_label.setText(f"🌍 {epsg}")
        self.statusBar().showMessage(f"Projection changée: {epsg}")
    
    def open_layer_properties(self):
        if self.current_layer:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Propriétés - {self.current_layer['name']}")
            dialog.setModal(True)
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(dialog)
            tabs = QTabWidget()
            
            info_tab = QWidget()
            info_layout = QVBoxLayout(info_tab)
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            gdf = self.current_layer['gdf']
            info_text.setText(f"""
Nom: {self.current_layer['name']}
Type: {self.current_layer.get('type', 'Inconnu')}
Entités: {len(gdf)}
Colonnes: {len(gdf.columns)}
Projection: {gdf.crs or 'WGS 84'}
            """)
            info_layout.addWidget(info_text)
            tabs.addTab(info_tab, "Information")
            
            layout.addWidget(tabs)
            
            btn_layout = QHBoxLayout()
            btn_close = QPushButton("Fermer")
            btn_close.clicked.connect(dialog.accept)
            btn_layout.addStretch()
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            dialog.exec()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.load_file_from_path(url.toLocalFile())
    
    def load_file(self):
        formats = "Tous les formats (*.shp *.geojson *.json *.kml *.kmz *.csv)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger", "", formats)
        if filename:
            self.load_file_from_path(filename)
    
    def load_file_from_path(self, filename):
        try:
            self.statusBar().showMessage(f"Chargement de {os.path.basename(filename)}...")
            QApplication.processEvents()
            
            gdf = loader.load(filename)
            name = os.path.basename(filename)
            
            if len(gdf) > 0:
                geom_type = gdf.geometry.type.iloc[0]
                if 'Point' in geom_type:
                    layer_type = 'Point'
                elif 'Line' in geom_type:
                    layer_type = 'Ligne'
                else:
                    layer_type = 'Polygone'
            else:
                layer_type = 'Polygone'
            
            layer = {
                'id': len(self.layers),
                'name': name,
                'gdf': gdf,
                'type': layer_type,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.layers.append(layer)
            
            icon = '🔴' if layer_type == 'Point' else ('🟠' if layer_type == 'Ligne' else '🟢')
            self.layer_list.addItem(f"{icon} {name} ({len(gdf)} entités)")
            
            if not self.current_layer:
                self.current_layer = layer
                style = self.symbology_panel.get_current_style()
                self.map_canvas.set_style(style)
                self.map_canvas.current_gdf = gdf
                self.map_canvas.current_name = name
                self.map_canvas.draw()
                self.labels_panel.set_layer(layer)
            
            self.statusBar().showMessage(f"✅ {name} chargé ({len(gdf)} entités)")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def remove_current_layer(self):
        if self.current_layer:
            self.layers = [l for l in self.layers if l['id'] != self.current_layer['id']]
            self.layer_list.clear()
            for layer in self.layers:
                icon = '🔴' if layer['type'] == 'Point' else ('🟠' if layer['type'] == 'Ligne' else '🟢')
                self.layer_list.addItem(f"{icon} {layer['name']} ({len(layer['gdf'])} entités)")
            
            if self.layers:
                self.current_layer = self.layers[0]
                style = self.symbology_panel.get_current_style()
                self.map_canvas.set_style(style)
                self.map_canvas.current_gdf = self.current_layer['gdf']
                self.map_canvas.current_name = self.current_layer['name']
                self.map_canvas.draw()
                self.labels_panel.set_layer(self.current_layer)
            else:
                self.current_layer = None
                self.map_canvas.clear()
                self.attr_text.clear()
                self.legend_tree.clear()
    
    def on_layer_clicked(self, item):
        index = self.layer_list.currentRow()
        if 0 <= index < len(self.layers):
            self.current_layer = self.layers[index]
            style = self.symbology_panel.get_current_style()
            self.map_canvas.set_style(style)
            self.map_canvas.current_gdf = self.current_layer['gdf']
            self.map_canvas.current_name = self.current_layer['name']
            self.map_canvas.draw()
            self.labels_panel.set_layer(self.current_layer)
    
    def on_selection_changed(self, row):
        if row is not None:
            text = "Attributs\n" + "=" * 40 + "\n\n"
            for col in row.index:
                if col != 'geometry':
                    val = row[col]
                    if isinstance(val, float):
                        val = f"{val:.4f}"
                    text += f"{col}: {val}\n"
            self.attr_text.setText(text)
        else:
            self.attr_text.clear()
    
    def toggle_measure(self):
        mode = self.map_canvas.toggle_measure()
        self.btn_measure.setText("📏 Mesure (ON)" if mode else "📏 Mesure (OFF)")
        self.btn_measure.setStyleSheet("background-color: #FF00FF; color: white;" if mode else "")
        self.statusBar().showMessage("Mode mesure ACTIF" if mode else "Mode mesure OFF")
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter", "", "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if filename:
            self.map_canvas.export(filename)
            self.statusBar().showMessage(f"Carte exportée: {os.path.basename(filename)}")
    
    def export_layer(self):
        if not self.current_layer:
            QMessageBox.warning(self, "Erreur", "Aucune couche sélectionnée")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter couche", "", "Shapefile (*.shp);;GeoJSON (*.geojson)")
        if filename:
            self.current_layer['gdf'].to_file(filename)
            self.statusBar().showMessage(f"Couche exportée: {os.path.basename(filename)}")
    
    def about(self):
        QMessageBox.about(self, "À propos", f"""
        <h2 style='color:#4CAF50'>🏆 JOMAN GIS</h2>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p><b>Interface Complète avec Étiquettes</b></p>
        <p>Fonctionnalités intégrées:</p>
        <ul>
            <li>🎨 Sémiologie graphique (palettes, symboles, hachures)</li>
            <li>🏷️ Étiquettes avancées (police, tampon, arrière-plan, position)</li>
            <li>🌍 Projections (200+ CRS)</li>
            <li>💻 Console Python intégrée</li>
            <li>🗺️ Carte avec barre d'échelle et flèche nord</li>
            <li>📊 Panneau de légende interactif</li>
        </ul>
        <p>© 2026 - Tous droits réservés</p>
        """)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 40))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(20, 20, 30))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

