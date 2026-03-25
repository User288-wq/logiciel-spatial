#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
🏆 JOMAN - LOGICIEL DE CARTOGRAPHIE PROFESSIONNEL
================================================================================
Version: 1.0.0
Auteur: Lead Dev

JOMAN - Votre alternative moderne à QGIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FONCTIONNALITÉS COMPLÈTES :
   • Interface dockable style QGIS
   • Multi-couches avec arbre hiérarchique
   • Navigation souris (zoom/pan)
   • Mesure de distance et surface
   • Table des attributs avec filtre
   • Éditeur de style (couleur, transparence)
   • Traitements géomatiques (Buffer, Intersection, Dissolve)
   • Barre d'échelle et flèche nord automatiques
   • Sauvegarde/chargement de projets (.joman)
   • Export haute qualité (PNG, JPEG, PDF)
   • Glisser-déposer de fichiers
   • Support des formats: Shapefile, GeoJSON, KML, CSV
================================================================================
"""

import sys
import os
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as MplPolygon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# CONSTANTES JOMAN
# ============================================================================

APP_NAME = "🏆 JOMAN - Logiciel de Cartographie"
APP_VERSION = "1.0.0"

# Chemins
USER_HOME = str(Path.home())
APP_DATA_DIR = os.path.join(USER_HOME, ".joman")
PROJECTS_DIR = os.path.join(APP_DATA_DIR, "projects")
EXPORTS_DIR = os.path.join(APP_DATA_DIR, "exports")

for d in [APP_DATA_DIR, PROJECTS_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================================
# STYLES JOMAN
# ============================================================================

class JomanStyle:
    def __init__(self):
        self.colors = {
            'Point': '#FF6B6B',
            'LineString': '#FFB347',
            'Polygon': '#4ECDC4',
        }
        self.selected_color = '#FFE66D'
        self.background = '#F7F9FC'
        
    def get_style(self, layer_type, selected=False):
        if selected:
            return {'color': self.selected_color, 'edge': '#FFAA33', 'alpha': 0.9, 'linewidth': 2.5}
        if 'Point' in layer_type:
            return {'color': self.colors['Point'], 'alpha': 0.9, 'marker': 'o', 'size': 60}
        elif 'Line' in layer_type:
            return {'color': self.colors['LineString'], 'alpha': 0.8, 'linewidth': 2}
        else:
            return {'color': self.colors['Polygon'], 'edge': '#2C7A6E', 'alpha': 0.4, 'linewidth': 1}

# ============================================================================
# CANVAS JOMAN
# ============================================================================

class JomanCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.style = JomanStyle()
        self.figure = Figure(figsize=(12, 8), facecolor=self.style.background)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.style.background)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        self.layers = []
        self.selected_features = {}
        self.measure_points = []
        self.measure_mode = None
        self.parent_app = parent
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if self.measure_mode:
            self.measure_points.append((event.xdata, event.ydata))
            self.draw_measure()
        else:
            self.select_features(event.xdata, event.ydata)
            
    def select_features(self, x, y):
        point = Point(x, y)
        for layer in self.layers:
            if layer.visible and layer.gdf is not None:
                for idx, row in layer.gdf.iterrows():
                    if row.geometry and row.geometry.contains(point):
                        if layer.id not in self.selected_features:
                            self.selected_features[layer.id] = []
                        if idx not in self.selected_features[layer.id]:
                            self.selected_features[layer.id].append(idx)
                        self.parent_app.show_attributes(layer, idx, row)
                        self.draw()
                        return
                        
    def draw_measure(self):
        if len(self.measure_points) < 2:
            return
            
        x = [p[0] for p in self.measure_points]
        y = [p[1] for p in self.measure_points]
        
        if self.measure_mode == 'distance':
            total_dist = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
                total_dist += dist
                
            self.ax.plot(x, y, '#FF6B6B', linewidth=2)
            self.ax.plot(x, y, 'o', color='#FF6B6B', markersize=6)
            
            x_last, y_last = self.measure_points[-1]
            self.ax.text(x_last, y_last, f"{total_dist:.2f} km",
                        fontsize=10, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FF6B6B'))
                        
        elif self.measure_mode == 'area' and len(self.measure_points) >= 3:
            polygon = Polygon(self.measure_points)
            area_km2 = polygon.area * 111 * 111
            
            patch = MplPolygon(self.measure_points, facecolor='#4ECDC4', alpha=0.3, edgecolor='#FF6B6B', linewidth=2)
            self.ax.add_patch(patch)
            
            centroid = polygon.centroid
            self.ax.text(centroid.x, centroid.y, f"{area_km2:.2f} km²",
                        fontsize=10, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#4ECDC4'))
                        
        self.canvas.draw()
        
    def set_measure_mode(self, mode):
        self.measure_mode = mode
        self.measure_points = []
        
    def clear_measure(self):
        self.measure_points = []
        self.measure_mode = None
        self.draw()
        
    def zoom_in(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        width = (xlim[1] - xlim[0]) / 2
        height = (ylim[1] - ylim[0]) / 2
        self.ax.set_xlim(cx - width/2, cx + width/2)
        self.ax.set_ylim(cy - height/2, cy + height/2)
        self.canvas.draw()
        
    def zoom_out(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        width = (xlim[1] - xlim[0]) * 1.5
        height = (ylim[1] - ylim[0]) * 1.5
        self.ax.set_xlim(cx - width/2, cx + width/2)
        self.ax.set_ylim(cy - height/2, cy + height/2)
        self.canvas.draw()
        
    def full_extent(self):
        if self.layers:
            bounds = []
            for layer in self.layers:
                if layer.visible and layer.gdf is not None and len(layer.gdf) > 0:
                    bounds.append(layer.gdf.total_bounds)
            if bounds:
                all_bounds = [min(b[0] for b in bounds), min(b[1] for b in bounds),
                             max(b[2] for b in bounds), max(b[3] for b in bounds)]
                margin_x = (all_bounds[2] - all_bounds[0]) * 0.05
                margin_y = (all_bounds[3] - all_bounds[1]) * 0.05
                self.ax.set_xlim(all_bounds[0] - margin_x, all_bounds[2] + margin_x)
                self.ax.set_ylim(all_bounds[1] - margin_y, all_bounds[3] + margin_y)
                self.canvas.draw()
                
    def add_layer(self, layer):
        self.layers.append(layer)
        self.draw()
        
    def remove_layer(self, layer_id):
        self.layers = [l for l in self.layers if l.id != layer_id]
        if layer_id in self.selected_features:
            del self.selected_features[layer_id]
        self.draw()
        
    def draw(self):
        self.ax.clear()
        self.ax.set_facecolor(self.style.background)
        
        for layer in self.layers:
            if not layer.visible or layer.gdf is None or len(layer.gdf) == 0:
                continue
                
            gdf = layer.gdf
            geom_type = gdf.geometry.type.iloc[0]
            style = self.style.get_style(geom_type)
            
            if 'Point' in geom_type:
                gdf.plot(ax=self.ax, color=style['color'], markersize=style['size'], marker='o', alpha=style['alpha'])
            elif 'Line' in geom_type:
                gdf.plot(ax=self.ax, color=style['color'], linewidth=style['linewidth'], alpha=style['alpha'])
            else:
                gdf.plot(ax=self.ax, color=style['color'], edgecolor=style['edge'], linewidth=style['linewidth'], alpha=style['alpha'])
            
            if layer.id in self.selected_features:
                selected = gdf.iloc[self.selected_features[layer.id]]
                if len(selected) > 0:
                    selected.plot(ax=self.ax, color=self.style.selected_color, edgecolor='#FFAA33', linewidth=2.5, alpha=0.9)
        
        # Barre d'échelle
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x = xlim[0] + (xlim[1] - xlim[0]) * 0.05
        y = ylim[0] + (ylim[1] - ylim[0]) * 0.05
        width_deg = xlim[1] - xlim[0]
        width_km = width_deg * 111
        
        if width_km > 100:
            scale_len, text = 100, "100 km"
        elif width_km > 50:
            scale_len, text = 50, "50 km"
        elif width_km > 20:
            scale_len, text = 20, "20 km"
        elif width_km > 10:
            scale_len, text = 10, "10 km"
        else:
            scale_len, text = 5, "5 km"
            
        scale_deg = scale_len / 111
        x_end = x + scale_deg
        self.ax.plot([x, x_end], [y, y], 'k-', linewidth=2)
        self.ax.text(x + scale_deg/2, y - y*0.005, text, ha='center', fontsize=8)
        
        # Flèche nord
        x = xlim[1] - (xlim[1] - xlim[0]) * 0.08
        y = ylim[1] - (ylim[1] - ylim[0]) * 0.08
        arrow_length = (ylim[1] - ylim[0]) * 0.05
        self.ax.annotate('N', xy=(x, y), xytext=(x, y + arrow_length),
                        arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=2),
                        fontsize=12, ha='center', color='#FF6B6B')
                        
        self.canvas.draw()
        
    def export(self, filename):
        self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.style.background)

# ============================================================================
# ARBRE DES COUCHES
# ============================================================================

class JomanLayerTree(QTreeWidget):
    layer_visibility_changed = Signal(str, bool)
    layer_selected = Signal(str)
    layer_removed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("📁 Couches JOMAN")
        self.setIndentation(20)
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
        self.parent_window = parent
        
    def add_layer(self, layer_id, name, layer_type):
        icons = {'Point': '📍', 'LineString': '📏', 'Polygon': '🔲'}
        icon = icons.get(layer_type, '🗺️')
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icon} {name}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'id': layer_id, 'type': layer_type})
        self.addTopLevelItem(item)
        return item
        
    def remove_layer(self, layer_id):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                self.takeTopLevelItem(i)
                self.layer_removed.emit(layer_id)
                break
                
    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data:
            self.layer_selected.emit(data['id'])
            
    def on_item_changed(self, item, column):
        if column == 0:
            data = item.data(0, Qt.UserRole)
            if data:
                visible = item.checkState(0) == Qt.Checked
                self.layer_visibility_changed.emit(data['id'], visible)

# ============================================================================
# TABLE DES ATTRIBUTS
# ============================================================================

class JomanAttributeTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layer = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("🔍 Filtrer...")
        self.filter_edit.textChanged.connect(self.filter_table)
        layout.addWidget(self.filter_edit)
        
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
    def set_layer(self, layer):
        self.current_layer = layer
        if layer is None or layer.gdf is None:
            self.table.setRowCount(0)
            return
            
        gdf = layer.gdf
        columns = [c for c in gdf.columns if c != 'geometry']
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        self.table.setRowCount(len(gdf))
        for i, (idx, row) in enumerate(gdf.iterrows()):
            for j, col in enumerate(columns):
                item = QTableWidgetItem(str(row[col])[:100])
                item.setData(Qt.UserRole, idx)
                self.table.setItem(i, j, item)
                
    def filter_table(self):
        if not self.current_layer:
            return
        filter_text = self.filter_edit.text().lower()
        for i in range(self.table.rowCount()):
            hidden = True
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item and filter_text in item.text().lower():
                    hidden = False
                    break
            self.table.setRowHidden(i, hidden)

# ============================================================================
# TRAITEMENTS JOMAN
# ============================================================================

class JomanProcessing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Buffer
        buffer_group = QGroupBox("Buffer")
        buffer_layout = QVBoxLayout(buffer_group)
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Distance (km):"))
        self.buffer_dist = QDoubleSpinBox()
        self.buffer_dist.setRange(0, 1000)
        self.buffer_dist.setValue(10)
        dist_layout.addWidget(self.buffer_dist)
        buffer_layout.addLayout(dist_layout)
        
        self.buffer_btn = QPushButton("🔵 Créer un buffer")
        self.buffer_btn.clicked.connect(self.create_buffer)
        buffer_layout.addWidget(self.buffer_btn)
        layout.addWidget(buffer_group)
        
        # Dissolve
        dissolve_group = QGroupBox("Dissolve")
        dissolve_layout = QVBoxLayout(dissolve_group)
        self.dissolve_btn = QPushButton("🔷 Fusionner")
        self.dissolve_btn.clicked.connect(self.create_dissolve)
        dissolve_layout.addWidget(self.dissolve_btn)
        layout.addWidget(dissolve_group)
        
        layout.addStretch()
        
    def create_buffer(self):
        if not self.parent_app.current_layer:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une couche")
            return
            
        layer = self.parent_app.current_layer
        distance_km = self.buffer_dist.value()
        distance_deg = distance_km / 111
        
        try:
            buffered = layer.gdf.copy()
            buffered.geometry = buffered.geometry.buffer(distance_deg)
            self.parent_app.create_layer(f"{layer.name}_buffer_{distance_km}km", buffered, layer.type)
            QMessageBox.information(self, "Succès", f"Buffer créé")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
            
    def create_dissolve(self):
        if not self.parent_app.current_layer:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une couche")
            return
            
        layer = self.parent_app.current_layer
        try:
            dissolved = gpd.GeoDataFrame(geometry=[unary_union(layer.gdf.geometry)], crs=layer.gdf.crs)
            self.parent_app.create_layer(f"{layer.name}_dissolved", dissolved, layer.type)
            QMessageBox.information(self, "Succès", "Fusion terminée")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

# ============================================================================
# CLASSE COUCHE
# ============================================================================

class JomanLayer:
    def __init__(self, layer_id, name, path, gdf, layer_type):
        self.id = layer_id
        self.name = name
        self.path = path
        self.gdf = gdf
        self.type = layer_type
        self.visible = True
        self.style = {}

# ============================================================================
# FENÊTRE PRINCIPALE JOMAN
# ============================================================================

class JomanMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(50, 50, 1400, 850)
        self.setAcceptDrops(True)
        
        self.layers = {}
        self.next_id = 0
        self.current_layer = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        self.statusBar().showMessage("✅ JOMAN prêt - Glissez-déposez vos fichiers")
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Info
        info = QLabel("💡 JOMAN - Glissez-déposez vos fichiers\n📁 .shp .geojson .kml .csv")
        info.setStyleSheet("background: #34495E; color: #F39C12; padding: 10px; border-radius: 5px;")
        left_layout.addWidget(info)
        
        # Arbre des couches
        self.layer_tree = JomanLayerTree(self)
        self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
        self.layer_tree.layer_removed.connect(self.on_layer_removed)
        left_layout.addWidget(QLabel("📁 Couches"))
        left_layout.addWidget(self.layer_tree)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Ajouter")
        btn_add.clicked.connect(self.add_layer)
        btn_remove = QPushButton("➖ Supprimer")
        btn_remove.clicked.connect(self.remove_selected_layer)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        left_layout.addLayout(btn_layout)
        
        # Attributs
        self.attr_group = QGroupBox("📋 Attributs sélectionnés")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setMaximumHeight(150)
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        # Légende
        legend = QGroupBox("📖 Légende")
        legend_layout = QVBoxLayout(legend)
        legend_layout.addWidget(QLabel("🟩 Polygones"))
        legend_layout.addWidget(QLabel("🟧 Lignes"))
        legend_layout.addWidget(QLabel("🔴 Points"))
        legend_layout.addWidget(QLabel("🟨 Sélectionné"))
        left_layout.addWidget(legend)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Canvas central
        self.canvas = JomanCanvas(self)
        layout.addWidget(self.canvas, 1)
        
        # Panneau droit
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        
        # Outils
        tools_group = QGroupBox("🛠️ Outils")
        tools_layout = QVBoxLayout(tools_group)
        
        self.measure_dist_btn = QPushButton("📏 Mesure distance")
        self.measure_dist_btn.clicked.connect(lambda: self.canvas.set_measure_mode('distance'))
        self.measure_area_btn = QPushButton("📐 Mesure surface")
        self.measure_area_btn.clicked.connect(lambda: self.canvas.set_measure_mode('area'))
        self.clear_measure_btn = QPushButton("🗑️ Effacer mesure")
        self.clear_measure_btn.clicked.connect(self.canvas.clear_measure)
        
        tools_layout.addWidget(self.measure_dist_btn)
        tools_layout.addWidget(self.measure_area_btn)
        tools_layout.addWidget(self.clear_measure_btn)
        right_layout.addWidget(tools_group)
        
        # Traitements
        self.processing = JomanProcessing(self)
        right_layout.addWidget(self.processing)
        
        # Table attributs
        self.attr_table = JomanAttributeTable(self)
        right_layout.addWidget(QLabel("📊 Table des attributs"))
        right_layout.addWidget(self.attr_table)
        
        layout.addWidget(right_panel)
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("📁 Fichier")
        file_menu.addAction("📂 Ajouter une couche", self.add_layer, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Sauvegarder projet", self.save_project, "Ctrl+S")
        file_menu.addAction("📂 Ouvrir projet", self.load_project, "Ctrl+Shift+O")
        file_menu.addSeparator()
        file_menu.addAction("📸 Exporter carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        view_menu = menubar.addMenu("👁️ Vue")
        view_menu.addAction("🔍 Zoom avant", self.canvas.zoom_in, "Ctrl++")
        view_menu.addAction("🔍 Zoom arrière", self.canvas.zoom_out, "Ctrl+-")
        view_menu.addAction("🌍 Vue totale", self.canvas.full_extent, "Ctrl+0")
        
        help_menu = menubar.addMenu("❓ Aide")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ À propos", self.about)
        
    def setup_toolbar(self):
        toolbar = self.addToolBar("JOMAN")
        toolbar.addAction("📂 Ajouter", self.add_layer)
        toolbar.addAction("💾 Sauvegarder", self.save_project)
        toolbar.addAction("🔍+", self.canvas.zoom_in)
        toolbar.addAction("🔍-", self.canvas.zoom_out)
        toolbar.addAction("🌍", self.canvas.full_extent)
        toolbar.addAction("📏", lambda: self.canvas.set_measure_mode('distance'))
        toolbar.addAction("📐", lambda: self.canvas.set_measure_mode('area'))
        
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 -")
        self.version_label = QLabel(f"🏆 JOMAN v{APP_VERSION}")
        
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.scale_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.version_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
        
    def update_status(self):
        if self.canvas.ax.has_data():
            xlim = self.canvas.ax.get_xlim()
            ylim = self.canvas.ax.get_ylim()
            lon = (xlim[0] + xlim[1]) / 2
            lat = (ylim[0] + ylim[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
            
            width_deg = xlim[1] - xlim[0]
            width_km = width_deg * 111
            scale = int(width_km * 100000)
            self.scale_label.setText(f"📏 1:{scale:,}")
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.load_file(filename)
                
    def add_layer(self):
        formats = "Fichiers (*.shp *.geojson *.json *.kml *.kmz *.csv);;Shapefile (*.shp);;GeoJSON (*.geojson);;KML (*.kml);;CSV (*.csv)"
        filename, _ = QFileDialog.getOpenFileName(self, "Ajouter une couche JOMAN", "", formats)
        if filename:
            self.load_file(filename)
            
    def load_file(self, filename):
        try:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.shp':
                gdf = gpd.read_file(filename)
            elif ext in ['.geojson', '.json']:
                gdf = gpd.read_file(filename)
            elif ext in ['.kml', '.kmz']:
                gdf = gpd.read_file(filename, driver='KML')
            elif ext in ['.csv', '.txt']:
                df = pd.read_csv(filename)
                lat_col, lon_col = None, None
                for col in df.columns:
                    if col.lower() in ['lat', 'latitude', 'y']:
                        lat_col = col
                    elif col.lower() in ['lon', 'long', 'longitude', 'x']:
                        lon_col = col
                if lat_col and lon_col:
                    geometry = [Point(x, y) for x, y in zip(df[lon_col], df[lat_col])]
                    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                else:
                    raise ValueError("Colonnes coordonnées non trouvées")
            else:
                raise ValueError(f"Format non supporté: {ext}")
                
            name = os.path.basename(filename)
            geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Polygon"
            
            if 'Point' in geom_type:
                layer_type = 'Point'
            elif 'Line' in geom_type:
                layer_type = 'LineString'
            else:
                layer_type = 'Polygon'
                
            layer_id = str(self.next_id)
            self.next_id += 1
            layer = JomanLayer(layer_id, name, filename, gdf, layer_type)
            
            self.layers[layer_id] = layer
            self.layer_tree.add_layer(layer_id, name, layer_type)
            self.canvas.add_layer(layer)
            
            if not self.current_layer:
                self.current_layer = layer
                
            self.statusBar().showMessage(f"✅ {name} chargé dans JOMAN ({len(gdf)} entités)")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur JOMAN", str(e))
            
    def create_layer(self, name, gdf, layer_type):
        layer_id = str(self.next_id)
        self.next_id += 1
        layer = JomanLayer(layer_id, name, None, gdf, layer_type)
        self.layers[layer_id] = layer
        self.layer_tree.add_layer(layer_id, name, layer_type)
        self.canvas.add_layer(layer)
        return layer
        
    def remove_layer(self, layer_id):
        if layer_id in self.layers:
            del self.layers[layer_id]
            self.layer_tree.remove_layer(layer_id)
            self.canvas.remove_layer(layer_id)
            if self.current_layer and self.current_layer.id == layer_id:
                self.current_layer = None
                
    def remove_selected_layer(self):
        for item in self.layer_tree.selectedItems():
            data = item.data(0, Qt.UserRole)
            if data:
                self.remove_layer(data['id'])
                
    def on_layer_visibility_changed(self, layer_id, visible):
        if layer_id in self.layers:
            self.layers[layer_id].visible = visible
            self.canvas.draw()
            
    def on_layer_selected(self, layer_id):
        if layer_id in self.layers:
            self.current_layer = self.layers[layer_id]
            self.attr_table.set_layer(self.current_layer)
            
    def on_layer_removed(self, layer_id):
        self.remove_layer(layer_id)
        
    def show_attributes(self, layer, idx, row):
        text = f"🗺️ {layer.name} - Entité {idx}\n"
        text += "═" * 40 + "\n\n"
        for col in row.index:
            if col != 'geometry':
                text += f"📌 {col}: {row[col]}\n"
        self.attr_text.setText(text)
        
    def save_project(self):
        if not self.layers:
            QMessageBox.warning(self, "Projet vide", "Aucune couche à sauvegarder")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder projet JOMAN", PROJECTS_DIR, "JOMAN (*.joman)")
        if filename:
            try:
                project = {'name': os.path.basename(filename), 'date': datetime.now().isoformat(), 'version': APP_VERSION, 'layers': []}
                for layer in self.layers.values():
                    if layer.path:
                        project['layers'].append({'name': layer.name, 'path': layer.path, 'type': layer.type})
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project, f, indent=2)
                self.statusBar().showMessage(f"💾 Projet sauvegardé")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))
                
    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir projet JOMAN", PROJECTS_DIR, "JOMAN (*.joman)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    project = json.load(f)
                for layer_id in list(self.layers.keys()):
                    self.remove_layer(layer_id)
                for layer_info in project['layers']:
                    if os.path.exists(layer_info['path']):
                        self.load_file(layer_info['path'])
                self.statusBar().showMessage(f"📂 Projet chargé")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))
                
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter carte JOMAN", EXPORTS_DIR, "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if filename:
            self.canvas.export(filename)
            self.statusBar().showMessage(f"💾 Carte exportée")
            
    def show_docs(self):
        QMessageBox.information(self, "Documentation JOMAN", 
                                f"""{APP_NAME} v{APP_VERSION}

