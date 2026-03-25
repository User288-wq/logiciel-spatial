#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
🌍 LOGICIEL DE CARTOGRAPHIE UNIVERSEL V2 - FONCTIONNE AVEC TOUTES LES DONNÉES
================================================================================
- Détection automatique du type de données (points, lignes, polygones)
- Adaptation automatique de l'affichage (couleurs, étiquettes)
- Zoom automatique sur les données chargées
- Support de tous les formats courants (Shapefile, GeoJSON, etc.)
- Gestion robuste des erreurs
- Messages de débogage pour comprendre ce qui se passe
================================================================================
"""

import os
import sys
import math
import traceback
from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Configuration
os.environ["QT_API"] = "pyside6"

# ============================================================================
# CONSTANTES - Styles adaptatifs
# ============================================================================

# Styles selon le type de géométrie et le nom
STYLES = {
    # Par type de géométrie
    'Point':     {'color': '#FF4444', 'edge': '#CC0000', 'alpha': 0.9, 'marker': 'o', 'size': 5, 'label': True},
    'LineString':{'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.8, 'linewidth': 1.5, 'label': False},
    'Polygon':   {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1, 'label': True},
    'MultiPolygon': {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1, 'label': True},
    'MultiPoint':{'color': '#FF4444', 'edge': '#CC0000', 'alpha': 0.8, 'marker': 'o', 'size': 3, 'label': False},
    'MultiLineString': {'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.7, 'linewidth': 1, 'label': False},
    
    # Par mot-clé dans le nom
    'region':     {'color': '#4CAF50', 'edge': '#2E7D32', 'alpha': 0.4, 'linewidth': 1, 'label': True},
    'departement':{'color': '#FFA500', 'edge': '#FF8C00', 'alpha': 0.3, 'linewidth': 1, 'label': True},
    'commune':    {'color': '#FF69B4', 'edge': '#C71585', 'alpha': 0.3, 'linewidth': 1, 'label': True},
    'route':      {'color': '#808080', 'edge': '#666666', 'alpha': 0.7, 'linewidth': 0.8, 'label': False},
    'hydro':      {'color': '#2196F3', 'edge': '#1976D2', 'alpha': 0.5, 'linewidth': 1, 'label': False},
    'default':    {'color': '#888888', 'edge': '#666666', 'alpha': 0.5, 'linewidth': 1, 'label': False}
}

# Noms de colonnes pour les étiquettes (ordre de priorité)
LABEL_COLUMNS = ['name', 'NAME', 'NOM', 'label', 'LABEL', 'commune', 'ville', 
                 'ADMIN1', 'ADMIN2', 'ADMIN3', 'ADMIN4', 'LIBELLE', 'LIBELLE_FR']

# ============================================================================
# GESTIONNAIRE DE COUCHES
# ============================================================================

class LayerTreeWidget(QTreeWidget):
    layer_visibility_changed = Signal(str, bool)
    layer_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("🗂️ Couches")
        self.setIndentation(15)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
    
    def add_layer(self, layer_id, name, layer_type, icon_char='📌'):
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icon_char} {name}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'id': layer_id, 'type': layer_type})
        self.addTopLevelItem(item)
        return item
    
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
    
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        menu = QMenu()
        menu.addAction("🔍 Zoom sur la couche", lambda: self.parent().zoom_to_layer(data['id']))
        menu.addAction("🗑️ Supprimer", lambda: self.parent().remove_layer(data['id']))
        menu.exec(self.viewport().mapToGlobal(position))

# ============================================================================
# PANNEAU DE PROPRIÉTÉS
# ============================================================================

class PropertiesWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #1a1a2a; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
    
    def update_properties(self, layer):
        if not layer or layer.gdf is None:
            self.setText("Aucune couche sélectionnée")
            return
        
        gdf = layer.gdf
        geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else 'N/A'
        
        info = f"""
╔══════════════════════════════════════════════════════════════╗
║  {layer.name}
╚══════════════════════════════════════════════════════════════╝

