# -*- coding: utf-8 -*-
"""
JOMAN - LOGICIEL SIG UNIVERSEL
Version autonome - Fonctionne avec tous les pays et tous les formats
"""

import sys
import os
import math
import json
import geopandas as gpd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from shapely.geometry import Point

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=" * 60)
print("JOMAN - SIG UNIVERSEL")
print("Version autonome - Tous pays, tous formats")
print("=" * 60)

class MapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.figure = Figure(figsize=(12, 9), facecolor='#1a2a3a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        self.current_gdf = None
        self.current_name = None
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def on_click(self, event):
        if event.inaxes is None or self.current_gdf is None:
            return
        point = Point(event.xdata, event.ydata)
        for idx, row in self.current_gdf.iterrows():
            if row.geometry and row.geometry.contains(point):
                self.main_window.show_info(idx, row)
                break
    
    def find_name_column(self, gdf):
        """Trouve automatiquement la colonne des noms (universel)"""
        # Liste exhaustive des noms de colonnes possibles dans tous les pays
        name_patterns = [
            'name', 'NAME', 'Nom', 'NOM', 'nom',
            'admin_name', 'ADMIN_NAME',
            'adm1_name', 'adm2_name', 'adm3_name', 'adm4_name',
            'region', 'REGION', 'Region', 'province', 'PROVINCE', 'Province',
            'state', 'STATE', 'State', 'county', 'COUNTY', 'County',
            'district', 'DISTRICT', 'District', 'city', 'CITY', 'City',
            'town', 'TOWN', 'Town', 'village', 'VILLAGE', 'Village',
            'label', 'LABEL', 'Label', 'libelle', 'LIBELLE', 'Libelle',
            'title', 'TITLE', 'Title', 'commune', 'COMMUNE', 'Commune',
            'departement', 'DEPARTEMENT', 'Departement', 'prefecture', 'PREFECTURE',
            'code', 'CODE', 'id', 'ID', 'index', 'INDEX'
        ]
        
        for col in name_patterns:
            if col in gdf.columns:
                try:
                    first_val = gdf[col].iloc[0]
                    if first_val and str(first_val) not in ['nan', 'None', '']:
                        return col
                except:
                    pass
        
        # Si aucune colonne trouvée, prendre la premiere colonne non-geometrique
        for col in gdf.columns:
            if col != 'geometry':
                return col
        return None
    
    def display_data(self, gdf, filename):
        """Affiche les donnees de maniere universelle"""
        self.current_gdf = gdf
        self.current_name = filename
        self.ax.clear()
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        # Determiner le type de geometrie
        geom_type = gdf.geometry.type.iloc[0]
        
        if 'Polygon' in geom_type:
            gdf.plot(ax=self.ax, color='#4ECDC4', edgecolor='white', linewidth=0.8, alpha=0.7)
        elif 'Line' in geom_type:
            gdf.plot(ax=self.ax, color='#FFB347', linewidth=1.5, alpha=0.8)
        else:
            gdf.plot(ax=self.ax, color='#FF6B6B', markersize=30, marker='o', alpha=0.8)
        
        # Ajouter les etiquettes
        name_col = self.find_name_column(gdf)
        
        if name_col:
            for idx, row in gdf.iterrows():
                try:
                    if row.geometry and not row.geometry.is_empty:
                        if 'Point' in geom_type:
                            x, y = row.geometry.x, row.geometry.y
                        else:
                            centroid = row.geometry.centroid
                            x, y = centroid.x, centroid.y
                        
                        label_text = str(row[name_col])[:30]
                        if label_text and label_text not in ['nan', 'None', '']:
                            self.ax.text(x, y, label_text,
                                       fontsize=9, color='#FFE66D', fontweight='bold',
                                       ha='center', va='center',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a2a3a', alpha=0.8))
                except:
                    pass
        
        # Ajuster les limites
        bounds = gdf.total_bounds
        margin_x = (bounds[2] - bounds[0]) * 0.05
        margin_y = (bounds[3] - bounds[1]) * 0.05
        self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
        self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
        
        # Barre d'echelle
        self.add_scale_bar()
        
        # Titre
        self.ax.set_title(f"JOMAN - {filename} ({len(gdf)} entites)", color='white', fontsize=12)
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def add_scale_bar(self):
        """Barre d'echelle automatique"""
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
        else:
            scale_len, text = 10, "10 km"
            
        scale_deg = scale_len / 111
        x_end = x + scale_deg
        
        self.ax.plot([x, x_end], [y, y], 'white', linewidth=2)
        self.ax.text(x + scale_deg/2, y - y*0.003, text, ha='center', fontsize=8, color='white')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JOMAN - SIG Universel")
        self.setGeometry(100, 100, 1300, 800)
        self.setAcceptDrops(True)
        self.dark_theme = True
        
        self.setup_ui()
        self.statusBar().showMessage("JOMAN pret - Glissez-de posez n'importe quel fichier geospatial")
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre
        title = QLabel("JOMAN")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # Boutons
        self.btn_load = QPushButton("Charger un fichier")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 12px; font-size: 14px; background-color: #4ECDC4; color: #1a2a3a; font-weight: bold;")
        left_layout.addWidget(self.btn_load)
        
        self.btn_clear = QPushButton("Effacer")
        self.btn_theme = QPushButton("Theme")
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_theme.setStyleSheet("padding: 8px; background-color: #4ECDC4; color: #1a2a3a;")
        left_layout.addWidget(self.btn_theme)
        self.btn_clear.clicked.connect(self.clear_data)
        self.btn_clear.setStyleSheet("padding: 8px; background-color: #FF6B6B; color: white;")
        left_layout.addWidget(self.btn_clear)
        
        left_layout.addWidget(QLabel(""))
        
        # Liste
        left_layout.addWidget(QLabel("Liste des entites:"))
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item_click)
        left_layout.addWidget(self.item_list)
        # Barre de recherche avancee
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #1a2a3a; border: 1px solid #4ECDC4; border-radius: 5px;")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_icon = QLabel("🔍")
        search_layout.addWidget(self.search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.search_features)
        self.search_input.setStyleSheet("background-color: #1a2a3a; color: white; border: none; padding: 5px;")
        search_layout.addWidget(self.search_input)
        
        self.search_clear = QPushButton("✖")
        self.search_clear.setFixedSize(20, 20)
        self.search_clear.setStyleSheet("background-color: #FF6B6B; color: white; border: none; border-radius: 10px;")
        self.search_clear.clicked.connect(self.clear_search)
        search_layout.addWidget(self.search_clear)
        
        left_layout.addWidget(search_frame)
        
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(100)
        self.search_results.itemClicked.connect(self.on_search_click)
        left_layout.addWidget(self.search_results)
        
        # Informations
        self.info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        self.info_text.setStyleSheet("background-color: #1a2a3a; color: #FFE66D; font-size: 11px;")
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        # Statistiques
        self.stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QLabel()
        self.stats_text.setStyleSheet("color: #4ECDC4; font-size: 11px;")
        stats_layout.addWidget(self.stats_text)
        left_layout.addWidget(self.stats_group)
        
        # Legende
        legend_group = QGroupBox("Legende")
        legend_layout = QVBoxLayout(legend_group)
        legend_layout.addWidget(QLabel("Polygones : Regions, pays"))
        legend_layout.addWidget(QLabel("Lignes : Routes, frontieres"))
        legend_layout.addWidget(QLabel("Points : Villes, points"))
        legend_layout.addWidget(QLabel("Noms : Detection automatique"))
        left_layout.addWidget(legend_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Canvas
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
        
        # Status pour le drag & drop
        self.setAcceptDrops(True)
        self.dark_theme = True
    
    def load_file(self):
        """Charge n'importe quel fichier geospatial"""
        formats = "Tous fichiers (*.shp *.geojson *.json *.kml *.kmz);;Shapefile (*.shp);;GeoJSON (*.geojson *.json);;KML/KMZ (*.kml *.kmz)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", formats)
        
        if filename:
            self.load_any_file(filename)
    
    def load_any_file(self, filename):
        """Charge et affiche n'importe quel fichier"""
        try:
            gdf = gpd.read_file(filename)
            name = os.path.basename(filename)
            
            self.map_canvas.display_data(gdf, name)
            
            # Remplir la liste
            self.item_list.clear()
            name_col = self.map_canvas.find_name_column(gdf)
            
            for idx, row in gdf.iterrows():
                if name_col and row[name_col]:
                    display_name = str(row[name_col])[:40]
                else:
                    display_name = f"Entite {idx}"
                self.item_list.addItem(display_name)
                self.item_list.item(idx).setData(Qt.UserRole, idx)
            
            # Statistiques
            geom_type = gdf.geometry.type.iloc[0]
            stats = f"Entites: {len(gdf)}\nType: {geom_type}\n"
            
            if 'Polygon' in geom_type:
                area = gdf.geometry.area.sum() * 111 * 111
                stats += f"Surface: {area:,.0f} km2"
            elif 'Line' in geom_type:
                length = gdf.geometry.length.sum() * 111
                stats += f"Longueur: {length:,.0f} km"
            
            self.stats_text.setText(stats)
            self.statusBar().showMessage(f"Charge: {name}")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger:\n{str(e)}")
    
    def clear_data(self):
        """Efface les donnees actuelles"""
        self.map_canvas.current_gdf = None
        self.map_canvas.ax.clear()
        self.map_canvas.ax.set_facecolor('#1a2a3a')
        self.map_canvas.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        self.map_canvas.ax.text(0.5, 0.5, "JOMAN\nGlissez-de posez un fichier", 
                               transform=self.map_canvas.ax.transAxes, ha='center', va='center',
                               color='white', fontsize=14)
        self.map_canvas.canvas.draw()
        self.item_list.clear()
        self.info_text.clear()
        self.stats_text.clear()
        self.statusBar().showMessage("Donnees effacees")
    
    def on_item_click(self, item):
        """Zoom sur l'entite selectionnee"""
        idx = item.data(Qt.UserRole)
        if idx is not None and self.map_canvas.current_gdf is not None:
            geom = self.map_canvas.current_gdf.iloc[idx].geometry
            bounds = geom.bounds
            margin_x = (bounds[2] - bounds[0]) * 0.1
            margin_y = (bounds[3] - bounds[1]) * 0.1
            self.map_canvas.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.map_canvas.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.map_canvas.canvas.draw()
            self.statusBar().showMessage(f"Zoom sur: {item.text()}")
    
    def show_info(self, idx, row):
        """Affiche les informations de l'entite"""
        info = "=== INFORMATIONS ===\n\n"
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val and str(val) not in ['nan', 'None', '']:
                    info += f"{col}: {val}\n"
        self.info_text.setText(info)
        self.statusBar().showMessage(f"Entite {idx} selectionnee")
    
    def dragEnterEvent(self, event):
        """Accepte le glisser-deposer"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Traite le fichier depose"""
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename.endswith(('.shp', '.geojson', '.json', '.kml', '.kmz')):
                self.load_any_file(filename)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 42, 58))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(26, 42, 58))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    print("=" * 60)
    print("JOMAN - SIG Universel")
    print("Fonctionne avec tous les pays et tous les formats")
    print("")
    print("Formats supportes:")
    print("  - Shapefile (.shp)")
    print("  - GeoJSON (.geojson, .json)")
    print("  - KML/KMZ (.kml, .kmz)")
    print("")
    print("Glissez-de posez n'importe quel fichier geospatial")
    print("=" * 60)
    
    sys.exit(app.exec())








