#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 LOGICIEL SPATIAL - Interface Style QGIS Version Avancée
===========================================================
Nouvelles fonctionnalités :
- Barres d'outils complètes
- Outil de mesure interactif
- Gestionnaire de projet
- Légende automatique
- Interface QGIS améliorée
"""

import os
os.environ["QT_API"] = "pyside6"

import sys
import json
import geopandas as gpd
from datetime import datetime
from math import sqrt

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# OUTIL DE MESURE INTERACTIF
# ============================================================================

class MesureTool:
    """Outil de mesure de distances sur la carte"""
    
    def __init__(self, canvas, status_callback):
        self.canvas = canvas
        self.status_callback = status_callback
        self.points = []
        self.distance = 0
        self.active = False
        self.cid = None
        self.lines = []
        
    def activate(self):
        self.active = True
        self.points = []
        self.distance = 0
        self.lines = []
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.status_callback("Mode mesure activé - Cliquez pour définir des points")
        
    def deactivate(self):
        self.active = False
        if self.cid:
            self.canvas.mpl_disconnect(self.cid)
            self.cid = None
        self.status_callback("Prêt")
            
    def on_click(self, event):
        if not self.active or event.inaxes is None:
            return
            
        self.points.append((event.xdata, event.ydata))
        
        if len(self.points) > 1:
            # Calculer la distance
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]
            
            # Conversion approximative en km (1 degré ≈ 111 km)
            dx = (x2 - x1) * 111
            dy = (y2 - y1) * 111
            segment = sqrt(dx*dx + dy*dy)
            self.distance += segment
            
            # Dessiner la ligne
            line, = event.inaxes.plot([x1, x2], [y1, y2], 
                                      'r-', linewidth=2, marker='o', markersize=4)
            self.lines.append(line)
            
            # Afficher la distance
            self.status_callback(f"Segment: {segment:.2f} km | Total: {self.distance:.2f} km")
            
            self.canvas.draw()
            
    def clear(self):
        """Efface toutes les mesures"""
        for line in self.lines:
            line.remove()
        self.lines = []
        self.points = []
        self.distance = 0
        self.canvas.draw()
        self.status_callback("Mesures effacées")

# ============================================================================
# LÉGENDE AUTOMATIQUE
# ============================================================================

class LegendeWidget(QWidget):
    """Widget de légende pour les couches"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.title = QLabel("📖 LÉGENDE")
        self.title.setStyleSheet("""
            font-weight: bold; 
            color: #4CAF50;
            font-size: 12px;
            padding: 5px;
            background-color: #1a1a2a;
            border-radius: 3px;
        """)
        layout.addWidget(self.title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumHeight(200)
        
        self.legend_content = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_content)
        self.scroll.setWidget(self.legend_content)
        layout.addWidget(self.scroll)
        
    def update_legend(self, layers):
        """Met à jour la légende avec les couches actuelles"""
        # Vider la légende
        for i in reversed(range(self.legend_layout.count())): 
            widget = self.legend_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not layers:
            label = QLabel("Aucune couche")
            label.setStyleSheet("color: #888; padding: 5px;")
            label.setAlignment(Qt.AlignCenter)
            self.legend_layout.addWidget(label)
            return
        
        # Ajouter les couches
        colors = ['#4CAF50', '#2196F3', '#FFA500', '#FF4444', '#9C27B0']
        for i, layer in enumerate(layers):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            
            # Indicateur de couleur
            color_label = QLabel("⬤")
            color_label.setStyleSheet(f"color: {colors[i % len(colors)]}; font-size: 14px;")
            layout.addWidget(color_label)
            
            # Nom du fichier (tronqué)
            name = os.path.basename(layer['name'])
            if len(name) > 20:
                name = name[:17] + "..."
            name_label = QLabel(name)
            name_label.setStyleSheet("color: white; font-size: 10px;")
            layout.addWidget(name_label)
            
            # Type d'icône
            icon_label = QLabel("🛰️" if layer['type'] == 'raster' else "📌")
            icon_label.setStyleSheet("font-size: 10px;")
            layout.addWidget(icon_label)
            
            layout.addStretch()
            
            self.legend_layout.addWidget(widget)

# ============================================================================
# GESTIONNAIRE DE PROJET
# ============================================================================

