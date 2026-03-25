#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 LOGICIEL SPATIAL - Version TEK (Style QGIS Professionnel)
=============================================================
Avec rendu cartographique de type QGIS utilisant TEK
"""

import os
os.environ["QT_API"] = "pyside6"

import sys
import json
import pandas as pd
import geopandas as gpd
from datetime import datetime

# Import TEK pour la cartographie stylisée
import tek as tk
from tek import *

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# GESTIONNAIRE DE STYLES TEK (COMME QGIS)
# ============================================================================

class TekStyleManager:
    """Gestionnaire de styles cartographiques inspiré de QGIS"""
    
    # Styles prédéfinis pour différents types de données
    STYLES = {
        'region': {
            'fill_color': '#4CAF50',
            'edge_color': '#2E7D32',
            'fill_alpha': 0.4,
            'edge_width': 1.5,
            'label_size': 10,
            'label_color': 'white',
            'label_weight': 'bold',
            'hatch': ''
        },
        'commune': {
            'fill_color': '#FFA500',
            'edge_color': '#FF8C00',
            'fill_alpha': 0.3,
            'edge_width': 0.8,
            'label_size': 8,
            'label_color': 'yellow',
            'label_weight': 'normal',
            'hatch': '///'
        },
        'route': {
            'fill_color': 'none',
            'edge_color': '#808080',
            'edge_width': 0.5,
            'line_style': 'solid'
        },
        'hydro': {
            'fill_color': '#2196F3',
            'edge_color': '#1976D2',
            'fill_alpha': 0.5,
            'hatch': '...'
        },
        'raster': {
            'alpha': 0.8,
            'colormap': 'viridis'
        }
    }
    
    @classmethod
    def apply_style(cls, ax, gdf, style_type='vector', **kwargs):
        """Applique un style TEK à la couche"""
        style = cls.STYLES.get(style_type, cls.STYLES['region']).copy()
        style.update(kwargs)
        
        if style_type == 'raster':
            return cls._style_raster(ax, gdf, style)
        else:
            return cls._style_vector(ax, gdf, style)
    
    @classmethod
    def _style_vector(cls, ax, gdf, style):
        """Style pour données vectorielles"""
        return gdf.plot(
            ax=ax,
            color=style.get('fill_color', 'none'),
            edgecolor=style.get('edge_color', 'black'),
            linewidth=style.get('edge_width', 1),
            alpha=style.get('fill_alpha', 1),
            hatch=style.get('hatch', '')
        )
    
    @classmethod
    def _style_raster(cls, ax, raster, style):
        """Style pour données raster"""
        from rasterio.plot import show
        return show(
            raster,
            ax=ax,
            alpha=style.get('alpha', 0.8),
            cmap=style.get('colormap', 'viridis')
        )

# ============================================================================
# CHARGEUR CARTOGRAPHIQUE AVEC TEK
# ============================================================================

class ChargeurCartoTek(QWidget):
    """Chargeur de fichiers avec rendu TEK"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files_loaded = []
        self.style_manager = TekStyleManager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils TEK
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Styles prédéfinis
        self.style_combo = QComboBox()
        self.style_combo.addItems(['Classique', 'Satellite', 'Relief', 'Nuit', 'Pastel'])
        self.style_combo.currentTextChanged.connect(self.change_style)
        toolbar.addWidget(QLabel("  Style: "))
        toolbar.addWidget(self.style_combo)
        
        toolbar.addSeparator()
        
        # Options de rendu
        self.legend_btn = QPushButton("📖 Légende")
        self.legend_btn.setCheckable(True)
        self.legend_btn.setChecked(True)
        toolbar.addWidget(self.legend_btn)
        
        self.grid_btn = QPushButton("🔲 Grille")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        toolbar.addWidget(self.grid_btn)
        
        layout.addWidget(toolbar)
        
        # Canvas
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.status_label = QLabel("Prêt - Style TEK actif")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def change_style(self, style_name):
        """Change le style global de la carte"""
        styles = {
            'Classique': {'bg': '#0a1a2a', 'grid': '#333', 'text': 'white'},
            'Satellite': {'bg': '#000000', 'grid': '#222', 'text': '#ccc'},
            'Relief': {'bg': '#2a2a1a', 'grid': '#443322', 'text': '#ffddaa'},
            'Nuit': {'bg': '#03030a', 'grid': '#1a1a3a', 'text': '#aaccff'},
            'Pastel': {'bg': '#2a2a3a', 'grid': '#5a5a7a', 'text': '#ffddaa'}
        }
        style = styles.get(style_name, styles['Classique'])
        self.figure.set_facecolor(style['bg'])
        self.plot_layers()
        self.status_label.setText(f"Style {style_name} appliqué")
    
    def load_file(self, filename):
        """Charge un fichier avec détection automatique"""
        try:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.shp', '.geojson', '.json']:
                gdf = gpd.read_file(filename)
                
                # Déterminer le type
                layer_type = 'vector'
                if 'region' in filename.lower() or 'admin1' in filename.lower():
                    layer_type = 'region'
                elif 'commune' in filename.lower() or 'admin4' in filename.lower():
                    layer_type = 'commune'
                elif 'route' in filename.lower():
                    layer_type = 'route'
                elif 'hydro' in filename.lower() or 'eau' in filename.lower():
                    layer_type = 'hydro'
                
                self.files_loaded.append({
                    'data': gdf,
                    'name': filename,
                    'type': layer_type
                })
                
            elif ext in ['.tif', '.tiff']:
                import rasterio
                src = rasterio.open(filename)
                self.files_loaded.append({
                    'data': src,
                    'name': filename,
                    'type': 'raster'
                })
            
            # Ajouter à l'arbre des couches
            if self.parent and hasattr(self.parent, 'add_layer'):
                self.parent.add_layer(filename, layer_type)
            
            self.plot_layers()
            self.status_label.setText(f"✅ Chargé: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def plot_layers(self):
        """Affiche toutes les couches avec styles TEK"""
        self.figure.clear()
        
        if not self.files_loaded:
            self.canvas.draw()
            return
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.figure.get_facecolor())
        
        # Calculer les limites
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')
        
        # Afficher chaque couche
        for layer in self.files_loaded:
            try:
                visible = True
                if self.parent and hasattr(self.parent, 'is_layer_visible'):
                    visible = self.parent.is_layer_visible(layer['name'])
                
                if visible:
                    if layer['type'] == 'raster':
                        TekStyleManager.apply_style(ax, layer['data'], 'raster')
                    else:
                        TekStyleManager.apply_style(ax, layer['data'], layer['type'])
                        
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
        
        # Ajouter la grille si demandée
        if self.grid_btn.isChecked():
            ax.grid(True, alpha=0.3, color='#666', linestyle='--')
        
        ax.set_title("Carte - Style TEK", color='white', fontsize=14)
        ax.tick_params(colors='white')
        
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
# INTERFACE PRINCIPALE AVEC TEK
# ============================================================================

