# -*- coding: utf-8 -*-
"""
JOMAN GIS - Interface Claire et Lisible
Avec panneau de propriétés complet
"""

import sys
import os
import math
import code
from datetime import datetime
from io import StringIO

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

APP_NAME = "JOMAN GIS"
APP_VERSION = "5.0.0"

# ============================================================================
# STYLES CLAIRS ET LISIBLES
# ============================================================================

STYLESHEET = """
QMainWindow {
    background-color: #2b2b2b;
}
QMenuBar {
    background-color: #3c3c3c;
    color: #ffffff;
}
QMenuBar::item:selected {
    background-color: #4CAF50;
}
QMenu {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555;
}
QMenu::item:selected {
    background-color: #4CAF50;
}
QToolBar {
    background-color: #3c3c3c;
    border: none;
    spacing: 3px;
}
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:pressed {
    background-color: #3d8c40;
}
QListWidget, QTreeWidget, QTableWidget {
    background-color: #3c3c3c;
    color: #ffffff;
    border: 1px solid #555;
    outline: none;
    font-size: 12px;
}
QListWidget::item, QTreeWidget::item {
    padding: 6px;
    border-bottom: 1px solid #4a4a4a;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #4CAF50;
    color: white;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #4a4a4a;
}
QGroupBox {
    font-weight: bold;
    color: #4CAF50;
    border: 1px solid #555;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}
QLabel {
    color: #dddddd;
    font-size: 12px;
}
QTextEdit, QLineEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
    font-size: 12px;
}
QTabWidget::pane {
    border: 1px solid #555;
    background-color: #2b2b2b;
}
QTabBar::tab {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #4CAF50;
    color: white;
}
QTabBar::tab:hover:!selected {
    background-color: #4a4a4a;
}
QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #4CAF50;
    border-radius: 6px;
    min-height: 20px;
}
QStatusBar {
    background-color: #3c3c3c;
    color: #dddddd;
}
QDialog {
    background-color: #2b2b2b;
}
QDoubleSpinBox, QSpinBox, QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
}
QCheckBox {
    color: #dddddd;
}
QSlider::groove:horizontal {
    height: 6px;
    background-color: #3c3c3c;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background-color: #4CAF50;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
"""

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
        raise Exception(f"Format non supporte: {ext}")

loader = FileLoader()

# ============================================================================
# CANVAS CARTOGRAPHIQUE
# ============================================================================