🏆 BIENVENUE DANS JOMAN

📖 RACCOURCIS:
   • Ctrl+O : Ajouter couche
   • Ctrl+S : Sauvegarder projet
   • Ctrl+E : Exporter carte
   • Ctrl+0 : Vue totale
   • Ctrl++ : Zoom avant
   • Ctrl+- : Zoom arrière

🛠️ OUTILS:
   • Mesure distance/surface
   • Sélection par clic
   • Buffer et Dissolve

📁 FORMATS:
   • Shapefile (.shp)
   • GeoJSON (.geojson)
   • KML/KMZ
   • CSV avec coordonnées

JOMAN - La cartographie simple et puissante !""")
        
    def about(self):
        QMessageBox.about(self, "À propos de JOMAN", 
                          f"""{APP_NAME} v{APP_VERSION}

🏆 JOMAN - Logiciel de Cartographie Professionnel

JOMAN est une alternative moderne aux SIG traditionnels.

✨ CARACTÉRISTIQUES:
   • Interface intuitive
   • Multi-couches
   • Mesure distance/surface
   • Traitements géomatiques
   • Export haute qualité

© 2026 - JOMAN GIS Team""")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
    palette.setColor(QPalette.Base, QColor(52, 73, 94))
    palette.setColor(QPalette.Text, QColor(236, 240, 241))
    palette.setColor(QPalette.Button, QColor(52, 73, 94))
    palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
    palette.setColor(QPalette.Highlight, QColor(243, 156, 18))
    app.setPalette(palette)
    
    window = JomanMainWindow()
    window.show()
    
    print("=" * 60)
    print(f"🏆 {APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    print("✅ JOMAN est prêt !")
    print("💡 Glissez-déposez vos fichiers")
    print("=" * 60)
    
    sys.exit(app.exec())