class TekGISApp(QMainWindow):
    """Application principale avec rendu TEK"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 TEK - Spatial GIS (Style QGIS)")
        self.setGeometry(100, 100, 1400, 900)
        
        self.layers = []
        self.init_ui()
        
    def init_ui(self):
        # Widget central avec TEK
        self.chargeur = ChargeurCartoTek(self)
        self.setCentralWidget(self.chargeur)
        
        self.create_menus()
        self.create_toolbars()
        self.create_docks()
        self.create_statusbar()
        
    def create_menus(self):
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("📁 Nouveau", self.new_project, "Ctrl+N")
        file_menu.addAction("📂 Ouvrir", self.open_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("❌ Quitter", self.close, "Ctrl+Q")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("🔍 Zoom +", self.chargeur.zoom_in, "Ctrl++")
        view_menu.addAction("🔍 Zoom -", self.chargeur.zoom_out, "Ctrl+-")
        view_menu.addAction("🌍 Étendre", self.chargeur.zoom_full)
        
        # Menu Styles
        style_menu = menubar.addMenu("&Styles")
        for style in ['Classique', 'Satellite', 'Relief', 'Nuit', 'Pastel']:
            action = QAction(style, self)
            action.triggered.connect(lambda checked, s=style: self.chargeur.change_style(s))
            style_menu.addAction(action)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ À propos", self.about)
    
    def create_toolbars(self):
        # Barre d'outils Fichier
        file_toolbar = self.addToolBar("Fichier")
        file_toolbar.addAction("📁 Nouveau", self.new_project)
        file_toolbar.addAction("📂 Ouvrir", self.open_file)
        
        # Barre d'outils Navigation
        nav_toolbar = self.addToolBar("Navigation")
        nav_toolbar.addAction("🔍 Zoom +", self.chargeur.zoom_in)
        nav_toolbar.addAction("🔍 Zoom -", self.chargeur.zoom_out)
        nav_toolbar.addAction("🌍 Étendre", self.chargeur.zoom_full)
    
    def create_docks(self):
        # Panneau Couches
        self.layer_dock = QDockWidget("🗂️ Couches", self)
        self.layer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Couches du projet")
        self.layer_tree.setIndentation(0)
        self.layer_tree.itemClicked.connect(self.on_layer_click)
        
        self.layer_dock.setWidget(self.layer_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layer_dock)
        
        # Panneau Propriétés
        self.prop_dock = QDockWidget("📋 Propriétés", self)
        self.prop_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        
        self.prop_text = QTextEdit()
        self.prop_text.setReadOnly(True)
        self.prop_text.setStyleSheet("background: #1a1a2a; color: #0f0; font-family: monospace;")
        self.prop_dock.setWidget(self.prop_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.prop_dock)
    
    def create_statusbar(self):
        self.status = self.statusBar()
        self.coord_label = QLabel("Coordonnées: -")
        self.style_label = QLabel("Style: Classique")
        self.status.addPermanentWidget(self.coord_label)
        self.status.addPermanentWidget(self.style_label)
        self.status.showMessage("Prêt - TEK GIS")
        
        # Timer pour mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
    
    def update_status(self):
        if hasattr(self.chargeur, 'figure') and self.chargeur.figure.axes:
            ax = self.chargeur.figure.gca()
            xl, yl = ax.get_xlim(), ax.get_ylim()
            self.coord_label.setText(f"Centre: {(xl[0]+xl[1])/2:.2f}°, {(yl[0]+yl[1])/2:.2f}°")
            self.style_label.setText(f"Style: {self.chargeur.style_combo.currentText()}")
    
    def add_layer(self, filename, layer_type):
        """Ajoute une couche à l'arbre"""
        icons = {
            'region': '🟩',
            'commune': '🟧',
            'route': '🛣️',
            'hydro': '💧',
            'raster': '🛰️'
        }
        icon = icons.get(layer_type, '📌')
        
        item = QTreeWidgetItem(self.layer_tree)
        item.setText(0, f"{icon} {os.path.basename(filename)}")
        item.setCheckState(0, Qt.Checked)
        item.setData(0, Qt.UserRole, {'name': filename, 'type': layer_type})
        self.layer_tree.addTopLevelItem(item)
        self.layers.append({'name': filename, 'type': layer_type, 'item': item})
    
    def is_layer_visible(self, filename):
        """Vérifie si une couche est visible"""
        for layer in self.layers:
            if layer['name'] == filename:
                return layer['item'].checkState(0) == Qt.Checked
        return True
    
    def on_layer_click(self, item):
        """Affiche les propriétés de la couche"""
        data = item.data(0, Qt.UserRole)
        if data:
            info = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📁 {os.path.basename(data['name'])}
 TYPE: {data['type'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATISTIQUES
───────────────
• Visible: {'Oui' if item.checkState(0) == Qt.Checked else 'Non'}
• Style: {self.chargeur.style_combo.currentText()}

🎨 OPTIONS DE RENDU
──────────────────
• Rendu TEK activé
• Styles prédéfinis disponibles
• Grille: {'Oui' if self.chargeur.grid_btn.isChecked() else 'Non'}
"""
            self.prop_text.setText(info)
    
    def new_project(self):
        self.chargeur.files_loaded.clear()
        self.chargeur.plot_layers()
        self.layer_tree.clear()
        self.layers.clear()
    
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir fichier", "", 
            "Fichiers supportés (*.shp *.geojson *.tif);;Tous (*.*)"
        )
        if filename:
            self.chargeur.load_file(filename)
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation",
            "📚 TEK - Spatial GIS\n\n"
            "Styles disponibles:\n"
            "• Classique - Style cartographique standard\n"
            "• Satellite - Rendu fond sombre\n"
            "• Relief - Tons terreux\n"
            "• Nuit - Couleurs nocturnes\n"
            "• Pastel - Tons doux\n\n"
            "Raccourcis:\n"
            "Ctrl+O: Ouvrir fichier\n"
            "Ctrl+N: Nouveau projet\n"
            "Ctrl++: Zoom avant\n"
            "Ctrl+-: Zoom arrière")
    
    def about(self):
        QMessageBox.about(self, "À propos",
            "🚀 TEK - Spatial GIS\n"
            "Version 1.0\n\n"
            "Moteur de rendu cartographique TEK\n"
            "Style inspiré de QGIS\n\n"
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
    
    window = TekGISApp()
    window.show()
    sys.exit(app.exec())