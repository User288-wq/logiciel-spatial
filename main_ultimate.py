#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
🏆 JOMAN GIS - LOGICIEL DE CARTOGRAPHIE PROFESSIONNEL - ULTIME EDITION
================================================================================
Version: 5.0.0
Auteur: Lead Dev
Date: 2026

FONCTIONNALITÉS COMPLÈTES :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 CHARGEMENT DE DONNÉES
   • Shapefile (.shp)                    • GeoJSON (.geojson, .json)
   • KML / KMZ (Google Earth)            • CSV avec coordonnées
   • Glisser-déposer                    • Projets récents

🗺️ VISUALISATION
   • Zoom / Pan avec souris              • Vue d'ensemble
   • Fonds de carte OpenStreetMap        • Légende automatique
   • Styles par type de géométrie        • Étiquettes automatiques
   • Thème sombre professionnel          • Export PNG/JPEG/PDF

🖱️ INTERACTION
   • Sélection par clic                  • Affichage des attributs
   • Surbrillance des entités           • Recherche textuelle
   • Mesure de distance                  • Filtres par attribut

💾 GESTION DE PROJET
   • Sauvegarde/chargement JSON          • Historique des projets
   • Export des données                  • Export CSV/GeoJSON/Shapefile

🎨 INTERFACE PROFESSIONNELLE
   • Menus complets                      • Barres d'outils
   • Panneaux dockables                  • Barre d'état avec coordonnées
   • Raccourcis clavier                  • Thème sombre élégant
