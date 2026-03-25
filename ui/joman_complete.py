# -*- coding: utf-8 -*-
"""
JOMAN - REGIONS DU SENEGAL
Avec support Shapefile et GeoJSON
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
print("JOMAN - CARTE DU SENEGAL")
print("Support: Shapefile (.shp) et GeoJSON (.geojson)")
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
    
    def display_data(self, gdf, name):
        """Affiche les donnees"""
        self.current_gdf = gdf
        self.current_name = name
        self.ax.clear()
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        # Determiner le type de donnees
        geom_type = gdf.geometry.type.iloc[0]
        
        if 'Polygon' in geom_type:
            color = '#4ECDC4'
            gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=1, alpha=0.7)
        elif 'Line' in geom_type:
            color = '#FFB347'
            gdf.plot(ax=self.ax, color=color, linewidth=1.5, alpha=0.8)
        else:
            color = '#FF6B6B'
            gdf.plot(ax=self.ax, color=color, markersize=30, marker='o', alpha=0.8)
        
        # Ajouter les noms (si colonne de nom existe)
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
                        
                        label_text = str(row[name_col])[:25]
                        if label_text and label_text != 'nan' and label_text != 'None':
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
        
        self.ax.set_title(f"JOMAN - {name} ({len(gdf)} entites)", color='white', fontsize=14)
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def find_name_column(self, gdf):
        """Trouve la colonne contenant les noms"""
        name_candidates = ['adm1_name', 'name', 'NAME', 'NOM', 'nom', 'label', 
                          'LIBELLE', 'ville', 'commune', 'region', 'departement']
        for col in name_candidates:
            if col in gdf.columns:
                # Verifier que ce n'est pas vide
                try:
                    if gdf[col].iloc[0] and str(gdf[col].iloc[0]) != 'nan':
                        return col
                except:
                    pass
        return None
    
    def add_scale_bar(self):
        """Ajoute une barre d'echelle"""
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
        self.setWindowTitle("JOMAN - Carte du Senegal")
        self.setGeometry(100, 100, 1300, 800)
        self.setAcceptDrops(True)
        
        self.setup_ui()
        self.statusBar().showMessage("JOMAN pret - Chargez un fichier (SHP ou GeoJSON)")
        
        # Charger automatiquement les regions si disponible
        self.load_default_regions()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre
        title = QLabel("🏆 JOMAN")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # Boutons
        self.btn_load = QPushButton("📂 Charger fichier (SHP/GeoJSON)")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 12px; font-size: 12px; background-color: #4ECDC4; color: #1a2a3a; font-weight: bold;")
        left_layout.addWidget(self.btn_load)
        
        self.btn_regions = QPushButton("🇸🇳 Charger regions Senegal")
        self.btn_regions.clicked.connect(self.load_senegal_regions)
        self.btn_regions.setStyleSheet("padding: 10px; font-size: 11px; background-color: #FFB347; color: #1a2a3a;")
        left_layout.addWidget(self.btn_regions)
        
        left_layout.addWidget(QLabel(""))
        
        # Liste des entites
        left_layout.addWidget(QLabel("📋 LISTE DES ENTITES:"))
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item_click)
        left_layout.addWidget(self.item_list)
        
        # Informations
        self.info_group = QGroupBox("ℹ️ INFORMATIONS")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        self.info_text.setStyleSheet("background-color: #1a2a3a; color: #FFE66D; font-size: 12px;")
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        # Statistiques
        self.stats_group = QGroupBox("📊 STATISTIQUES")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QLabel()
        self.stats_text.setStyleSheet("color: #4ECDC4; font-size: 12px;")
        stats_layout.addWidget(self.stats_text)
        left_layout.addWidget(self.stats_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Canvas
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
    
    def load_file(self):
        """Charge un fichier (SHP ou GeoJSON)"""
        formats = "Fichiers supportes (*.shp *.geojson *.json);;Shapefile (*.shp);;GeoJSON (*.geojson *.json)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", formats)
        
        if filename:
            self.load_data(filename)
    
    def load_data(self, filename):
        """Charge et affiche les donnees"""
        try:
            gdf = gpd.read_file(filename)
            name = os.path.basename(filename)
            
            self.map_canvas.display_data(gdf, name)
            
            # Remplir la liste
            self.item_list.clear()
            name_col = self.map_canvas.find_name_column(gdf)
            
            for idx, row in gdf.iterrows():
                if name_col and row[name_col]:
                    display_name = str(row[name_col])
                else:
                    display_name = f"Entite {idx}"
                self.item_list.addItem(display_name)
                self.item_list.item(idx).setData(Qt.UserRole, idx)
            
            # Statistiques
            stats = f"Entites: {len(gdf)}\n"
            stats += f"Type: {gdf.geometry.type.iloc[0]}\n"
            if 'Polygon' in str(gdf.geometry.type.iloc[0]):
                area = gdf.geometry.area.sum() * 111 * 111
                stats += f"Surface totale: {area:,.0f} km²"
            self.stats_text.setText(stats)
            
            self.statusBar().showMessage(f"Charge: {name}")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def load_senegal_regions(self):
        """Charge les regions du Senegal"""
        # Chercher le fichier
        paths = [
            r'C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\senegal\sen_admin1.shp',
            r'C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\senegal\sen_admin1.geojson',
            r'C:\Users\User\Downloads\sen_admin_boundaries_shp\sen_admin1.shp'
        ]
        
        for path in paths:
            if os.path.exists(path):
                self.load_data(path)
                return
        
        QMessageBox.warning(self, "Erreur", "Fichier des regions non trouve")
    
    def load_default_regions(self):
        """Charge automatiquement les regions au demarrage"""
        self.load_senegal_regions()
    
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
        """Affiche les informations"""
        info = "=== INFORMATIONS ===\n\n"
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val and str(val) != 'nan':
                    info += f"{col}: {val}\n"
        self.info_text.setText(info)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if filename.endswith(('.shp', '.geojson', '.json')):
                self.load_data(filename)


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
    print("JOMAN - Carte du Senegal")
    print("Support: Shapefile (.shp) et GeoJSON (.geojson)")
    print("Glissez-deposez vos fichiers directement")
    print("=" * 60)
    
    sys.exit(app.exec())
