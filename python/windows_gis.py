#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 LOGICIEL SPATIAL - Version Windows Pro
==========================================
Compatible Windows avec :
- contextily pour les fonds de carte
- cartopy pour les projections
- Style QGIS professionnel
"""

import os
os.environ["QT_API"] = "pyside6"

import sys
import json
import geopandas as gpd
import pandas as pd
from datetime import datetime

# Bibliothèques compatibles Windows
import contextily as ctx
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# GESTIONNAIRE DE STYLES (COMPATIBLE WINDOWS)
# ============================================================================

class StyleManager:
    """Gestionnaire de styles avec contextily et cartopy"""
    
    # Fond de carte disponibles (contextily)
    BASEMAPS = {
        'Classique': ctx.providers.Stamen.TonerLite,
        'Satellite': ctx.providers.Esri.WorldImagery,
        'Relief': ctx.providers.Stamen.Terrain,
        'Nuit': ctx.providers.CartoDB.DarkMatter,
        'Route': ctx.providers.OpenStreetMap.Mapnik
    }
    
    @classmethod
    def add_basemap(cls, ax, style='Classique'):
        """Ajoute un fond de carte avec contextily"""
        try:
            ctx.add_basemap(ax, source=cls.BASEMAPS.get(style, cls.BASEMAPS['Classique']))
        except:
            pass  # Pas de fond si hors ligne
    
    @classmethod
    def style_region(cls, ax, gdf):
        """Style pour les régions"""
        gdf.plot(ax=ax,
                color='#4CAF50',
                edgecolor='#2E7D32',
                linewidth=1.5,
                alpha=0.4)
        
        # Ajouter les étiquettes
        for idx, row in gdf.iterrows():
            if row.geometry and not row.geometry.is_empty:
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y,
                       row.get('NAME', row.get('name', '')),
                       fontsize=9,
                       fontweight='bold',
                       color='white',
                       ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.3",
                                facecolor='#1a1a2a',
                                alpha=0.7,
                                edgecolor='#4CAF50'))
    
    @classmethod
    def style_commune(cls, ax, gdf):
        """Style pour les communes"""
        gdf.plot(ax=ax,
                color='#FFA500',
                edgecolor='#FF8C00',
                linewidth=0.8,
                alpha=0.3,
                hatch='///')
        
        # Ajouter les étiquettes (moins fréquentes)
        for idx, row in gdf.iterrows():
            if row.geometry and not row.geometry.is_empty and idx % 3 == 0:  # 1 commune sur 3
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y,
                       row.get('NAME', row.get('name', '')),
                       fontsize=7,
                       color='yellow',
                       ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='#0a1a2a',
                                alpha=0.6,
                                edgecolor='#FFA500'))
    
    @classmethod
    def style_route(cls, ax, gdf):
        """Style pour les routes"""
        gdf.plot(ax=ax,
                color='#808080',
                linewidth=0.5,
                alpha=0.7)
    
    @classmethod
    def style_hydro(cls, ax, gdf):
        """Style pour l'hydrographie"""
        gdf.plot(ax=ax,
                color='#2196F3',
                edgecolor='#1976D2',
                alpha=0.5,
                hatch='...')

# ============================================================================
# CHARGEUR CARTOGRAPHIQUE
# ============================================================================