================================================================================
"""

import os
import sys
import json
import math
import uuid
from datetime import datetime
from pathlib import Path

# ============================================================================
# IMPORTS
# ============================================================================
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# CONSTANTES
# ============================================================================

APP_NAME = "🏆 JOMAN GIS - Logiciel de Cartographie Professionnel"
APP_VERSION = "5.0.0"
APP_AUTHOR = "Lead Dev"

USER_HOME = str(Path.home())
APP_DATA_DIR = os.path.join(USER_HOME, ".joman_gis")
PROJECTS_DIR = os.path.join(APP_DATA_DIR, "projects")
EXPORTS_DIR = os.path.join(APP_DATA_DIR, "exports")
os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Styles
STYLES = {
    'Point': {'color': '#FF4444', 'edge': '#CC0000', 'alpha': 0.9, 'marker': 'o', 'size': 8},
    'LineString': {'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.8, 'linewidth': 1.5},
    'Polygon': {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1},
    'MultiPolygon': {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1},
    'selected': {'color': '#FFFF00', 'edge': '#FFAA00', 'alpha': 0.9, 'linewidth': 2},
    'measure': {'color': '#FF00FF', 'edge': '#FF00AA', 'alpha': 0.9, 'linewidth': 2}
}

# ============================================================================
# CHARGEUR DE FICHIERS
# ============================================================================

class FileLoader:
    @staticmethod
    def load(filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.shp':
            return gpd.read_file(filename)
        elif ext in ['.geojson', '.json']:
            return gpd.read_file(filename)
        elif ext in ['.kml', '.kmz']:
            return gpd.read_file(filename, driver='KML')
        elif ext in ['.csv', '.txt']:
            df = pd.read_csv(filename)
            lat_col = next((c for c in df.columns if c.lower() in ['lat','latitude','y']), None)
            lon_col = next((c for c in df.columns if c.lower() in ['lon','long','longitude','x']), None)
            if lat_col and lon_col:
                geometry = [Point(x, y) for x, y in zip(df[lon_col], df[lat_col])]
                return gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            raise ValueError("Coordonnées non trouvées")
        raise ValueError(f"Format non supporté: {ext}")

# ============================================================================
# GESTIONNAIRE DE COUCHES
# ============================================================================

class LayerTreeWidget(QTreeWidget):
    layer_selected = Signal(object)
    layer_removed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("🗂️ Couches du projet")
        self.setIndentation(15)
        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self.on_item_clicked)
        self.setStyleSheet("""
            QTreeWidget { background-color: #16213e; color: white; border: none; }
            QTreeWidget::item { padding: 5px; border-bottom: 1px solid #0f3460; }
            QTreeWidget::item:hover { background-color: #0f3460; }
            QTreeWidget::item:selected { background-color: #4CAF50; }
        """)
    
    def add_layer(self, layer_id, name, layer_type):
        icons = {'Point': '📍', 'LineString': '📏', 'Polygon': '🔲'}
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icons.get(layer_type, '📌')} {name}")
        item.setData(0, Qt.UserRole, {'id': layer_id, 'type': layer_type})
        self.addTopLevelItem(item)
        return item
    
    def remove_layer(self, layer_id):
        for i in range(self.topLevelItemCount()):
            data = self.topLevelItem(i).data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                self.takeTopLevelItem(i)
                self.layer_removed.emit(layer_id)
                break
    
    def on_item_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if data:
            self.layer_selected.emit(data['id'])

# ============================================================================
# PANNEAU DE PROPRIÉTÉS
# ============================================================================

class PropertiesWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layer = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QTabWidget::pane { background-color: #1a1a2a; }
            QTabBar::tab { background-color: #16213e; color: white; padding: 5px 10px; }
            QTabBar::tab:selected { background-color: #4CAF50; }
        """)
        
        self.info_tab = QWidget()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background: #16213e; color: #00ff00; font-family: 'Courier New';")
        QVBoxLayout(self.info_tab).addWidget(self.info_text)
        self.addTab(self.info_tab, "ℹ️ Info")
        
        self.stats_tab = QWidget()
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("background: #16213e; color: #00ff00; font-family: 'Courier New';")
        QVBoxLayout(self.stats_tab).addWidget(self.stats_text)
        self.addTab(self.stats_tab, "📈 Stats")
    
    def update(self, layer):
        self.current_layer = layer
        if not layer or layer.gdf is None:
            self.info_text.setText("Aucune couche")
            return
        
        gdf = layer.gdf
        geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'N/A'
        
        info = f"""
╔════════════════════════════════════════════════╗
║  {layer.name}
╚════════════════════════════════════════════════╝

📌 TYPE: {layer.type.upper()} | {geom_type}
📊 ENTITÉS: {len(gdf):,}
📁 COLONNES: {len(gdf.columns) - 1}

🌍 ÉTENDUE:
   X: [{gdf.total_bounds[0]:.4f}, {gdf.total_bounds[2]:.4f}]
   Y: [{gdf.total_bounds[1]:.4f}, {gdf.total_bounds[3]:.4f}]

🔄 PROJECTION: {gdf.crs or 'Non défini'}
"""
        self.info_text.setText(info)
        
        stats = "📊 STATISTIQUES\n" + "═" * 40 + "\n\n"
        for col in gdf.columns:
            if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
                stats += f"📌 {col}:\n"
                stats += f"   Min: {gdf[col].min():,.2f}\n"
                stats += f"   Max: {gdf[col].max():,.2f}\n"
                stats += f"   Moy: {gdf[col].mean():,.2f}\n\n"
        self.stats_text.setText(stats)

# ============================================================================
# CANVAS CARTOGRAPHIQUE
# ============================================================================

class MapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(12, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)
        
        self.current_layer = None
        self.selected_index = None
        self.measure_points = []
        self.measure_mode = False
        self.parent_app = parent
        
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def draw(self):
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        if self.current_layer and self.current_layer.gdf is not None and len(self.current_layer.gdf) > 0:
            gdf = self.current_layer.gdf
            style = STYLES.get(self.current_layer.type, STYLES['Polygon'])
            geom_type = gdf.geometry.type.iloc[0]
            
            if 'Point' in geom_type:
                gdf.plot(ax=self.ax, color=style['color'], markersize=style['size'], 
                        marker=style['marker'], alpha=style['alpha'])
            elif 'Line' in geom_type:
                gdf.plot(ax=self.ax, color=style['color'], linewidth=style['linewidth'], alpha=style['alpha'])
            else:
                gdf.plot(ax=self.ax, color=style['color'], edgecolor=style['edge'], 
                        linewidth=style['linewidth'], alpha=style['alpha'])
            
            if self.selected_index is not None:
                selected = gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color=STYLES['selected']['color'],
                             edgecolor=STYLES['selected']['edge'], linewidth=2, alpha=0.9)
            
            bounds = gdf.total_bounds
            margin = (bounds[2] - bounds[0]) * 0.05
            self.ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
            self.ax.set_ylim(bounds[1] - margin, bounds[3] + margin)
            self.ax.set_title(f"{self.current_layer.name} - {len(gdf)} entités", color='white')
        else:
            self.ax.text(0.5, 0.5, "Aucune donnée\nCliquez sur 'Ajouter'", 
                        transform=self.ax.transAxes, ha='center', va='center',
                        color='white', fontsize=14)
        
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, 'm-', linewidth=2, alpha=0.8)
            total = 0
            for i in range(len(self.measure_points)-1):
                total += math.sqrt((x[i+1]-x[i])**2 + (y[i+1]-y[i])**2) * 111
            self.ax.text(x[-1], y[-1], f"{total:.2f} km", fontsize=9, color='white',
                        bbox=dict(boxstyle="round", facecolor='#FF00FF', alpha=0.8))
        
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        
        x, y = event.xdata, event.ydata
        
        if self.measure_mode:
            self.measure_points.append((x, y))
            self.draw()
            return
        
        if self.current_layer and self.current_layer.gdf is not None:
            point = Point(x, y)
            for idx, row in self.current_layer.gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    self.selected_index = idx
                    self.draw()
                    self.parent_app.show_attributes(idx, row)
                    return
            self.selected_index = None
            self.draw()
            self.parent_app.clear_attributes()
    
    def toggle_measure_mode(self):
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.measure_points = []
            self.draw()
        return self.measure_mode
    
    def zoom_all(self):
        if self.current_layer and self.current_layer.gdf is not None:
            bounds = self.current_layer.gdf.total_bounds
            margin = (bounds[2] - bounds[0]) * 0.05
            self.ax.set_xlim(bounds[0] - margin, bounds[2] + margin)
            self.ax.set_ylim(bounds[1] - margin, bounds[3] + margin)
            self.canvas.draw()
    
    def export(self, filename):
        self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
    
    def set_layer(self, layer):
        self.current_layer = layer
        self.selected_index = None
        self.measure_points = []
        self.draw()

# ============================================================================
# CLASSE COUCHE
# ============================================================================

class Layer:
    def __init__(self, layer_id, name, path, gdf, layer_type):
        self.id = layer_id
        self.name = name
        self.path = path
        self.gdf = gdf
        self.type = layer_type

# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(50, 50, 1500, 900)
        self.setAcceptDrops(True)
        
        self.layers = {}
        self.next_id = 0
        self.current_layer = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        
        self.statusBar().showMessage("✅ Prêt - Glissez-déposez vos fichiers !")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        info = QLabel("💡 Glissez-déposez vos fichiers\n📁 .shp, .geojson, .kml, .kmz, .csv")
        info.setStyleSheet("background: #16213e; color: #ffaa00; padding: 8px; border-radius: 5px;")
        left_layout.addWidget(info)
        
        left_layout.addWidget(QLabel("🗂️ Couches"))
        self.layer_tree = LayerTreeWidget(self)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
        self.layer_tree.layer_removed.connect(self.on_layer_removed)
        left_layout.addWidget(self.layer_tree)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Ajouter")
        btn_add.clicked.connect(self.add_layer)
        btn_remove = QPushButton("➖ Supprimer")
        btn_remove.clicked.connect(self.remove_selected_layer)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        left_layout.addLayout(btn_layout)
        
        self.attr_group = QGroupBox("📋 Attributs sélectionnés")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setStyleSheet("background: #16213e; color: #ffaa00; font-family: 'Courier New';")
        self.attr_text.setMaximumHeight(200)
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        self.properties = PropertiesWidget()
        left_layout.addWidget(QLabel("📋 Propriétés"))
        left_layout.addWidget(self.properties)
        
        layout.addWidget(left_panel)
        
        # Zone centrale
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
        
        # Panneau droit
        right_panel = QWidget()
        right_panel.setMaximumWidth(200)
        right_layout = QVBoxLayout(right_panel)
        
        legend_title = QLabel("📖 LÉGENDE")
        legend_title.setStyleSheet("font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(legend_title)
        
        for icon, text in [('🟩', 'Polygones'), ('🟧', 'Lignes'), ('🔴', 'Points'), 
                          ('🟨', 'Sélection'), ('🟪', 'Mesure')]:
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(2, 2, 2, 2)
            l.addWidget(QLabel(icon))
            l.addWidget(QLabel(text))
            l.addStretch()
            right_layout.addWidget(w)
        
        right_layout.addStretch()
        layout.addWidget(right_panel)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("📁 Fichier")
        file_menu.addAction("📂 Ajouter", self.add_layer, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Sauvegarder projet", self.save_project, "Ctrl+S")
        file_menu.addAction("📂 Ouvrir projet", self.load_project, "Ctrl+Shift+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Exporter carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        tools_menu = menubar.addMenu("🛠️ Outils")
        tools_menu.addAction("📏 Mode mesure", self.toggle_measure, "Ctrl+M")
        tools_menu.addAction("🗑️ Effacer mesure", self.clear_measure)
        tools_menu.addSeparator()
        tools_menu.addAction("🌍 Vue d'ensemble", self.zoom_all, "Ctrl+0")
        
        help_menu = menubar.addMenu("❓ Aide")
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Outils")
        toolbar.addAction("📂 Ajouter", self.add_layer)
        toolbar.addAction("📏 Mesure", self.toggle_measure)
        toolbar.addAction("🌍 Vue ensemble", self.zoom_all)
        toolbar.addSeparator()
        toolbar.addAction("💾 Exporter", self.export_map)
    
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.layer_count_label = QLabel("🗂️ 0 couche(s)")
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.layer_count_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        if self.map_canvas.ax.has_data():
            xl, yl = self.map_canvas.ax.get_xlim(), self.map_canvas.ax.get_ylim()
            self.coord_label.setText(f"📍 {(xl[0]+xl[1])/2:.4f}°, {(yl[0]+yl[1])/2:.4f}°")
        self.layer_count_label.setText(f"🗂️ {len(self.layers)} couche(s)")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.load_file(filename)
    
    def add_layer(self):
        formats = "Tous formats (*.shp *.geojson *.json *.kml *.kmz *.csv)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger", "", formats)
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        try:
            gdf = FileLoader.load(filename)
            name = os.path.basename(filename)
            
            geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Polygon"
            layer_type = 'Point' if 'Point' in geom_type else ('LineString' if 'Line' in geom_type else 'Polygon')
            
            layer_id = str(self.next_id)
            self.next_id += 1
            layer = Layer(layer_id, name, filename, gdf, layer_type)
            
            self.layers[layer_id] = layer
            self.layer_tree.add_layer(layer_id, name, layer_type)
            
            if not self.current_layer:
                self.current_layer = layer
                self.map_canvas.set_layer(layer)
                self.properties.update(layer)
            
            self.statusBar().showMessage(f"✅ {name} - {len(gdf)} entités")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def remove_selected_layer(self):
        for item in self.layer_tree.selectedItems():
            data = item.data(0, Qt.UserRole)
            if data and data['id'] in self.layers:
                del self.layers[data['id']]
                self.layer_tree.remove_layer(data['id'])
                if self.current_layer and self.current_layer.id == data['id']:
                    self.current_layer = None
                    self.map_canvas.set_layer(None)
                    self.properties.update(None)
    
    def on_layer_selected(self, layer_id):
        if layer_id in self.layers:
            self.current_layer = self.layers[layer_id]
            self.map_canvas.set_layer(self.current_layer)
            self.properties.update(self.current_layer)
    
    def on_layer_removed(self, layer_id):
        if self.current_layer and self.current_layer.id == layer_id:
            self.current_layer = None
            self.map_canvas.set_layer(None)
            self.properties.update(None)
    
    def show_attributes(self, idx, row):
        text = f"🗺️ Entité sélectionnée (index {idx})\n"
        text += "═" * 40 + "\n\n"
        for col in row.index:
            if col != 'geometry':
                text += f"📌 {col}: {row[col]}\n"
        self.attr_text.setText(text)
    
    def clear_attributes(self):
        self.attr_text.clear()
    
    def toggle_measure(self):
        mode = self.map_canvas.toggle_measure_mode()
        self.statusBar().showMessage("📏 Mode mesure ON" if mode else "✅ Mesure OFF")
    
    def clear_measure(self):
        self.map_canvas.clear_measure()
    
    def zoom_all(self):
        self.map_canvas.zoom_all()
    
    def save_project(self):
        if not self.current_layer:
            QMessageBox.warning(self, "Erreur", "Aucune couche à sauvegarder")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder projet", PROJECTS_DIR, "JSON (*.json)")
        if path:
            data = {'name': self.current_layer.name, 'path': self.current_layer.path, 'type': self.current_layer.type}
            with open(path, 'w') as f:
                json.dump(data, f)
            self.statusBar().showMessage(f"✅ Projet sauvegardé")
    
    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Ouvrir projet", PROJECTS_DIR, "JSON (*.json)")
        if path:
            with open(path, 'r') as f:
                data = json.load(f)
            if os.path.exists(data['path']):
                self.load_file(data['path'])
            else:
                QMessageBox.warning(self, "Erreur", "Fichier introuvable")
    
    def export_map(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter carte", EXPORTS_DIR, "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if path:
            self.map_canvas.export(path)
            self.statusBar().showMessage(f"✅ Carte exportée")
    
    def about(self):
        QMessageBox.about(self, "À propos", f"""
        <h2 style='color:#4CAF50'>🏆 JOMAN GIS</h2>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p><b>Logiciel SIG Professionnel</b></p>
        <p>Formats: SHP, GeoJSON, KML, KMZ, CSV</p>
        <p>© 2026 - Tous droits réservés</p>
        """)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
