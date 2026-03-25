# -*- coding: utf-8 -*-
"""
JOMAN - AFFICHAGE DES REGIONS DU SENEGAL
Version simplifiee et fonctionnelle
"""

import sys
import os
import math
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
print("JOMAN - REGIONS DU SENEGAL")
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
                self.main_window.show_region_info(idx, row)
                break
    
    def display_regions(self, gdf, name):
        """Affiche les regions"""
        self.current_gdf = gdf
        self.current_name = name
        self.ax.clear()
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        # Dessiner les regions
        gdf.plot(ax=self.ax, color='#4ECDC4', edgecolor='white', linewidth=1, alpha=0.7)
        
        # Ajouter les noms des regions
        for idx, row in gdf.iterrows():
            try:
                centroid = row.geometry.centroid
                region_name = row['adm1_name']
                self.ax.text(centroid.x, centroid.y, region_name,
                           fontsize=10, color='#FFE66D', fontweight='bold',
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
        
        self.ax.set_title(f"REGIONS DU SENEGAL - {len(gdf)} regions", color='white', fontsize=14)
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
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
        else:
            scale_len, text = 20, "20 km"
            
        scale_deg = scale_len / 111
        x_end = x + scale_deg
        
        self.ax.plot([x, x_end], [y, y], 'white', linewidth=2)
        self.ax.text(x + scale_deg/2, y - y*0.003, text, ha='center', fontsize=8, color='white')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JOMAN - Regions du Senegal")
        self.setGeometry(100, 100, 1300, 800)
        
        self.setup_ui()
        self.statusBar().showMessage("JOMAN pret - Charger les regions")
        
        # Charger automatiquement les regions
        self.load_regions()
    
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
        
        # Bouton charger
        self.btn_load = QPushButton("📂 Charger les regions")
        self.btn_load.clicked.connect(self.load_regions)
        self.btn_load.setStyleSheet("padding: 12px; font-size: 14px; background-color: #4ECDC4; color: #1a2a3a; font-weight: bold;")
        left_layout.addWidget(self.btn_load)
        
        left_layout.addWidget(QLabel(""))
        
        # Liste des regions
        left_layout.addWidget(QLabel("📋 LISTE DES REGIONS:"))
        self.region_list = QListWidget()
        self.region_list.itemClicked.connect(self.on_region_click)
        left_layout.addWidget(self.region_list)
        
        # Informations
        self.info_group = QGroupBox("ℹ️ INFORMATION")
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
        
        # Legende
        legend_group = QGroupBox("📖 LEGENDE")
        legend_layout = QVBoxLayout(legend_group)
        legend_layout.addWidget(QLabel("🟦 Regions du Senegal"))
        legend_layout.addWidget(QLabel("🟨 Noms des regions"))
        legend_layout.addWidget(QLabel("📏 Barre d'echelle"))
        left_layout.addWidget(legend_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Canvas
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
    
    def load_regions(self):
        """Charge les regions du Senegal"""
        filename = r'C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\senegal\sen_admin1.shp'
        
        if not os.path.exists(filename):
            QMessageBox.warning(self, "Erreur", f"Fichier non trouve:\n{filename}")
            return
        
        try:
            gdf = gpd.read_file(filename)
            self.map_canvas.display_regions(gdf, "Regions du Senegal")
            
            # Remplir la liste des regions
            self.region_list.clear()
            for idx, row in gdf.iterrows():
                self.region_list.addItem(row['adm1_name'])
                self.region_list.item(idx).setData(Qt.UserRole, idx)
            
            # Statistiques
            area_total = gdf.geometry.area.sum() * 111 * 111
            self.stats_text.setText(f"Nombre de regions: {len(gdf)}\nSurface totale: {area_total:,.0f} km²")
            
            self.statusBar().showMessage(f"✅ {len(gdf)} regions chargees")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def on_region_click(self, item):
        """Zoom sur la region selectionnee"""
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
    
    def show_region_info(self, idx, row):
        """Affiche les informations de la region"""
        info = f"=== {row['adm1_name']} ===\n\n"
        info += f"Code: {row['adm1_pcode']}\n"
        info += f"Superficie: {row['area_sqkm']:.0f} km²\n"
        info += f"Latitude: {row['center_lat']:.4f}°\n"
        info += f"Longitude: {row['center_lon']:.4f}°\n"
        self.info_text.setText(info)
        self.statusBar().showMessage(f"Region: {row['adm1_name']}")


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
    print("JOMAN - Carte des regions du Senegal")
    print("14 regions chargees automatiquement")
    print("=" * 60)
    
    sys.exit(app.exec())