class MapCanvas(FigureCanvas):
    selection_changed = Signal(object)
    coordinates_changed = Signal(float, float)
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 8), facecolor='#2b2b2b')
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#3c3c3c')
        self.ax.grid(True, alpha=0.3, color='#888888', linestyle='--')
        self.ax.tick_params(colors='#dddddd')
        
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
        
        self.draw_welcome()
    
    def draw_welcome(self):
        self.ax.clear()
        self.ax.set_facecolor('#3c3c3c')
        self.ax.text(0.5, 0.5, "JOMAN GIS\n\nCliquez sur 'Ajouter' pour charger des donnees\n\nFormats: SHP, GeoJSON, KML, KMZ, CSV", 
                    transform=self.ax.transAxes, ha='center', va='center', 
                    color='#dddddd', fontsize=14)
        self.ax.set_title("JOMAN GIS - Logiciel de Cartographie", color='#4CAF50', fontsize=14)
        self.draw()
    
    def draw_layer(self, gdf, name, style=None):
        self.current_gdf = gdf
        self.current_name = name
        if style:
            self.current_style = style
        
        self.ax.clear()
        self.ax.set_facecolor('#3c3c3c')
        self.ax.grid(True, alpha=0.3, color='#888888', linestyle='--')
        
        if gdf is not None and len(gdf) > 0:
            color = self.current_style.get('color', '#4CAF50')
            alpha = self.current_style.get('opacity', 0.7)
            size = self.current_style.get('size', 5)
            geom_type = gdf.geometry.type.iloc[0]
            
            if 'Point' in geom_type:
                marker = self.current_style.get('marker', 'o')
                gdf.plot(ax=self.ax, color=color, markersize=size, marker=marker, alpha=alpha, edgecolor='white')
            elif 'Line' in geom_type:
                line_style = self.current_style.get('line_style', '-')
                gdf.plot(ax=self.ax, color=color, linewidth=size, alpha=alpha, linestyle=line_style)
            else:
                hatch = self.current_style.get('hatch', '')
                gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=0.8, alpha=alpha, hatch=hatch)
            
            # Etiquettes
            if self.current_labels.get('enabled', False) and self.current_labels.get('field'):
                field = self.current_labels['field']
                if field in gdf.columns:
                    for idx, row in gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                centroid = row.geometry.centroid
                                label = str(row[field])[:30]
                                self.ax.text(centroid.x, centroid.y, label,
                                           fontsize=self.current_labels.get('size', 10),
                                           color=self.current_labels.get('color', '#ffffff'),
                                           ha='center', va='center',
                                           bbox=dict(boxstyle="round,pad=0.2", facecolor='#2b2b2b', alpha=0.7))
                            except:
                                pass
            
            if self.selected_index is not None and self.selected_index < len(gdf):
                selected = gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color='#FFD700', edgecolor='#FFA500', linewidth=2, alpha=0.9)
            
            bounds = gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            if margin_x == 0:
                margin_x = 1
            if margin_y == 0:
                margin_y = 1
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            width_deg = (bounds[2] - bounds[0])
            width_km = width_deg * 111
            self.scale = width_km * 100000
            self.ax.set_title(f"{name} - {len(gdf)} entites", color='#dddddd', fontsize=12)
        
        self.draw_measure()
        self.add_scalebar()
        self.add_north_arrow()
        self.draw()
    
    def add_scalebar(self):
        if self.current_gdf is None or len(self.current_gdf) == 0:
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
        
        self.ax.plot([x_pos, x_pos + bar_deg], [y_pos, y_pos], 'white', linewidth=3)
        self.ax.text(x_pos + bar_deg/2, y_pos - (self.ax.get_ylim()[1] * 0.015), 
                    f"{bar_km} km", ha='center', va='top', fontsize=9, color='white',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='#2b2b2b', alpha=0.7))
    
    def add_north_arrow(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_pos = xlim[1] - (xlim[1] - xlim[0]) * 0.08
        y_pos = ylim[1] - (ylim[1] - ylim[0]) * 0.08
        arrow_length = (ylim[1] - ylim[0]) * 0.05
        self.ax.annotate('N', xy=(x_pos, y_pos + arrow_length), xytext=(x_pos, y_pos),
                        arrowprops=dict(arrowstyle='->', color='white', lw=2),
                        ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    def draw_measure(self):
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FF69B4', linewidth=2, alpha=0.8)
            total = 0
            for i in range(len(self.measure_points)-1):
                total += math.sqrt((x[i+1]-x[i])**2 + (y[i+1]-y[i])**2) * 111
            self.ax.text(x[-1], y[-1], f"{total:.1f} km", fontsize=10, color='#FF69B4',
                        bbox=dict(boxstyle="round", facecolor='#2b2b2b', alpha=0.8))
    
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
        self.draw_welcome()
    
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
            if margin_x == 0:
                margin_x = 1
            if margin_y == 0:
                margin_y = 1
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.draw()
    
    def set_style(self, style):
        self.current_style = style
        if self.current_gdf is not None:
            self.draw_layer(self.current_gdf, self.current_name, style)
    
    def set_labels(self, labels):
        self.current_labels = labels
        if self.current_gdf is not None:
            self.draw_layer(self.current_gdf, self.current_name)
    
    def export(self, filename):
        self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2b2b2b')
    
    def get_scale(self):
        return self.scale

# ============================================================================
# DIALOGUE DES PROPRIETES DE COUCHE (CLAIR ET LISIBLE)
# ============================================================================

class LayerPropertiesDialog(QDialog):
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.setWindowTitle(f"Proprietes de la couche - {layer['name']}")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.setStyleSheet(STYLESHEET)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau de navigation gauche
        nav_list = QListWidget()
        nav_list.setMaximumWidth(200)
        nav_list.setStyleSheet("""
            QListWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #4a4a4a;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        nav_items = [
            "Information",
            "Source",
            "Symbologie",
            "Etiquettes",
            "Masques",
            "Vue 3D",
            "Diagrammes",
            "Champs",
            "Formulaire",
            "Jointures",
            "Stockage",
            "Actions",
            "Affichage",
            "Rendu",
            "Temporel",
            "Variables",
            "Metadonnees",
            "Dependances",
            "Legende"
        ]
        
        for item in nav_items:
            nav_list.addItem(item)
        
        nav_list.setCurrentRow(3)
        nav_list.currentRowChanged.connect(lambda i: self.content_stack.setCurrentIndex(i))
        splitter.addWidget(nav_list)
        
        # Panneau de contenu
        self.content_stack = QStackedWidget()
        
        # Onglet Etiquettes (complet)
        labels_widget = self.create_labels_widget()
        self.content_stack.addWidget(self.create_info_widget())
        self.content_stack.addWidget(self.create_source_widget())
        self.content_stack.addWidget(self.create_symbology_widget())
        self.content_stack.addWidget(labels_widget)
        
        for i in range(5, len(nav_items)):
            dummy = QWidget()
            dummy_layout = QVBoxLayout(dummy)
            dummy_layout.addWidget(QLabel("Fonctionnalite a venir"))
            dummy_layout.addStretch()
            self.content_stack.addWidget(dummy)
        
        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 700])
        main_layout.addWidget(splitter)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton("Appliquer")
        btn_apply.clicked.connect(self.apply)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_apply)
        main_layout.addLayout(btn_layout)
    
    def create_info_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        gdf = self.layer['gdf']
        
        group = QGroupBox("Informations generales")
        grid = QGridLayout(group)
        
        grid.addWidget(QLabel("Nom:"), 0, 0)
        grid.addWidget(QLabel(self.layer['name']), 0, 1)
        grid.addWidget(QLabel("Type:"), 1, 0)
        grid.addWidget(QLabel(self.layer.get('type', 'Inconnu')), 1, 1)
        grid.addWidget(QLabel("Entites:"), 2, 0)
        grid.addWidget(QLabel(str(len(gdf))), 2, 1)
        grid.addWidget(QLabel("Colonnes:"), 3, 0)
        grid.addWidget(QLabel(str(len(gdf.columns))), 3, 1)
        grid.addWidget(QLabel("Projection:"), 4, 0)
        grid.addWidget(QLabel(str(gdf.crs or 'WGS 84')), 4, 1)
        
        layout.addWidget(group)
        
        stats_group = QGroupBox("Statistiques")
        stats_layout = QGridLayout(stats_group)
        stats_layout.addWidget(QLabel("Etendue X:"), 0, 0)
        stats_layout.addWidget(QLabel(f"[{gdf.total_bounds[0]:.4f}, {gdf.total_bounds[2]:.4f}]"), 0, 1)
        stats_layout.addWidget(QLabel("Etendue Y:"), 1, 0)
        stats_layout.addWidget(QLabel(f"[{gdf.total_bounds[1]:.4f}, {gdf.total_bounds[3]:.4f}]"), 1, 1)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return widget
    
    def create_source_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(f"Fichier: {self.layer.get('path', 'Memoire')}\nDate: {self.layer.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
        layout.addWidget(text)
        return widget
    
    def create_symbology_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Symbologie - Fonctionnalite a venir"))
        return widget
    
    def create_labels_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Valeur
        value_group = QGroupBox("Valeur")
        value_layout = QVBoxLayout(value_group)
        self.label_field = QComboBox()
        for col in self.layer['gdf'].columns:
            if col != 'geometry':
                self.label_field.addItem(col)
        value_layout.addWidget(self.label_field)
        layout.addWidget(value_group)
        
        # Texte
        text_group = QGroupBox("Texte")
        text_layout = QGridLayout(text_group)
        text_layout.addWidget(QLabel("Police:"), 0, 0)
        font_combo = QComboBox()
        font_combo.addItems(["Sans-serif", "Serif", "Monospace"])
        text_layout.addWidget(font_combo, 0, 1)
        text_layout.addWidget(QLabel("Taille:"), 1, 0)
        self.label_size = QSpinBox()
        self.label_size.setRange(8, 24)
        self.label_size.setValue(10)
        text_layout.addWidget(self.label_size, 1, 1)
        text_layout.addWidget(QLabel("Couleur:"), 2, 0)
        self.label_color = QPushButton()
        self.label_color.setFixedSize(50, 25)
        self.label_color.setStyleSheet("background-color: #ffffff; border-radius: 3px;")
        self.label_color.clicked.connect(self.choose_color)
        text_layout.addWidget(self.label_color, 2, 1)
        layout.addWidget(text_group)
        
        # Arriere-plan
        bg_group = QGroupBox("Arriere-plan")
        bg_layout = QVBoxLayout(bg_group)
        self.bg_check = QCheckBox("Afficher un fond")
        bg_layout.addWidget(self.bg_check)
        bg_layout.addWidget(QLabel("Forme:"))
        shape_combo = QComboBox()
        shape_combo.addItems(["Rectangle", "Rond", "Carré"])
        bg_layout.addWidget(shape_combo)
        bg_layout.addWidget(QLabel("Opacite:"))
        self.bg_opacity = QSlider(Qt.Horizontal)
        self.bg_opacity.setRange(0, 100)
        self.bg_opacity.setValue(70)
        bg_layout.addWidget(self.bg_opacity)
        layout.addWidget(bg_group)
        
        # Position
        pos_group = QGroupBox("Position")
        pos_layout = QGridLayout(pos_group)
        pos_layout.addWidget(QLabel("Placement:"), 0, 0)
        placement = QComboBox()
        placement.addItems(["Auto", "Centre", "Haut", "Bas", "Gauche", "Droite"])
        pos_layout.addWidget(placement, 0, 1)
        pos_layout.addWidget(QLabel("Decalage X:"), 1, 0)
        offset_x = QDoubleSpinBox()
        offset_x.setRange(-100, 100)
        pos_layout.addWidget(offset_x, 1, 1)
        pos_layout.addWidget(QLabel("Decalage Y:"), 2, 0)
        offset_y = QDoubleSpinBox()
        offset_y.setRange(-100, 100)
        pos_layout.addWidget(offset_y, 2, 1)
        layout.addWidget(pos_group)
        
        layout.addStretch()
        return widget
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.label_color.setStyleSheet(f"background-color: {color.name()}; border-radius: 3px;")
    
    def apply(self):
        if hasattr(self, 'label_field') and hasattr(self, 'label_size') and hasattr(self, 'label_color'):
            color = self.label_color.styleSheet().split('background-color: ')[1].split(';')[0]
            labels = {
                'enabled': True,
                'field': self.label_field.currentText(),
                'size': self.label_size.value(),
                'color': color,
                'background': hasattr(self, 'bg_check') and self.bg_check.isChecked()
            }
            self.parent().map_canvas.set_labels(labels)
        self.accept()

# ============================================================================
# FENETRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION} - Logiciel de Cartographie")
        self.setGeometry(50, 50, 1500, 900)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLESHEET)
        
        self.layers = []
        self.current_layer = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        
        self.statusBar().showMessage("Pret - Cliquez sur Ajouter pour charger des donnees")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        info = QLabel("JOMAN GIS - Logiciel de Cartographie\nFormats supportes: SHP, GeoJSON, KML, KMZ, CSV")
        info.setStyleSheet("background-color: #3c3c3c; color: #4CAF50; padding: 10px; border-radius: 5px; font-weight: bold;")
        info.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(info)
        
        left_layout.addWidget(QLabel("Couches chargees:"))
        self.layer_list = QListWidget()
        self.layer_list.itemDoubleClicked.connect(self.open_properties)
        self.layer_list.itemClicked.connect(self.on_layer_clicked)
        left_layout.addWidget(self.layer_list)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(self.load_file)
        btn_remove = QPushButton("Supprimer")
        btn_remove.clicked.connect(self.remove_current_layer)
        btn_props = QPushButton("Proprietes")
        btn_props.clicked.connect(self.open_properties)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_props)
        left_layout.addLayout(btn_layout)
        
        left_layout.addWidget(QLabel("Attributs selectionnes:"))
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setMaximumHeight(120)
        left_layout.addWidget(self.attr_text)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Carte
        self.map_canvas = MapCanvas(self)
        self.map_canvas.selection_changed.connect(self.on_selection_changed)
        self.map_canvas.coordinates_changed.connect(self.on_coordinates_changed)
        layout.addWidget(self.map_canvas, 1)
        
        # Panneau droit
        right_panel = QWidget()
        right_panel.setMaximumWidth(280)
        right_layout = QVBoxLayout(right_panel)
        
        tools_group = QGroupBox("Outils")
        tools_layout = QVBoxLayout(tools_group)
        btn_zoom_in = QPushButton("Zoom +")
        btn_zoom_in.clicked.connect(self.map_canvas.zoom_in)
        tools_layout.addWidget(btn_zoom_in)
        btn_zoom_out = QPushButton("Zoom -")
        btn_zoom_out.clicked.connect(self.map_canvas.zoom_out)
        tools_layout.addWidget(btn_zoom_out)
        btn_zoom_all = QPushButton("Vue d'ensemble")
        btn_zoom_all.clicked.connect(self.map_canvas.zoom_all)
        tools_layout.addWidget(btn_zoom_all)
        self.btn_measure = QPushButton("Mesure (OFF)")
        self.btn_measure.clicked.connect(self.toggle_measure)
        tools_layout.addWidget(self.btn_measure)
        btn_export = QPushButton("Exporter carte")
        btn_export.clicked.connect(self.export_map)
        tools_layout.addWidget(btn_export)
        right_layout.addWidget(tools_group)
        
        legend_group = QGroupBox("Legende")
        legend_layout = QVBoxLayout(legend_group)
        self.legend_tree = QTreeWidget()
        self.legend_tree.setHeaderHidden(True)
        legend_layout.addWidget(self.legend_tree)
        right_layout.addWidget(legend_group)
        
        right_layout.addStretch()
        layout.addWidget(right_panel)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Fichier")
        file_menu.addAction("Charger", self.load_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("Exporter carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("Quitter", self.close, "Ctrl+Q")
        
        layer_menu = menubar.addMenu("Couche")
        layer_menu.addAction("Proprietes", self.open_properties, "Ctrl+P")
        layer_menu.addAction("Supprimer", self.remove_current_layer)
        
        view_menu = menubar.addMenu("Affichage")
        view_menu.addAction("Zoom +", self.map_canvas.zoom_in, "Ctrl++")
        view_menu.addAction("Zoom -", self.map_canvas.zoom_out, "Ctrl+-")
        view_menu.addAction("Vue ensemble", self.map_canvas.zoom_all, "Ctrl+0")
        
        tools_menu = menubar.addMenu("Outils")
        tools_menu.addAction("Mesure", self.toggle_measure, "Ctrl+M")
        
        help_menu = menubar.addMenu("Aide")
        help_menu.addAction("A propos", self.about)
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Principale")
        toolbar.addAction("Charger", self.load_file)
        toolbar.addAction("Zoom +", self.map_canvas.zoom_in)
        toolbar.addAction("Zoom -", self.map_canvas.zoom_out)
        toolbar.addAction("Vue ensemble", self.map_canvas.zoom_all)
        toolbar.addAction("Mesure", self.toggle_measure)
        toolbar.addAction("Proprietes", self.open_properties)
        toolbar.addAction("Exporter", self.export_map)
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.coord_label = QLabel("Coordonnees: -")
        self.scale_label = QLabel("Echelle: -")
        self.statusbar.addPermanentWidget(self.coord_label)
        self.statusbar.addPermanentWidget(QLabel("  |  "))
        self.statusbar.addPermanentWidget(self.scale_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        if self.map_canvas.ax.has_data():
            xl, yl = self.map_canvas.ax.get_xlim(), self.map_canvas.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"Coordonnees: {lon:.4f}, {lat:.4f}")
            scale = self.map_canvas.get_scale()
            if scale > 0:
                self.scale_label.setText(f"Echelle: 1:{int(scale):,}")
    
    def on_coordinates_changed(self, x, y):
        self.coord_label.setText(f"Coordonnees: {x:.4f}, {y:.4f}")
    
    def open_properties(self):
        if self.current_layer:
            dialog = LayerPropertiesDialog(self.current_layer, self)
            dialog.exec()
    
    def update_legend(self):
        self.legend_tree.clear()
        for layer in self.layers:
            item = QTreeWidgetItem(self.legend_tree)
            icon = "●"
            if layer['type'] == 'Point':
                icon = "●"
            elif layer['type'] == 'Ligne':
                icon = "─"
            else:
                icon = "■"
            item.setText(0, f"{icon} {layer['name']}")
            if 'color' in layer:
                item.setForeground(0, QColor(layer['color']))
    
    def load_file(self):
        formats = "Tous les formats (*.shp *.geojson *.json *.kml *.kmz *.csv)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger une couche", "", formats)
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
                    color = '#FF6B6B'
                elif 'Line' in geom_type:
                    layer_type = 'Ligne'
                    color = '#FFB347'
                else:
                    layer_type = 'Polygone'
                    color = '#4CAF50'
            else:
                layer_type = 'Polygone'
                color = '#4CAF50'
            
            layer = {
                'id': len(self.layers),
                'name': name,
                'path': filename,
                'gdf': gdf,
                'type': layer_type,
                'color': color,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.layers.append(layer)
            
            icon = "●" if layer_type == 'Point' else ("─" if layer_type == 'Ligne' else "■")
            self.layer_list.addItem(f"{icon} {name} ({len(gdf)} entites)")
            
            if not self.current_layer:
                self.current_layer = layer
                style = {'color': color, 'opacity': 0.7, 'size': 5, 'type': layer_type}
                self.map_canvas.draw_layer(gdf, name, style)
            
            self.update_legend()
            self.statusBar().showMessage(f"{name} charge ({len(gdf)} entites)")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def remove_current_layer(self):
        if self.current_layer:
            self.layers = [l for l in self.layers if l['id'] != self.current_layer['id']]
            self.layer_list.clear()
            for layer in self.layers:
                icon = "●" if layer['type'] == 'Point' else ("─" if layer['type'] == 'Ligne' else "■")
                self.layer_list.addItem(f"{icon} {layer['name']} ({len(layer['gdf'])} entites)")
            
            if self.layers:
                self.current_layer = self.layers[0]
                style = {'color': self.current_layer['color'], 'opacity': 0.7, 'size': 5, 'type': self.current_layer['type']}
                self.map_canvas.draw_layer(self.current_layer['gdf'], self.current_layer['name'], style)
            else:
                self.current_layer = None
                self.map_canvas.clear()
                self.attr_text.clear()
            
            self.update_legend()
    
    def on_layer_clicked(self, item):
        index = self.layer_list.currentRow()
        if 0 <= index < len(self.layers):
            self.current_layer = self.layers[index]
            style = {'color': self.current_layer['color'], 'opacity': 0.7, 'size': 5, 'type': self.current_layer['type']}
            self.map_canvas.draw_layer(self.current_layer['gdf'], self.current_layer['name'], style)
    
    def on_selection_changed(self, row):
        if row is not None:
            text = "Attributs de l'entite selectionnee\n"
            text += "=" * 40 + "\n\n"
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
        self.btn_measure.setText("Mesure (ON)" if mode else "Mesure (OFF)")
        self.btn_measure.setStyleSheet("background-color: #FF6B6B;" if mode else "")
        self.statusBar().showMessage("Mode mesure ACTIF" if mode else "Mode mesure OFF")
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter la carte", "", "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if filename:
            self.map_canvas.export(filename)
            self.statusBar().showMessage(f"Carte exportee: {os.path.basename(filename)}")
    
    def about(self):
        QMessageBox.about(self, "A propos", f"""
        <h2 style='color:#4CAF50'>JOMAN GIS</h2>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p><b>Logiciel de Cartographie Professionnel</b></p>
        <p>Fonctionnalites:</p>
        <ul>
            <li>Chargement de fichiers: SHP, GeoJSON, KML, KMZ, CSV</li>
            <li>Zoom / Pan / Vue d'ensemble</li>
            <li>Selection par clic</li>
            <li>Mesure de distance</li>
            <li>Proprietes des couches</li>
            <li>Export de carte</li>
        </ul>
        <p>(c) 2026 - Tous droits reserves</p>
        """)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