class ProjetManager:
    """Gère la sauvegarde et le chargement de projets"""
    
    def __init__(self, parent):
        self.parent = parent
        self.projet_courant = {
            'nom': 'Nouveau projet',
            'date': datetime.now().isoformat(),
            'couches': []
        }
        
    def nouveau_projet(self):
        """Crée un nouveau projet"""
        self.parent.chargeur.files_loaded.clear()
        self.parent.chargeur.plot_layers()
        self.parent.layer_list.clear()
        self.parent.layers_data.clear()
        self.parent.legende.update_legend([])
        self.projet_courant = {
            'nom': 'Nouveau projet',
            'date': datetime.now().isoformat(),
            'couches': []
        }
        self.parent.statusBar().showMessage("Nouveau projet créé")
        
    def sauvegarder_projet(self, filename):
        """Sauvegarde le projet en JSON"""
        projet = {
            'nom': self.projet_courant['nom'],
            'date': datetime.now().isoformat(),
            'couches': []
        }
        
        for layer in self.parent.layers_data:
            projet['couches'].append({
                'fichier': layer['name'],
                'type': layer['type']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(projet, f, indent=2, ensure_ascii=False)
            
        self.parent.statusBar().showMessage(f"Projet sauvegardé: {os.path.basename(filename)}")
            
    def charger_projet(self, filename):
        """Charge un projet depuis JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                projet = json.load(f)
                
            self.nouveau_projet()
            self.projet_courant = projet
            
            for couche in projet['couches']:
                if os.path.exists(couche['fichier']):
                    if couche['type'] == 'vector':
                        gdf = gpd.read_file(couche['fichier'])
                        self.parent.chargeur.add_layer(gdf, couche['fichier'])
                else:
                    QMessageBox.warning(self.parent, "Fichier manquant", 
                                       f"Fichier non trouvé: {couche['fichier']}")
                                       
            self.parent.statusBar().showMessage(f"Projet chargé: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur", f"Impossible de charger le projet: {str(e)}")

# ============================================================================
# CHARGEUR DE FICHIERS CARTOGRAPHIQUES (amélioré)
# ============================================================================

class ChargeurCarto(QWidget):
    """Widget pour charger et afficher des fichiers cartographiques"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files_loaded = []
        self.current_gdf = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Boutons avec texte seulement (pour l'instant)
        self.btn_shape = QAction("📂 Shapefile", self)
        self.btn_shape.triggered.connect(self.load_shapefile)
        toolbar.addAction(self.btn_shape)
        
        self.btn_geojson = QAction("🌍 GeoJSON", self)
        self.btn_geojson.triggered.connect(self.load_geojson)
        toolbar.addAction(self.btn_geojson)
        
        self.btn_tiff = QAction("🖼️ GeoTIFF", self)
        self.btn_tiff.triggered.connect(self.load_geotiff)
        toolbar.addAction(self.btn_tiff)
        
        self.btn_osm = QAction("🏙️ OSM", self)
        self.btn_osm.triggered.connect(self.load_osm)
        toolbar.addAction(self.btn_osm)
        
        toolbar.addSeparator()
        
        self.btn_zoom_in = QAction("🔍 Zoom +", self)
        self.btn_zoom_in.triggered.connect(self.zoom_in)
        toolbar.addAction(self.btn_zoom_in)
        
        self.btn_zoom_out = QAction("🔍 Zoom -", self)
        self.btn_zoom_out.triggered.connect(self.zoom_out)
        toolbar.addAction(self.btn_zoom_out)
        
        self.btn_reset = QAction("🔄 Reset", self)
        self.btn_reset.triggered.connect(self.reset_view)
        toolbar.addAction(self.btn_reset)
        
        self.btn_save = QAction("💾 Sauvegarder", self)
        self.btn_save.triggered.connect(self.save_map)
        toolbar.addAction(self.btn_save)
        
        layout.addWidget(toolbar)
        
        # Canvas
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Barre d'état du chargeur
        self.status_label = QLabel("Prêt - Chargez un fichier")
        self.status_label.setStyleSheet("color: #888888; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def load_shapefile(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger Shapefile", "", 
            "Shapefile (*.shp);;Tous (*.*)"
        )
        if filename:
            self._load_vector_file(filename)
    
    def load_geojson(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger GeoJSON", "", 
            "GeoJSON (*.geojson);;JSON (*.json);;Tous (*.*)"
        )
        if filename:
            self._load_vector_file(filename)
    
    def _load_vector_file(self, filename):
        try:
            self.status_label.setText(f"🔄 Chargement: {os.path.basename(filename)}")
            QApplication.processEvents()
            
            gdf = gpd.read_file(filename)
            self.files_loaded.append({
                'gdf': gdf,
                'name': filename,
                'type': 'vector'
            })
            self.plot_layers()
            self.status_label.setText(f"✅ Chargé: {os.path.basename(filename)}")
            
            if self.parent:
                self.parent.add_layer_to_list(filename, 'vector')
                self.parent.legende.update_legend(self.files_loaded)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger: {str(e)}")
            self.status_label.setText("❌ Erreur de chargement")
    
    def load_geotiff(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger GeoTIFF", "", 
            "GeoTIFF (*.tif *.tiff);;Tous (*.*)"
        )
        if filename:
            try:
                import rasterio
                from rasterio.plot import show
                
                self.status_label.setText(f"🔄 Chargement: {os.path.basename(filename)}")
                QApplication.processEvents()
                
                src = rasterio.open(filename)
                self.files_loaded.append({
                    'src': src,
                    'name': filename,
                    'type': 'raster'
                })
                self.plot_layers()
                self.status_label.setText(f"✅ Chargé: {os.path.basename(filename)}")
                
                if self.parent:
                    self.parent.add_layer_to_list(filename, 'raster')
                    self.parent.legende.update_legend(self.files_loaded)
                
            except ImportError:
                QMessageBox.warning(self, "Module manquant", 
                    "Installez rasterio: pip install rasterio")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de charger: {str(e)}")
                self.status_label.setText("❌ Erreur de chargement")
    
    def load_osm(self):
        try:
            import osmnx as ox
            
            ville, ok = QInputDialog.getText(
                self, "OpenStreetMap", 
                "Entrez le nom d'une ville (ex: Dakar, Senegal):"
            )
            
            if ok and ville:
                self.status_label.setText(f"🔄 Téléchargement de {ville}...")
                QApplication.processEvents()
                
                graph = ox.graph_from_place(ville, network_type='drive')
                gdf = ox.graph_to_gdfs(graph, nodes=False, edges=True)
                
                self.files_loaded.append({
                    'gdf': gdf,
                    'name': f"OSM - {ville}",
                    'type': 'vector'
                })
                self.plot_layers()
                self.status_label.setText(f"✅ Données OSM chargées pour {ville}")
                
                if self.parent:
                    self.parent.add_layer_to_list(f"OSM - {ville}", 'vector')
                    self.parent.legende.update_legend(self.files_loaded)
                
        except ImportError:
            QMessageBox.warning(self, "Module manquant", 
                "Installez osmnx: pip install osmnx")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def plot_layers(self):
        self.figure.clear()
        
        if not self.files_loaded:
            self.canvas.draw()
            return
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#0a1a2a')
        
        for layer in self.files_loaded:
            try:
                if layer['type'] == 'raster':
                    if 'src' in layer:
                        from rasterio.plot import show
                        show(layer['src'], ax=ax, alpha=0.7)
                else:
                    if 'gdf' in layer:
                        layer['gdf'].plot(ax=ax, alpha=0.7, edgecolor='white', facecolor='none')
            except Exception as e:
                print(f"Erreur d'affichage: {e}")
        
        ax.set_title("Carte - Logiciel Spatial", color='white', fontsize=14)
        ax.tick_params(colors='white', labelsize=10)
        ax.grid(True, alpha=0.3, color='gray')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def zoom_in(self):
        ax = self.figure.gca()
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        xc, yc = (xlim[0]+xlim[1])/2, (ylim[0]+ylim[1])/2
        xr, yr = (xlim[1]-xlim[0])*0.8, (ylim[1]-ylim[0])*0.8
        ax.set_xlim(xc-xr/2, xc+xr/2)
        ax.set_ylim(yc-yr/2, yc+yr/2)
        self.canvas.draw()
        self.status_label.setText("Zoom avant")
    
    def zoom_out(self):
        ax = self.figure.gca()
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        xc, yc = (xlim[0]+xlim[1])/2, (ylim[0]+ylim[1])/2
        xr, yr = (xlim[1]-xlim[0])*1.25, (ylim[1]-ylim[0])*1.25
        ax.set_xlim(xc-xr/2, xc+xr/2)
        ax.set_ylim(yc-yr/2, yc+yr/2)
        self.canvas.draw()
        self.status_label.setText("Zoom arrière")
    
    def reset_view(self):
        self.plot_layers()
        self.status_label.setText("Vue réinitialisée")
    
    def save_map(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la carte", "", 
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filename:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            self.status_label.setText(f"✅ Carte sauvegardée: {os.path.basename(filename)}")

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

class InterfaceQGIS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Logiciel Spatial - Version Avancée")
        self.setGeometry(100, 100, 1400, 900)
        
        self.layers_data = []
        self.mesure_tool = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbars()
        self.setup_docks()
        self.setup_statusbar()
        
        self.projet_manager = ProjetManager(self)
        
    def setup_ui(self):
        self.chargeur = ChargeurCarto(self)
        self.setCentralWidget(self.chargeur)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📁 Nouveau projet", self.nouveau_projet, "Ctrl+N")
        file_menu.addAction("📂 Ouvrir projet", self.ouvrir_projet, "Ctrl+O")
        file_menu.addAction("💾 Sauvegarder projet", self.sauvegarder_projet, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("📂 Charger Shapefile", self.chargeur.load_shapefile)
        file_menu.addAction("🌍 Charger GeoJSON", self.chargeur.load_geojson)
        file_menu.addAction("🖼️ Charger GeoTIFF", self.chargeur.load_geotiff)
        file_menu.addAction("🏙️ Charger OSM", self.chargeur.load_osm)
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Outils
        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction("📏 Mesurer", self.activate_measure)
        tools_menu.addAction("🗑️ Effacer mesures", self.clear_measure)
        tools_menu.addSeparator()
        tools_menu.addAction("🔍 Zoom avant", self.chargeur.zoom_in)
        tools_menu.addAction("🔍 Zoom arrière", self.chargeur.zoom_out)
        tools_menu.addAction("🔄 Réinitialiser vue", self.chargeur.reset_view)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🗂️ Couches", self.toggle_layers_panel)
        view_menu.addAction("📋 Propriétés", self.toggle_properties_panel)
        view_menu.addAction("📖 Légende", self.toggle_legend_panel)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def setup_toolbars(self):
        # Barre d'outils Fichier
        file_toolbar = self.addToolBar("Fichier")
        file_toolbar.addAction("📁 Nouveau", self.nouveau_projet)
        file_toolbar.addAction("📂 Ouvrir", self.ouvrir_projet)
        file_toolbar.addAction("💾 Sauvegarder", self.sauvegarder_projet)
        
        # Barre d'outils Carte
        map_toolbar = self.addToolBar("Carte")
        map_toolbar.addAction("🔍 Zoom +", self.chargeur.zoom_in)
        map_toolbar.addAction("🔍 Zoom -", self.chargeur.zoom_out)
        map_toolbar.addAction("🔄 Reset", self.chargeur.reset_view)
        map_toolbar.addSeparator()
        map_toolbar.addAction("📏 Mesure", self.activate_measure)
        
    def setup_docks(self):
        # Panneau Couches
        self.layers_dock = QDockWidget("🗂️ Couches", self)
        self.layers_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        layers_widget = QWidget()
        layers_layout = QVBoxLayout(layers_widget)
        
        self.layer_list = QTreeWidget()
        self.layer_list.setHeaderLabel("Couches chargées")
        self.layer_list.setIndentation(0)
        self.layer_list.itemClicked.connect(self.on_layer_selected)
        layers_layout.addWidget(self.layer_list)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("➕ Ajouter", clicked=self.chargeur.load_shapefile))
        btn_layout.addWidget(QPushButton("➖ Supprimer", clicked=self.remove_layer))
        layers_layout.addLayout(btn_layout)
        
        self.layers_dock.setWidget(layers_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers_dock)
        
        # Panneau Propriétés
        self.properties_dock = QDockWidget("📋 Propriétés", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 10px;
            }
        """)
        self.properties_dock.setWidget(self.properties_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        
        # Panneau Légende
        self.legend_dock = QDockWidget("📖 Légende", self)
        self.legend_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.legende = LegendeWidget()
        self.legend_dock.setWidget(self.legende)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.legend_dock)
        
        # Organiser les panneaux
        self.tabifyDockWidget(self.layers_dock, self.properties_dock)
        self.tabifyDockWidget(self.layers_dock, self.legend_dock)
    
    def setup_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("Coordonnées: -")
        self.status.addPermanentWidget(self.coord_label)
        self.status.showMessage("Prêt")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_coords)
        self.timer.start(1000)
    
    def update_coords(self):
        if hasattr(self.chargeur, 'figure') and self.chargeur.figure.axes:
            ax = self.chargeur.figure.gca()
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            self.coord_label.setText(f"Centre: {(xlim[0]+xlim[1])/2:.2f}°, {(ylim[0]+ylim[1])/2:.2f}°")
    
    def add_layer_to_list(self, filename, layer_type):
        item = QTreeWidgetItem(self.layer_list)
        icon = "🛰️" if layer_type == 'raster' else "📌"
        item.setText(0, f"{icon} {os.path.basename(filename)}")
        item.setCheckState(0, Qt.Checked)
        self.layers_data.append({
            'name': filename,
            'type': layer_type,
            'item': item
        })
        self.legende.update_legend(self.chargeur.files_loaded)
    
    def on_layer_selected(self, item):
        for layer in self.layers_data:
            if layer['item'] == item:
                info = f"🗺️ COUCHE\n========\n"
                info += f"Fichier: {os.path.basename(layer['name'])}\n"
                info += f"Type: {'Raster' if layer['type']=='raster' else 'Vectoriel'}\n"
                info += f"Statut: Chargée"
                self.properties_text.setText(info)
                break
    
    def remove_layer(self):
        current = self.layer_list.currentItem()
        if current:
            for i, layer in enumerate(self.layers_data):
                if layer['item'] == current:
                    self.layers_data.pop(i)
                    break
            self.layer_list.invisibleRootItem().removeChild(current)
            
            if self.chargeur.files_loaded:
                self.chargeur.files_loaded.pop()
                self.chargeur.plot_layers()
                self.legende.update_legend(self.chargeur.files_loaded)
    
    def nouveau_projet(self):
        self.projet_manager.nouveau_projet()
    
    def ouvrir_projet(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir projet", "", 
            "Projet JSON (*.json);;Tous (*.*)"
        )
        if filename:
            self.projet_manager.charger_projet(filename)
    
    def sauvegarder_projet(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder projet", "", 
            "Projet JSON (*.json)"
        )
        if filename:
            self.projet_manager.sauvegarder_projet(filename)
    
    def activate_measure(self):
        if self.mesure_tool:
            self.mesure_tool.deactivate()
        self.mesure_tool = MesureTool(self.chargeur.canvas, self.status.showMessage)
        self.mesure_tool.activate()
    
    def clear_measure(self):
        if self.mesure_tool:
            self.mesure_tool.clear()
    
    def toggle_layers_panel(self):
        self.layers_dock.setVisible(not self.layers_dock.isVisible())
    
    def toggle_properties_panel(self):
        self.properties_dock.setVisible(not self.properties_dock.isVisible())
    
    def toggle_legend_panel(self):
        self.legend_dock.setVisible(not self.legend_dock.isVisible())
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation",
            " LOGICIEL SPATIAL - Version Avancée\n\n"
            "Nouvelles fonctionnalités:\n"
            "• Outil de mesure de distances\n"
            "• Gestionnaire de projet (JSON)\n"
            "• Légende automatique\n"
            "• Barres d'outils complètes\n"
            "• Interface style QGIS améliorée")
    
    def about(self):
        QMessageBox.about(self, "À propos",
            " LOGICIEL SPATIAL\n"
            "Version 3.0 - Avancée\n\n"
            "Développé avec:\n"
            "• PySide6\n"
            "• GeoPandas\n"
            "• Matplotlib\n\n"
            "© 2026")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = InterfaceQGIS()
    window.show()
    sys.exit(app.exec())