class ChargeurCarto(QWidget):
    """Chargeur de fichiers compatible Windows"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files_loaded = []
        self.current_style = 'Classique'
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils
        toolbar = QToolBar()
        
        # Sélecteur de style
        self.style_combo = QComboBox()
        self.style_combo.addItems(['Classique', 'Satellite', 'Relief', 'Nuit', 'Route'])
        self.style_combo.currentTextChanged.connect(self.change_style)
        toolbar.addWidget(QLabel("  Style: "))
        toolbar.addWidget(self.style_combo)
        
        toolbar.addSeparator()
        
        # Options
        self.basemap_btn = QPushButton("🗺️ Fond de carte")
        self.basemap_btn.setCheckable(True)
        self.basemap_btn.setChecked(True)
        toolbar.addWidget(self.basemap_btn)
        
        self.grid_btn = QPushButton("🔲 Grille")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        toolbar.addWidget(self.grid_btn)
        
        layout.addWidget(toolbar)
        
        # Canvas
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.status_label = QLabel("Prêt - Style QGIS")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def change_style(self, style):
        """Change le style de la carte"""
        self.current_style = style
        self.plot_layers()
        self.status_label.setText(f"Style {style} appliqué")
    
    def load_file(self, filename):
        """Charge un fichier"""
        try:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.shp', '.geojson']:
                gdf = gpd.read_file(filename)
                
                # Détection du type
                layer_type = 'vector'
                if 'region' in filename.lower() or 'admin1' in filename.lower():
                    layer_type = 'region'
                elif 'commune' in filename.lower() or 'admin4' in filename.lower():
                    layer_type = 'commune'
                elif 'route' in filename.lower():
                    layer_type = 'route'
                elif 'hydro' in filename.lower():
                    layer_type = 'hydro'
                
                self.files_loaded.append({
                    'data': gdf,
                    'name': filename,
                    'type': layer_type
                })
                
                if self.parent:
                    self.parent.add_layer(filename, layer_type)
                
                self.plot_layers()
                self.status_label.setText(f"✅ Chargé: {os.path.basename(filename)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def plot_layers(self):
        """Affiche les couches avec le style choisi"""
        self.figure.clear()
        
        if not self.files_loaded:
            self.canvas.draw()
            return
        
        # Projection par défaut
        ax = self.figure.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_facecolor('#0a1a2a')
        
        # Ajouter le fond de carte si demandé
        if self.basemap_btn.isChecked():
            try:
                import contextily as ctx
                # Convertir en la bonne projection
                ax = plt.axes(projection=ccrs.PlateCarree())
                ctx.add_basemap(ax, source=StyleManager.BASEMAPS.get(
                    self.current_style, StyleManager.BASEMAPS['Classique']))
            except:
                pass
        
        # Calculer les limites
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        
        # Afficher chaque couche
        for layer in self.files_loaded:
            try:
                visible = True
                if self.parent and hasattr(self.parent, 'is_visible'):
                    visible = self.parent.is_visible(layer['name'])
                
                if visible:
                    if layer['type'] == 'region':
                        StyleManager.style_region(ax, layer['data'])
                    elif layer['type'] == 'commune':
                        StyleManager.style_commune(ax, layer['data'])
                    elif layer['type'] == 'route':
                        StyleManager.style_route(ax, layer['data'])
                    elif layer['type'] == 'hydro':
                        StyleManager.style_hydro(ax, layer['data'])
                    
                    # Mettre à jour les limites
                    bounds = layer['data'].total_bounds
                    xmin = min(xmin, bounds[0])
                    ymin = min(ymin, bounds[1])
                    xmax = max(xmax, bounds[2])
                    ymax = max(ymax, bounds[3])
                    
            except Exception as e:
                print(f"Erreur: {e}")
        
        # Ajuster les limites
        if xmin != float('inf'):
            margin_x = (xmax - xmin) * 0.05
            margin_y = (ymax - ymin) * 0.05
            ax.set_xlim(xmin - margin_x, xmax + margin_x)
            ax.set_ylim(ymin - margin_y, ymax + margin_y)
        
        # Ajouter la grille
        if self.grid_btn.isChecked():
            ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                        linewidth=0.5, color='gray', alpha=0.5)
        
        ax.set_title(f"Carte - Style {self.current_style}", color='white')
        
        self.canvas.draw()
    
    def zoom_in(self):
        ax = self.figure.gca()
        xl, yl = ax.get_xlim(), ax.get_ylim()
        xc, yc = (xl[0]+xl[1])/2, (yl[0]+yl[1])/2
        xr, yr = (xl[1]-xl[0])*0.8, (yl[1]-yl[0])*0.8
        ax.set_xlim(xc-xr/2, xc+xr/2)
        ax.set_ylim(yc-yr/2, yc+yr/2)
        self.canvas.draw()
    
    def zoom_out(self):
        ax = self.figure.gca()
        xl, yl = ax.get_xlim(), ax.get_ylim()
        xc, yc = (xl[0]+xl[1])/2, (yl[0]+yl[1])/2
        xr, yr = (xl[1]-xl[0])*1.25, (yl[1]-yl[0])*1.25
        ax.set_xlim(xc-xr/2, xc+xr/2)
        ax.set_ylim(yc-yr/2, yc+yr/2)
        self.canvas.draw()
    
    def zoom_full(self):
        self.plot_layers()

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

class WindowsGISApp(QMainWindow):
    """Application compatible Windows"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Spatial GIS - Version Windows")
        self.setGeometry(100, 100, 1400, 900)
        
        self.layers = []
        self.init_ui()
        
    def init_ui(self):
        # Widget central
        self.chargeur = ChargeurCarto(self)
        self.setCentralWidget(self.chargeur)
        
        self.create_menus()
        self.create_docks()
        self.create_statusbar()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📂 Charger", self.open_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🔍 Zoom +", self.chargeur.zoom_in, "Ctrl++")
        view_menu.addAction("🔍 Zoom -", self.chargeur.zoom_out, "Ctrl+-")
        view_menu.addAction("🌍 Étendre", self.chargeur.zoom_full)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def create_docks(self):
        # Panneau Couches
        self.layer_dock = QDockWidget("🗂️ Couches", self)
        
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Couches du projet")
        self.layer_tree.itemClicked.connect(self.on_layer_click)
        
        self.layer_dock.setWidget(self.layer_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layer_dock)
        
        # Panneau Propriétés
        self.prop_dock = QDockWidget("📋 Propriétés", self)
        
        self.prop_text = QTextEdit()
        self.prop_text.setReadOnly(True)
        self.prop_text.setStyleSheet("background: #1a1a2a; color: #0f0; font-family: monospace;")
        
        self.prop_dock.setWidget(self.prop_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.prop_dock)
    
    def create_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("Coordonnées: -")
        self.status.addPermanentWidget(self.coord_label)
        self.status.showMessage("Prêt - Version Windows")
        
        # Timer pour mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
    
    def update_status(self):
        if hasattr(self.chargeur, 'figure') and self.chargeur.figure.axes:
            ax = self.chargeur.figure.gca()
            xl, yl = ax.get_xlim(), ax.get_ylim()
            self.coord_label.setText(f"Centre: {(xl[0]+xl[1])/2:.2f}°, {(yl[0]+yl[1])/2:.2f}°")
    
    def add_layer(self, filename, layer_type):
        """Ajoute une couche à l'arbre"""
        icons = {
            'region': '🟩',
            'commune': '🟧',
            'route': '🛣️',
            'hydro': '💧'
        }
        icon = icons.get(layer_type, '📌')
        
        item = QTreeWidgetItem(self.layer_tree)
        item.setText(0, f"{icon} {os.path.basename(filename)}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'name': filename, 'type': layer_type})
        self.layer_tree.addTopLevelItem(item)
        self.layers.append({'name': filename, 'type': layer_type, 'item': item})
    
    def is_visible(self, filename):
        """Vérifie si une couche est visible"""
        for layer in self.layers:
            if layer['name'] == filename:
                return layer['item'].checkState(0) == Qt.Checked
        return True
    
    def on_layer_click(self, item):
        """Affiche les propriétés"""
        data = item.data(0, Qt.UserRole)
        if data:
            info = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📁 {os.path.basename(data['name'])}
 TYPE: {data['type'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATUT
────────
• Visible: {'Oui' if item.checkState(0) == Qt.Checked else 'Non'}
• Style: {self.chargeur.style_combo.currentText()}
• Fond de carte: {'Oui' if self.chargeur.basemap_btn.isChecked() else 'Non'}
• Grille: {'Oui' if self.chargeur.grid_btn.isChecked() else 'Non'}
"""
            self.prop_text.setText(info)
    
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger fichier", "", 
            "Shapefile (*.shp);;GeoJSON (*.geojson);;Tous (*.*)"
        )
        if filename:
            self.chargeur.load_file(filename)
    
    def about(self):
        QMessageBox.about(self, "À propos",
            "🚀 Spatial GIS - Version Windows\n"
            "Version 1.0\n\n"
            "Compatible Windows\n"
            "Moteur: contextily + cartopy\n\n"
            "© 2026")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = WindowsGISApp()
    window.show()
    sys.exit(app.exec())