📌 TYPE: {layer.type.upper()} | Géométrie: {geom_type}
📊 ENTITÉS: {len(gdf):,}
📁 COLONNES: {len(gdf.columns) - 1}

🌍 ÉTENDUE:
   X: [{gdf.total_bounds[0]:.4f}, {gdf.total_bounds[2]:.4f}]
   Y: [{gdf.total_bounds[1]:.4f}, {gdf.total_bounds[3]:.4f}]

🔄 PROJECTION: {gdf.crs or 'Non défini'}

📋 COLONNES DISPONIBLES:
"""
        for col in gdf.columns:
            if col != 'geometry':
                info += f"   • {col}\n"
        
        self.setText(info)

# ============================================================================
# MOTEUR CARTOGRAPHIQUE
# ============================================================================

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)
    
    def get_style(self, layer):
        """Détermine le style à appliquer à une couche"""
        # 1. Par mot-clé dans le nom
        name_lower = layer.name.lower()
        for keyword, style in STYLES.items():
            if keyword != 'default' and keyword in name_lower:
                return style
        
        # 2. Par type de géométrie
        if layer.gdf is not None and len(layer.gdf) > 0:
            geom_type = layer.gdf.geometry.type.iloc[0]
            if geom_type in STYLES:
                return STYLES[geom_type]
        
        # 3. Style par défaut
        return STYLES['default']
    
    def get_label_column(self, gdf):
        """Trouve la meilleure colonne pour les étiquettes"""
        for col in LABEL_COLUMNS:
            if col in gdf.columns:
                return col
        return None
    
    def draw_layers(self, layers):
        """Dessine toutes les couches visibles avec zoom automatique"""
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        any_visible = False
        
        for layer in layers:
            if not layer.visible or layer.gdf is None:
                continue
            if len(layer.gdf) == 0:
                print(f"⚠️ {layer.name} est vide")
                continue
                
            any_visible = True
            style = self.get_style(layer)
            geom_type = layer.gdf.geometry.type.iloc[0]
            
            print(f"🎨 Dessin de {layer.name} (type={layer.type}, geom={geom_type}) - {len(layer.gdf)} entités")
            
            # Tracé selon le type de géométrie
            if 'Point' in geom_type:
                layer.gdf.plot(ax=self.ax, color=style['color'], 
                              markersize=style.get('size', 5), 
                              marker=style.get('marker', 'o'),
                              alpha=style['alpha'])
            elif 'Line' in geom_type:
                layer.gdf.plot(ax=self.ax, color=style['color'], 
                              linewidth=style.get('linewidth', 1),
                              alpha=style['alpha'])
            else:  # Polygones
                layer.gdf.plot(ax=self.ax, color=style['color'], 
                              edgecolor=style['edge'], 
                              linewidth=style.get('linewidth', 0.5),
                              alpha=style['alpha'])
            
            # Mise à jour des limites
            bounds = layer.gdf.total_bounds
            xmin = min(xmin, bounds[0])
            ymin = min(ymin, bounds[1])
            xmax = max(xmax, bounds[2])
            ymax = max(ymax, bounds[3])
            print(f"   Étendue: [{bounds[0]:.2f}, {bounds[2]:.2f}] x [{bounds[1]:.2f}, {bounds[3]:.2f}]")
            
            # Étiquettes
            if style.get('label', True):
                label_col = self.get_label_column(layer.gdf)
                if label_col:
                    self._draw_labels(layer, label_col)
        
        if not any_visible:
            self.ax.set_title("Aucune donnée visible", color='white')
            self.canvas.draw()
            return None
        
        # Zoom automatique sur les données
        if xmin != float('inf'):
            margin_x = (xmax - xmin) * 0.05
            margin_y = (ymax - ymin) * 0.05
            self.ax.set_xlim(xmin - margin_x, xmax + margin_x)
            self.ax.set_ylim(ymin - margin_y, ymax + margin_y)
            print(f"📐 Zoom: x[{xmin-margin_x:.2f}, {xmax+margin_x:.2f}] y[{ymin-margin_y:.2f}, {ymax+margin_y:.2f}]")
        else:
            # Vue par défaut sur l'Afrique de l'Ouest
            self.ax.set_xlim(-20, 20)
            self.ax.set_ylim(0, 25)
            print("📐 Vue par défaut: Afrique de l'Ouest")
        
        self.ax.tick_params(colors='white')
        self.ax.set_title(f"Carte - {len([l for l in layers if l.visible])} couche(s)", color='white')
        self.canvas.draw()
        
        return (xmin, ymin, xmax, ymax)

    def _draw_labels(self, layer, label_col):
        """Ajoute les étiquettes"""
        gdf = layer.gdf
        style = self.get_style(layer)
        
        for _, row in gdf.iterrows():
            if row.geometry and not row.geometry.is_empty:
                try:
                    centroid = row.geometry.centroid
                    label = str(row[label_col])[:25]  # Limiter la longueur
                    if label and label != 'nan':
                        self.ax.text(centroid.x, centroid.y, label,
                                   fontsize=7, color='white',
                                   ha='center', va='center',
                                   bbox=dict(boxstyle="round,pad=0.2",
                                            facecolor='#1a1a2a',
                                            alpha=0.7,
                                            edgecolor=style.get('edge', '#666')))
                except:
                    pass  # Ignorer les erreurs de centroïde

# ============================================================================
# COUCHE
# ============================================================================

class Layer:
    def __init__(self, layer_id, name, path, gdf, layer_type):
        self.id = layer_id
        self.name = name
        self.path = path
        self.gdf = gdf
        self.type = layer_type
        self.visible = True
        self.item = None

# ============================================================================
# FENÊTRE PRINCIPALE
# ============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Logiciel de Cartographie Universel V2")
        self.setGeometry(100, 100, 1400, 900)
        
        self.layers = []
        self.next_id = 0
        
        self.setup_ui()
        self.setup_menus()
        self.setup_statusbar()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        self.layer_tree = LayerTreeWidget(self)
        self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
        left_layout.addWidget(QLabel("🗂️ Couches"))
        left_layout.addWidget(self.layer_tree)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter")
        self.btn_add.clicked.connect(self.add_layer)
        self.btn_remove = QPushButton("➖ Supprimer")
        self.btn_remove.clicked.connect(self.remove_selected_layer)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        left_layout.addLayout(btn_layout)
        
        self.properties = PropertiesWidget()
        left_layout.addWidget(QLabel("📋 Propriétés"))
        left_layout.addWidget(self.properties)
        
        layout.addWidget(left_panel)
        
        self.map_widget = MapWidget(self)
        layout.addWidget(self.map_widget, 1)
    
    def setup_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📂 Ajouter une couche", self.add_layer, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Exporter la carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🌍 Vue d'ensemble", self.zoom_all, "Ctrl+0")
    
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 -")
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.scale_label)
        self.status.showMessage("Prêt - Ajoutez des données")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        if hasattr(self.map_widget, 'ax') and self.map_widget.ax.has_data():
            xl, yl = self.map_widget.ax.get_xlim(), self.map_widget.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
            width_deg = xl[1] - xl[0]
            width_km = width_deg * 111
            scale = width_km * 100000
            self.scale_label.setText(f"📏 1:{int(scale):,}")
    
    def add_layer(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger une couche", "",
            "Fichiers supportés (*.shp *.geojson *.json);;Shapefile (*.shp);;GeoJSON (*.geojson);;Tous (*.*)"
        )
        if not filename:
            return
        
        try:
            print(f"\n📂 Chargement de {filename}...")
            gdf = gpd.read_file(filename)
            name = os.path.basename(filename)
            
            if len(gdf) == 0:
                QMessageBox.warning(self, "Attention", "Le fichier ne contient aucune entité.")
                return
            
            # Détection du type
            layer_type = self.guess_type(filename, gdf)
            
            print(f"✅ Chargé: {len(gdf)} entités")
            print(f"📊 Type de géométrie: {gdf.geometry.type.iloc[0]}")
            print(f"📁 Colonnes: {list(gdf.columns)}")
            print(f"🌍 Étendue: {gdf.total_bounds}")
            print(f"🏷️ Type détecté: {layer_type}")
            
            layer_id = str(self.next_id)
            self.next_id += 1
            layer = Layer(layer_id, name, filename, gdf, layer_type)
            
            # Icône selon le type
            icons = {'Point': '📍', 'LineString': '📏', 'Polygon': '🔲'}
            geom_type = gdf.geometry.type.iloc[0]
            icon = icons.get(geom_type, '📌')
            
            item = self.layer_tree.add_layer(layer_id, name, layer_type, icon)
            layer.item = item
            self.layers.append(layer)
            
            self.redraw_map()
            self.status.showMessage(f"✅ {name} chargé ({len(gdf)} entités)")
            
            # Zoom automatique
            self.zoom_all()
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier :\n{e}")
    
    def guess_type(self, filename, gdf):
        """Détection intelligente du type"""
        name_lower = filename.lower()
        
        # Par mot-clé
        keywords = ['region', 'departement', 'commune', 'route', 'hydro']
        for kw in keywords:
            if kw in name_lower:
                return kw
        
        # Par type de géométrie
        if len(gdf) > 0:
            geom = gdf.geometry.type.iloc[0]
            if 'Point' in geom:
                return 'point'
            elif 'Line' in geom:
                return 'line'
            elif 'Polygon' in geom:
                return 'polygon'
        
        return 'default'
    
    def remove_layer(self, layer_id):
        for i, layer in enumerate(self.layers):
            if layer.id == layer_id:
                self.layer_tree.takeTopLevelItem(self.layer_tree.indexOfTopLevelItem(layer.item))
                del self.layers[i]
                self.redraw_map()
                self.status.showMessage("🗑️ Couche supprimée")
                break
    
    def remove_selected_layer(self):
        for item in self.layer_tree.selectedItems():
            data = item.data(0, Qt.UserRole)
            if data:
                self.remove_layer(data['id'])
    
    def on_layer_visibility_changed(self, layer_id, visible):
        for layer in self.layers:
            if layer.id == layer_id:
                layer.visible = visible
                self.redraw_map()
                break
    
    def on_layer_selected(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id:
                self.properties.update_properties(layer)
                break
    
    def zoom_to_layer(self, layer_id):
        for layer in self.layers:
            if layer.id == layer_id and layer.gdf is not None:
                bounds = layer.gdf.total_bounds
                margin_x = (bounds[2] - bounds[0]) * 0.05
                margin_y = (bounds[3] - bounds[1]) * 0.05
                self.map_widget.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
                self.map_widget.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
                self.map_widget.canvas.draw()
                self.status.showMessage(f"🔍 Zoom sur {layer.name}")
                break
    
    def zoom_all(self):
        """Zoom sur toutes les couches"""
        if not self.layers:
            self.map_widget.ax.set_xlim(-20, 20)
            self.map_widget.ax.set_ylim(0, 25)
            self.map_widget.canvas.draw()
            return
        
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        for layer in self.layers:
            if layer.gdf is not None and len(layer.gdf) > 0:
                bounds = layer.gdf.total_bounds
                xmin = min(xmin, bounds[0])
                ymin = min(ymin, bounds[1])
                xmax = max(xmax, bounds[2])
                ymax = max(ymax, bounds[3])
        
        if xmin != float('inf'):
            margin_x = (xmax - xmin) * 0.1
            margin_y = (ymax - ymin) * 0.1
            self.map_widget.ax.set_xlim(xmin - margin_x, xmax + margin_x)
            self.map_widget.ax.set_ylim(ymin - margin_y, ymax + margin_y)
        else:
            self.map_widget.ax.set_xlim(-20, 20)
            self.map_widget.ax.set_ylim(0, 25)
        
        self.map_widget.canvas.draw()
        self.status.showMessage("🌍 Vue d'ensemble")
    
    def redraw_map(self):
        self.map_widget.draw_layers(self.layers)
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter la carte", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filename:
            self.map_widget.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.status.showMessage(f"✅ Carte exportée : {os.path.basename(filename)}")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(18, 18, 18))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())