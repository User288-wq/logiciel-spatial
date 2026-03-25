#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 LOGICIEL SPATIAL - Interface Style QGIS avec Étiquettes
===========================================================
Fonctionnalités ajoutées :
- Affichage des étiquettes pour les régions et communes
- Personnalisation des styles d'étiquettes
- Support des données administratives du Sénégal
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
# GESTIONNAIRE D'ÉTIQUETTES POUR RÉGIONS ET COMMUNES
# ============================================================================

class EtiquetteManager:
    """Gère l'affichage des étiquettes sur les cartes"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.etiquettes = []
        self.style_regions = {
            'couleur': 'white',
            'taille': 10,
            'poids': 'bold',
            'decallage': (0, 5)
        }
        self.style_communes = {
            'couleur': 'yellow',
            'taille': 8,
            'poids': 'normal',
            'decallage': (0, 3)
        }
        self.afficher_regions = True
        self.afficher_communes = True
        
    def ajouter_etiquette_region(self, ax, nom, x, y):
        """Ajoute une étiquette pour une région"""
        if not self.afficher_regions:
            return
            
        texte = ax.text(x, y, nom, 
                       fontsize=self.style_regions['taille'],
                       fontweight=self.style_regions['poids'],
                       color=self.style_regions['couleur'],
                       ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor='#1a1a2a', 
                                alpha=0.7,
                                edgecolor='#4CAF50'))
        self.etiquettes.append(texte)
        
    def ajouter_etiquette_commune(self, ax, nom, x, y):
        """Ajoute une étiquette pour une commune"""
        if not self.afficher_communes:
            return
            
        texte = ax.text(x, y, nom,
                       fontsize=self.style_communes['taille'],
                       fontweight=self.style_communes['poids'],
                       color=self.style_communes['couleur'],
                       ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.2",
                                facecolor='#0a1a2a',
                                alpha=0.6,
                                edgecolor='#FFA500'))
        self.etiquettes.append(texte)
        
    def nettoyer_etiquettes(self):
        """Supprime toutes les étiquettes"""
        for etiq in self.etiquettes:
            etiq.remove()
        self.etiquettes.clear()
        
    def mettre_a_jour_style(self, type_etiq, **kwargs):
        """Met à jour le style des étiquettes"""
        if type_etiq == 'region':
            self.style_regions.update(kwargs)
        elif type_etiq == 'commune':
            self.style_communes.update(kwargs)
            
    def basculer_affichage(self, type_etiq):
        """Active/désactive l'affichage d'un type d'étiquette"""
        if type_etiq == 'region':
            self.afficher_regions = not self.afficher_regions
        elif type_etiq == 'commune':
            self.afficher_communes = not self.afficher_communes

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
        self.etiquette_manager = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Boutons de chargement
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
        
        # Boutons d'étiquettes
        self.btn_region = QAction("🏷️ Régions", self)
        self.btn_region.setCheckable(True)
        self.btn_region.setChecked(True)
        self.btn_region.triggered.connect(self.toggle_regions)
        toolbar.addAction(self.btn_region)
        
        self.btn_commune = QAction("🏷️ Communes", self)
        self.btn_commune.setCheckable(True)
        self.btn_commune.setChecked(True)
        self.btn_commune.triggered.connect(self.toggle_communes)
        toolbar.addAction(self.btn_commune)
        
        toolbar.addSeparator()
        
        # Boutons de zoom
        self.btn_zoom_in = QAction("🔍 Zoom +", self)
        self.btn_zoom_in.triggered.connect(self.zoom_in)
        toolbar.addAction(self.btn_zoom_in)
        
        self.btn_zoom_out = QAction("🔍 Zoom -", self)
        self.btn_zoom_out.triggered.connect(self.zoom_out)
        toolbar.addAction(self.btn_zoom_out)
        
        self.btn_reset = QAction("🔄 Reset", self)
        self.btn_reset.triggered.connect(self.reset_view)
        toolbar.addAction(self.btn_reset)
        
        layout.addWidget(toolbar)
        
        # Canvas
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Initialiser le gestionnaire d'étiquettes
        self.etiquette_manager = EtiquetteManager(self.canvas)
        
        # Barre d'état
        self.status_label = QLabel("Prêt - Chargez un fichier")
        self.status_label.setStyleSheet("color: #888888; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def toggle_regions(self, checked):
        """Active/désactive les étiquettes des régions"""
        if self.etiquette_manager:
            self.etiquette_manager.basculer_affichage('region')
            self.plot_layers()
            self.status_label.setText("Étiquettes des régions " + ("activées" if checked else "désactivées"))
    
    def toggle_communes(self, checked):
        """Active/désactive les étiquettes des communes"""
        if self.etiquette_manager:
            self.etiquette_manager.basculer_affichage('commune')
            self.plot_layers()
            self.status_label.setText("Étiquettes des communes " + ("activées" if checked else "désactivées"))
    
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
            
            # Déterminer le type de couche
            layer_type = 'vector'
            if 'region' in filename.lower() or 'admin1' in filename.lower():
                layer_type = 'region'
            elif 'commune' in filename.lower() or 'admin4' in filename.lower():
                layer_type = 'commune'
            
            self.files_loaded.append({
                'gdf': gdf,
                'name': filename,
                'type': layer_type
            })
            self.plot_layers()
            self.status_label.setText(f"✅ Chargé: {os.path.basename(filename)}")
            
            if self.parent:
                self.parent.add_layer_to_list(filename, layer_type)
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
        """Affiche toutes les couches avec leurs étiquettes"""
        self.figure.clear()
        
        if not self.files_loaded:
            self.canvas.draw()
            return
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#0a1a2a')
        
        # Nettoyer les anciennes étiquettes
        if self.etiquette_manager:
            self.etiquette_manager.nettoyer_etiquettes()
        
        # Afficher chaque couche
        for layer in self.files_loaded:
            try:
                if layer['type'] == 'raster':
                    if 'src' in layer:
                        from rasterio.plot import show
                        show(layer['src'], ax=ax, alpha=0.7)
                else:
                    if 'gdf' in layer:
                        # Définir la couleur selon le type
                        if layer['type'] == 'region':
                            color = '#4CAF50'
                            edgecolor = '#45a049'
                            alpha = 0.3
                        elif layer['type'] == 'commune':
                            color = '#FFA500'
                            edgecolor = '#FF8C00'
                            alpha = 0.2
                        else:
                            color = 'none'
                            edgecolor = 'white'
                            alpha = 0.7
                        
                        layer['gdf'].plot(ax=ax, 
                                        color=color,
                                        edgecolor=edgecolor,
                                        linewidth=1 if layer['type'] != 'vector' else 0.5,
                                        alpha=alpha,
                                        facecolor=color if layer['type'] != 'vector' else 'none')
                        
                        # Ajouter les étiquettes pour les régions et communes
                        if self.etiquette_manager and layer['type'] in ['region', 'commune']:
                            gdf = layer['gdf']
                            
                            # Pour chaque entité, ajouter une étiquette à son centroïde
                            for idx, row in gdf.iterrows():
                                if row.geometry and not row.geometry.is_empty:
                                    # Calculer le centroïde
                                    centroid = row.geometry.centroid
                                    x, y = centroid.x, centroid.y
                                    
                                    # Récupérer le nom (différents noms de colonnes possibles)
                                    nom = None
                                    for col in ['NAME', 'name', 'NOM', 'ADMIN1', 'ADMIN4']:
                                        if col in row and row[col]:
                                            nom = row[col]
                                            break
                                    
                                    if nom:
                                        if layer['type'] == 'region':
                                            self.etiquette_manager.ajouter_etiquette_region(ax, nom, x, y)
                                        elif layer['type'] == 'commune':
                                            self.etiquette_manager.ajouter_etiquette_commune(ax, nom, x, y)
                                            
            except Exception as e:
                print(f"Erreur d'affichage: {e}")
        
        ax.set_title("Carte du Sénégal - Régions et Communes", color='white', fontsize=14)
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
        
        # Ajouter des entrées de légende fixes
        self.ajouter_entree_legende("🟩 Régions", "#4CAF50")
        self.ajouter_entree_legende("🟧 Communes", "#FFA500")
        self.ajouter_entree_legende("⬜ Autres", "white")
        
    def ajouter_entree_legende(self, nom, couleur):
        """Ajoute une entrée fixe dans la légende"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        
        color_label = QLabel("⬤")
        color_label.setStyleSheet(f"color: {couleur}; font-size: 14px;")
        layout.addWidget(color_label)
        
        name_label = QLabel(nom)
        name_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        self.legend_layout.addWidget(widget)
    
    def update_legend(self, layers):
        """Met à jour la légende avec les couches chargées"""
        # Pour l'instant, on garde la légende fixe
        pass

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

class InterfaceQGIS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Carte du Sénégal - Régions et Communes")
        self.setGeometry(100, 100, 1400, 900)
        
        self.layers_data = []
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbars()
        self.setup_docks()
        self.setup_statusbar()
        
    def setup_ui(self):
        self.chargeur = ChargeurCarto(self)
        self.setCentralWidget(self.chargeur)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📁 Nouveau", self.nouveau, "Ctrl+N")
        file_menu.addAction("📂 Ouvrir", self.ouvrir, "Ctrl+O")
        file_menu.addAction("💾 Sauvegarder", self.sauvegarder, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🗂️ Couches", self.toggle_layers_panel)
        view_menu.addAction("📋 Propriétés", self.toggle_properties_panel)
        view_menu.addAction("📖 Légende", self.toggle_legend_panel)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def setup_toolbars(self):
        # Barre d'outils Fichier
        file_toolbar = self.addToolBar("Fichier")
        file_toolbar.addAction("📁 Nouveau", self.nouveau)
        file_toolbar.addAction("📂 Ouvrir", self.ouvrir)
        file_toolbar.addAction("💾 Sauvegarder", self.sauvegarder)
        
        # Barre d'outils Carte
        map_toolbar = self.addToolBar("Carte")
        map_toolbar.addAction("🔍 Zoom +", self.chargeur.zoom_in)
        map_toolbar.addAction("🔍 Zoom -", self.chargeur.zoom_out)
        map_toolbar.addAction("🔄 Reset", self.chargeur.reset_view)
        
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
        self.status.showMessage("Prêt - Chargez les données du Sénégal")
        
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
        
        # Choisir l'icône selon le type
        if layer_type == 'region':
            icon = "🟩"
        elif layer_type == 'commune':
            icon = "🟧"
        else:
            icon = "📌"
            
        item.setText(0, f"{icon} {os.path.basename(filename)}")
        item.setCheckState(0, Qt.Checked)
        self.layers_data.append({
            'name': filename,
            'type': layer_type,
            'item': item
        })
    
    def on_layer_selected(self, item):
        for layer in self.layers_data:
            if layer['item'] == item:
                info = f"🗺️ COUCHE\n========\n"
                info += f"Fichier: {os.path.basename(layer['name'])}\n"
                info += f"Type: {layer['type'].upper()}\n"
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
    
    def nouveau(self):
        self.chargeur.files_loaded.clear()
        self.chargeur.plot_layers()
        self.layer_list.clear()
        self.layers_data.clear()
        self.status.showMessage("Nouveau projet créé")
    
    def ouvrir(self):
        self.chargeur.load_shapefile()
    
    def sauvegarder(self):
        self.chargeur.save_map()
    
    def toggle_layers_panel(self):
        self.layers_dock.setVisible(not self.layers_dock.isVisible())
    
    def toggle_properties_panel(self):
        self.properties_dock.setVisible(not self.properties_dock.isVisible())
    
    def toggle_legend_panel(self):
        self.legend_dock.setVisible(not self.legend_dock.isVisible())
    
    def about(self):
        QMessageBox.about(self, "À propos",
            "🚀 Carte du Sénégal\n"
            "Version 1.0\n\n"
            "Affiche les régions et communes du Sénégal\n"
            "avec étiquettes automatiques\n\n"
            "Données: HDX - OCHA\n"
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