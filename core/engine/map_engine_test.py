# ui/main_window.py
"""
================================================================================
🚀 LOGICIEL DE CARTOGRAPHIE - INTERFACE UTILISATEUR COMPLÈTE
================================================================================
Version: 1.0.0
Auteur: Lead Dev
Date: 2026

Fonctionnalités :
- Chargement de fichiers (Shapefile, GeoJSON, KML, CSV)
- Visualisation cartographique interactive
- Gestionnaire de couches
- Sélection d'entités
- Mesure de distance
- Recherche textuelle
- Filtres par attributs
- Sauvegarde/chargement de projet
- Export d'images
================================================================================
"""

import os
import sys
import json
import math
from datetime import datetime
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Import de la fondation
from core.engine.map_engine import MapEngine, VectorLayer, MapExtent, LayerStyle
from core.io.file_loader import FileLoader
from core.analysis.spatial_analysis import SpatialAnalysis
from core.project.project_manager import ProjectManager

# Configuration
os.environ["QT_API"] = "pyside6"


class LayerTreeWidget(QTreeWidget):
    """Widget arborescent pour la gestion des couches"""
    
    layer_visibility_changed = Signal(str, bool)
    layer_selected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("🗂️ Couches")
        self.setIndentation(15)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
        
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #16213e;
                alternate-background-color: #1a1a2a;
                border: none;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #0f3460;
            }
            QTreeWidget::item:hover {
                background-color: #0f3460;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
    
    def add_layer(self, layer_id: str, name: str, layer_type: str) -> QTreeWidgetItem:
        """Ajoute une couche à l'arbre"""
        icons = {
            'Point': '📍',
            'LineString': '📏',
            'Polygon': '🔲',
            'vector': '📌',
            'raster': '🖼️'
        }
        icon = icons.get(layer_type, '📌')
        
        item = QTreeWidgetItem(self)
        item.setText(0, f"{icon} {name}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'id': layer_id, 'type': layer_type})
        self.addTopLevelItem(item)
        return item
    
    def update_visibility(self, layer_id: str, visible: bool):
        """Met à jour la visibilité d'une couche"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                item.setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
                break
    
    def remove_layer(self, layer_id: str):
        """Supprime une couche de l'arbre"""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data['id'] == layer_id:
                self.takeTopLevelItem(i)
                break
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.UserRole)
        if data:
            self.layer_selected.emit(data['id'])
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        if column == 0:
            data = item.data(0, Qt.UserRole)
            if data:
                visible = item.checkState(0) == Qt.Checked
                self.layer_visibility_changed.emit(data['id'], visible)
    
    def show_context_menu(self, position: QPoint):
        item = self.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        
        menu = QMenu()
        menu.addAction("🔍 Zoom sur la couche", lambda: self.parent().zoom_to_layer(data['id']))
        menu.addAction("🎨 Style", lambda: self.parent().edit_layer_style(data['id']))
        menu.addSeparator()
        menu.addAction("📤 Exporter", lambda: self.parent().export_layer(data['id']))
        menu.addSeparator()
        menu.addAction("🗑️ Supprimer", lambda: self.parent().remove_layer(data['id']))
        menu.exec(self.viewport().mapToGlobal(position))


class PropertiesWidget(QWidget):
    """Widget d'affichage des propriétés"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Onglet Info
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background-color: #16213e; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
        info_layout.addWidget(self.info_text)
        self.tabs.addTab(self.info_tab, "ℹ️ Info")
        
        # Onglet Attributs
        self.attr_tab = QWidget()
        attr_layout = QVBoxLayout(self.attr_tab)
        self.attr_table = QTableWidget()
        self.attr_table.setColumnCount(3)
        self.attr_table.setHorizontalHeaderLabels(["Champ", "Type", "Valeur"])
        self.attr_table.horizontalHeader().setStretchLastSection(True)
        self.attr_table.setAlternatingRowColors(True)
        attr_layout.addWidget(self.attr_table)
        self.tabs.addTab(self.attr_tab, "📊 Attributs")
        
        # Onglet Statistiques
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("background-color: #16213e; color: #00ff00; font-family: 'Courier New'; font-size: 11px;")
        stats_layout.addWidget(self.stats_text)
        self.tabs.addTab(self.stats_tab, "📈 Stats")
        
        layout.addWidget(self.tabs)
    
    def update_properties(self, layer: VectorLayer):
        """Met à jour l'affichage des propriétés"""
        if not layer or not hasattr(layer, 'gdf'):
            self.info_text.setText("Aucune couche sélectionnée")
            self.attr_table.setRowCount(0)
            self.stats_text.setText("")
            return
        
        gdf = layer.gdf
        geom_type = layer.get_geometry_type() if hasattr(layer, 'get_geometry_type') else "Unknown"
        
        # Info
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
        self.info_text.setText(info)
        
        # Attributs
        self.attr_table.setRowCount(len(gdf.columns) - 1)
        row = 0
        for col in gdf.columns:
            if col != 'geometry':
                self.attr_table.setItem(row, 0, QTableWidgetItem(col))
                self.attr_table.setItem(row, 1, QTableWidgetItem(str(gdf[col].dtype)))
                preview = str(gdf[col].iloc[0])[:50] if len(gdf) > 0 else ''
                self.attr_table.setItem(row, 2, QTableWidgetItem(preview))
                row += 1
        
        # Statistiques
        stats = "📊 STATISTIQUES DES CHAMPS NUMÉRIQUES\n"
        stats += "═" * 40 + "\n\n"
        for col in gdf.columns:
            if col != 'geometry' and pd.api.types.is_numeric_dtype(gdf[col]):
                stats += f"📌 {col}:\n"
                stats += f"   Min: {gdf[col].min():,.2f}\n"
                stats += f"   Max: {gdf[col].max():,.2f}\n"
                stats += f"   Moy: {gdf[col].mean():,.2f}\n"
                stats += f"   Std: {gdf[col].std():,.2f}\n\n"
        self.stats_text.setText(stats)


class MainWindow(QMainWindow):
    """Fenêtre principale du logiciel"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Logiciel de Cartographie Professionnel")
        self.setGeometry(100, 100, 1400, 900)
        self.setAcceptDrops(True)
        
        # Initialisation des composants
        self.engine = MapEngine()
        self.file_loader = FileLoader()
        self.project_manager = ProjectManager()
        self.layers = {}  # id -> layer
        self.next_id = 0
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_statusbar()
        
        # Connexion des événements
        self.engine.add_listener(self.on_engine_event)
        
        self.status.showMessage("Prêt - Glissez-déposez vos fichiers !")
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche (couches + propriétés)
        left_panel = QWidget()
        left_panel.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_panel)
        
        # Info glisser-déposer
        info_label = QLabel("💡 Glissez-déposez vos fichiers ici\n📁 Formats: .shp, .geojson, .kml, .kmz, .csv...")
        info_label.setStyleSheet("background-color: #16213e; color: #ffaa00; padding: 8px; border-radius: 5px;")
        left_layout.addWidget(info_label)
        
        # Gestionnaire de couches
        self.layer_tree = LayerTreeWidget(self)
        self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
        self.layer_tree.layer_selected.connect(self.on_layer_selected)
        left_layout.addWidget(QLabel("🗂️ Couches"))
        left_layout.addWidget(self.layer_tree)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter")
        self.btn_add.clicked.connect(self.import_file)
        self.btn_remove = QPushButton("➖ Supprimer")
        self.btn_remove.clicked.connect(self.remove_selected_layer)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        left_layout.addLayout(btn_layout)
        
        # Attributs sélectionnés
        self.attr_group = QGroupBox("📋 Attributs de l'entité sélectionnée")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setStyleSheet("background-color: #16213e; color: #ffaa00; font-family: 'Courier New'; font-size: 11px;")
        self.attr_text.setMaximumHeight(200)
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        # Propriétés
        self.properties = PropertiesWidget()
        left_layout.addWidget(QLabel("📋 Propriétés de la couche"))
        left_layout.addWidget(self.properties)
        
        layout.addWidget(left_panel)
        
        # Zone centrale (carte)
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        self.map_widget = self.create_map_widget()
        center_layout.addWidget(self.map_widget)
        layout.addWidget(center_panel, 1)
        
        # Panneau droit (légende)
        right_panel = QWidget()
        right_panel.setMaximumWidth(250)
        right_layout = QVBoxLayout(right_panel)
        
        legend_title = QLabel("📖 LÉGENDE")
        legend_title.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 12px;")
        right_layout.addWidget(legend_title)
        
        legend_items = [
            ('🟩', 'Régions', '#4CAF50'),
            ('🟧', 'Départements', '#FFA500'),
            ('🟪', 'Communes', '#FF69B4'),
            ('📍', 'Points', '#FF4444'),
            ('📏', 'Lignes', '#FFA500'),
            ('🔲', 'Polygones', '#4CAF50'),
            ('🟨', 'Sélectionné', '#FFFF00'),
            ('🟪', 'Mesure', '#FF00FF'),
        ]
        
        for icon, name, color in legend_items:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.addWidget(QLabel(icon))
            layout.addWidget(QLabel(name))
            layout.addStretch()
            right_layout.addWidget(widget)
        
        right_layout.addStretch()
        layout.addWidget(right_panel)
    
    def create_map_widget(self):
        """Crée le widget de carte"""
        class MapCanvas(QWidget):
            def __init__(self, parent):
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
                
                self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
                self.parent_app = parent
            
            def on_click(self, event):
                if event.inaxes is None:
                    return
                self.parent_app.on_map_click(event.xdata, event.ydata)
            
            def draw_layers(self, layers):
                self.ax.clear()
                self.ax.set_facecolor('#0a1a2a')
                
                xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
                any_visible = False
                
                for layer in layers:
                    if not layer.visible:
                        continue
                    any_visible = True
                    
                    # Rendu de la couche
                    gdf = layer.get_data() if hasattr(layer, 'get_data') else layer.gdf
                    geom_type = layer.get_geometry_type() if hasattr(layer, 'get_geometry_type') else "Polygon"
                    
                    if geom_type == "Point":
                        gdf.plot(ax=self.ax, color=layer.style.color, 
                                markersize=layer.style.point_size,
                                alpha=layer.style.fill_alpha)
                    elif geom_type == "LineString":
                        gdf.plot(ax=self.ax, color=layer.style.color,
                                linewidth=layer.style.line_width,
                                alpha=layer.style.fill_alpha)
                    else:
                        gdf.plot(ax=self.ax, color=layer.style.color,
                                edgecolor=layer.style.edge_color,
                                linewidth=layer.style.line_width,
                                alpha=layer.style.fill_alpha)
                    
                    # Mise à jour des limites
                    bounds = gdf.total_bounds
                    xmin = min(xmin, bounds[0])
                    ymin = min(ymin, bounds[1])
                    xmax = max(xmax, bounds[2])
                    ymax = max(ymax, bounds[3])
                
                if any_visible and xmin != float('inf'):
                    margin_x = (xmax - xmin) * 0.05
                    margin_y = (ymax - ymin) * 0.05
                    self.ax.set_xlim(xmin - margin_x, xmax + margin_x)
                    self.ax.set_ylim(ymin - margin_y, ymax + margin_y)
                else:
                    self.ax.set_xlim(-20, 20)
                    self.ax.set_ylim(0, 25)
                
                self.ax.tick_params(colors='white')
                self.ax.set_title(f"Carte - {len(layers)} couche(s)", color='white')
                self.canvas.draw()
        
        return MapCanvas(self)
    
    def setup_menus(self):
        """Configure les menus"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📂 Importer un fichier", self.import_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Sauvegarder projet", self.save_project, "Ctrl+S")
        file_menu.addAction("📂 Ouvrir projet", self.load_project, "Ctrl+Shift+O")
        file_menu.addSeparator()
        file_menu.addAction("💾 Exporter la carte", self.export_map, "Ctrl+E")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🔍 Zoom avant", self.zoom_in, "Ctrl++")
        view_menu.addAction("🔍 Zoom arrière", self.zoom_out, "Ctrl+-")
        view_menu.addAction("🌍 Vue d'ensemble", self.zoom_all, "Ctrl+0")
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def setup_toolbars(self):
        """Configure les barres d'outils"""
        toolbar = self.addToolBar("Outils")
        toolbar.addAction("📂 Importer", self.import_file)
        toolbar.addAction("💾 Sauvegarder", self.save_project)
        toolbar.addAction("🔍 Zoom +", self.zoom_in)
        toolbar.addAction("🔍 Zoom -", self.zoom_out)
        toolbar.addAction("🌍 Vue d'ensemble", self.zoom_all)
        toolbar.addSeparator()
        toolbar.addAction("❓ Aide", self.show_docs)
    
    def setup_statusbar(self):
        """Configure la barre d'état"""
        self.status = self.statusBar()
        self.coord_label = QLabel("📍 -")
        self.scale_label = QLabel("📏 -")
        self.layer_count_label = QLabel("🗂️ 0 couche(s)")
        
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.scale_label)
        self.status.addPermanentWidget(QLabel("  |  "))
        self.status.addPermanentWidget(self.layer_count_label)
        self.status.showMessage("Prêt")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)
    
    def update_status(self):
        """Met à jour la barre d'état"""
        if hasattr(self.map_widget, 'ax') and self.map_widget.ax.has_data():
            xl, yl = self.map_widget.ax.get_xlim(), self.map_widget.ax.get_ylim()
            lon = (xl[0] + xl[1]) / 2
            lat = (yl[0] + yl[1]) / 2
            self.coord_label.setText(f"📍 {lon:.4f}°, {lat:.4f}°")
            
            width_deg = xl[1] - xl[0]
            width_km = width_deg * 111
            scale = width_km * 100000
            self.scale_label.setText(f"📏 1:{int(scale):,}")
        
        self.layer_count_label.setText(f"🗂️ {len(self.layers)} couche(s)")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename:
                self.load_file(filename)
    
    def import_file(self):
        """Importe un fichier via dialogue"""
        formats = "Fichiers supportés (*.shp *.geojson *.json *.kml *.kmz *.csv *.txt);;"
        formats += "Shapefile (*.shp);;GeoJSON (*.geojson *.json);;KML/KMZ (*.kml *.kmz);;CSV (*.csv *.txt)"
        
        filename, _ = QFileDialog.getOpenFileName(self, "Importer un fichier", "", formats)
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename: str):
        """Charge un fichier"""
        gdf, error = self.file_loader.load(filename)
        
        if gdf is None:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger {os.path.basename(filename)}\n{error}")
            return
        
        name = os.path.basename(filename)
        layer_id = str(self.next_id)
        self.next_id += 1
        
        # Déterminer le type
        geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Polygon"
        if 'Point' in geom_type:
            layer_type = 'Point'
        elif 'Line' in geom_type:
            layer_type = 'LineString'
        else:
            layer_type = 'Polygon'
        
        layer = VectorLayer(layer_id, name, filename, gdf, layer_type)
        self.layers[layer_id] = layer
        self.engine.add_layer(layer)
        
        # Ajouter à l'arbre
        self.layer_tree.add_layer(layer_id, name, layer_type)
        
        # Mettre à jour l'affichage
        self.redraw_map()
        self.status.showMessage(f"✅ {name} chargé")
    
    def remove_layer(self, layer_id: str):
        """Supprime une couche"""
        if layer_id in self.layers:
            del self.layers[layer_id]
            self.engine.remove_layer(layer_id)
            self.layer_tree.remove_layer(layer_id)
            self.redraw_map()
            self.status.showMessage("🗑️ Couche supprimée")
    
    def remove_selected_layer(self):
        """Supprime la couche sélectionnée"""
        current = self.layer_tree.currentItem()
        if current:
            data = current.data(0, Qt.UserRole)
            if data:
                self.remove_layer(data['id'])
    
    def on_layer_visibility_changed(self, layer_id: str, visible: bool):
        """Gère le changement de visibilité d'une couche"""
        if layer_id in self.layers:
            self.layers[layer_id].visible = visible
            self.redraw_map()
    
    def on_layer_selected(self, layer_id: str):
        """Gère la sélection d'une couche"""
        if layer_id in self.layers:
            self.properties.update_properties(self.layers[layer_id])
    
    def on_map_click(self, x: float, y: float):
        """Gère le clic sur la carte"""
        result = self.engine.select_feature(x, y)
        if result:
            layer, idx = result
            row = layer.get_data().iloc[idx]
            self.show_attributes(layer, idx, row)
        else:
            self.attr_text.clear()
    
    def show_attributes(self, layer: VectorLayer, idx: int, row):
        """Affiche les attributs d'une entité sélectionnée"""
        text = f"🗺️ {layer.name}\n"
        text += "═" * 40 + "\n\n"
        
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val is not None:
                    text += f"📌 {col}: {val}\n"
                else:
                    text += f"📌 {col}: (vide)\n"
        
        text += f"\n📍 Index: {idx}"
        self.attr_text.setText(text)
        self.status.showMessage(f"✅ Entité sélectionnée dans {layer.name}")
    
    def zoom_in(self):
        """Zoom avant"""
        if self.engine.current_extent:
            self.engine.zoom_in()
            extent = self.engine.current_extent
            self.map_widget.ax.set_xlim(extent.xmin, extent.xmax)
            self.map_widget.ax.set_ylim(extent.ymin, extent.ymax)
            self.map_widget.canvas.draw()
    
    def zoom_out(self):
        """Zoom arrière"""
        if self.engine.current_extent:
            self.engine.zoom_out()
            extent = self.engine.current_extent
            self.map_widget.ax.set_xlim(extent.xmin, extent.xmax)
            self.map_widget.ax.set_ylim(extent.ymin, extent.ymax)
            self.map_widget.canvas.draw()
    
    def zoom_all(self):
        """Vue d'ensemble"""
        self.engine.zoom_all()
        if self.engine.current_extent:
            extent = self.engine.current_extent
            self.map_widget.ax.set_xlim(extent.xmin, extent.xmax)
            self.map_widget.ax.set_ylim(extent.ymin, extent.ymax)
            self.map_widget.canvas.draw()
            self.status.showMessage("🌍 Vue d'ensemble")
    
    def zoom_to_layer(self, layer_id: str):
        """Zoom sur une couche"""
        if layer_id in self.layers:
            extent = self.layers[layer_id].get_bounds()
            if extent:
                self.map_widget.ax.set_xlim(extent.xmin, extent.xmax)
                self.map_widget.ax.set_ylim(extent.ymin, extent.ymax)
                self.map_widget.canvas.draw()
    
    def edit_layer_style(self, layer_id: str):
        """Édite le style d'une couche"""
        QMessageBox.information(self, "Style", "Fonctionnalité à venir")
    
    def export_layer(self, layer_id: str):
        """Exporte une couche"""
        QMessageBox.information(self, "Export", "Fonctionnalité à venir")
    
    def save_project(self):
        """Sauvegarde le projet"""
        filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le projet", "", "Projet JSON (*.json)")
        if filename:
            layers_list = list(self.layers.values())
            if self.project_manager.save_project(filename, layers_list):
                self.status.showMessage(f"✅ Projet sauvegardé: {os.path.basename(filename)}")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de sauvegarder le projet")
    
    def load_project(self):
        """Charge un projet"""
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir un projet", "", "Projet JSON (*.json)")
        if filename:
            data = self.project_manager.load_project(filename)
            if data:
                # Nettoyer les couches existantes
                for layer_id in list(self.layers.keys()):
                    self.remove_layer(layer_id)
                
                # Charger les couches
                for layer_info in data.get('layers', []):
                    if os.path.exists(layer_info.get('path', '')):
                        self.load_file(layer_info['path'])
                
                self.status.showMessage(f"✅ Projet chargé: {os.path.basename(filename)}")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de charger le projet")
    
    def export_map(self):
        """Exporte la carte en image"""
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter la carte", "", "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)")
        if filename:
            self.map_widget.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.status.showMessage(f"✅ Carte exportée: {os.path.basename(filename)}")
    
    def redraw_map(self):
        """Redessine la carte"""
        self.map_widget.draw_layers(list(self.layers.values()))
    
    def on_engine_event(self, event_type: str, *args):
        """Gère les événements du moteur"""
        if event_type == 'extent_changed':
            extent = args[0]
            self.map_widget.ax.set_xlim(extent.xmin, extent.xmax)
            self.map_widget.ax.set_ylim(extent.ymin, extent.ymax)
            self.map_widget.canvas.draw()
    
    def show_docs(self):
        """Affiche la documentation"""
        QMessageBox.information(self, "Documentation",
            "🚀 LOGICIEL DE CARTOGRAPHIE\n\n"
            "📁 Formats supportés:\n"
            "• Shapefile (.shp)\n"
            "• GeoJSON (.geojson, .json)\n"
            "• KML/KMZ (Google Earth)\n"
            "• CSV avec coordonnées\n\n"
            "🖱️ Raccourcis:\n"
            "• Ctrl+O: Importer\n"
            "• Ctrl+S: Sauvegarder projet\n"
            "• Ctrl+E: Exporter carte\n"
            "• Ctrl+0: Vue d'ensemble\n"
            "• Ctrl++: Zoom avant\n"
            "• Ctrl+-: Zoom arrière")
    
    def about(self):
        """Affiche les informations sur le logiciel"""
        QMessageBox.about(self, "À propos",
            "🚀 LOGICIEL DE CARTOGRAPHIE\n"
            "Version 1.0.0\n\n"
            "Logiciel de cartographie professionnel\n"
            "Développé avec PySide6 et GeoPandas\n\n"
            "© 2026 - Tous droits réservés")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette sombre
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