# -*- coding: utf-8 -*-
"""
JOMAN - SIG UNIVERSEL
Version stable
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
print("JOMAN - SIG UNIVERSEL")
print("Tous pays, tous formats")
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
        name_patterns = ['name', 'NAME', 'NOM', 'nom', 'adm1_name', 'admin_name', 
                        'region', 'REGION', 'province', 'state', 'county', 'city', 'label']
        for col in name_patterns:
            if col in gdf.columns:
                try:
                    if gdf[col].iloc[0] and str(gdf[col].iloc[0]) not in ['nan', 'None']:
                        return col
                except:
                    pass
        for col in gdf.columns:
            if col != 'geometry':
                return col
        return None
    
    def display_data(self, gdf, filename):
        self.current_gdf = gdf
        self.current_name = filename
        self.ax.clear()
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        geom_type = gdf.geometry.type.iloc[0]
        
        if 'Polygon' in geom_type:
            gdf.plot(ax=self.ax, color='#4ECDC4', edgecolor='white', linewidth=0.8, alpha=0.7)
        elif 'Line' in geom_type:
            gdf.plot(ax=self.ax, color='#FFB347', linewidth=1.5, alpha=0.8)
        else:
            gdf.plot(ax=self.ax, color='#FF6B6B', markersize=30, marker='o', alpha=0.8)
        
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
                            self.ax.text(x, y, label_text, fontsize=9, color='#FFE66D',
                                       fontweight='bold', ha='center', va='center',
                                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a2a3a', alpha=0.8))
                except:
                    pass
        
        bounds = gdf.total_bounds
        margin_x = (bounds[2] - bounds[0]) * 0.05
        margin_y = (bounds[3] - bounds[1]) * 0.05
        self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
        self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
        
        self.add_scale_bar()
        self.ax.set_title(f"JOMAN - {filename} ({len(gdf)} entites)", color='white', fontsize=12)
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def add_scale_bar(self):
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
        self.statusBar().showMessage("JOMAN pret - Glissez-de posez un fichier")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("JOMAN")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        self.btn_load = QPushButton("Charger un fichier")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 12px; background-color: #4ECDC4; color: #1a2a3a; font-weight: bold;")
        left_layout.addWidget(self.btn_load)
        
        self.btn_clear = QPushButton("Effacer")
        self.btn_clear.clicked.connect(self.clear_data)
        self.btn_clear.setStyleSheet("padding: 8px; background-color: #FF6B6B;")
        left_layout.addWidget(self.btn_clear)
        
        left_layout.addWidget(QLabel(""))
        left_layout.addWidget(QLabel("Liste des entites:"))
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item_click)
        left_layout.addWidget(self.item_list)
        
        # Barre de recherche
        search_frame = QFrame()
        search_frame.setStyleSheet("border: 1px solid #4ECDC4; border-radius: 5px;")
        search_layout = QHBoxLayout(search_frame)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.search_features)
        search_layout.addWidget(self.search_input)
        left_layout.addWidget(search_frame)
        
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(100)
        self.search_results.itemClicked.connect(self.on_search_click)
        left_layout.addWidget(self.search_results)
        
        self.info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        self.stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QLabel()
        stats_layout.addWidget(self.stats_text)
        left_layout.addWidget(self.stats_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
    
    def load_file(self):
        formats = "Tous fichiers (*.shp *.geojson *.json *.kml *.kmz);;Shapefile (*.shp);;GeoJSON (*.geojson)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger", "", formats)
        if filename:
            self.load_any_file(filename)
    
    def load_any_file(self, filename):
        try:
            gdf = gpd.read_file(filename)
            name = os.path.basename(filename)
            self.map_canvas.display_data(gdf, name)
            
            self.item_list.clear()
            name_col = self.map_canvas.find_name_column(gdf)
            for idx, row in gdf.iterrows():
                display = str(row[name_col])[:40] if name_col and row[name_col] else f"Entite {idx}"
                self.item_list.addItem(display)
                self.item_list.item(idx).setData(Qt.UserRole, idx)
            
            geom_type = gdf.geometry.type.iloc[0]
            stats = f"Entites: {len(gdf)}\nType: {geom_type}"
            if 'Polygon' in geom_type:
                area = gdf.geometry.area.sum() * 111 * 111
                stats += f"\nSurface: {area:,.0f} km2"
            self.stats_text.setText(stats)
            self.statusBar().showMessage(f"Charge: {name}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def clear_data(self):
        self.map_canvas.current_gdf = None
        self.map_canvas.ax.clear()
        self.map_canvas.ax.set_facecolor('#1a2a3a')
        self.map_canvas.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        self.map_canvas.ax.text(0.5, 0.5, "JOMAN\nGlissez-de posez un fichier", 
                               transform=self.map_canvas.ax.transAxes, ha='center', va='center',
                               color='white', fontsize=14)
        self.map_canvas.canvas.draw()
        self.item_list.clear()
        self.search_results.clear()
        self.search_input.clear()
        self.info_text.clear()
        self.stats_text.clear()
        self.statusBar().showMessage("Donnees effacees")
    
    def on_item_click(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None and self.map_canvas.current_gdf is not None:
            geom = self.map_canvas.current_gdf.iloc[idx].geometry
            bounds = geom.bounds
            margin_x = (bounds[2] - bounds[0]) * 0.1
            margin_y = (bounds[3] - bounds[1]) * 0.1
            self.map_canvas.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.map_canvas.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.map_canvas.canvas.draw()
            self.statusBar().showMessage(f"Zoom: {item.text()}")
    
    def show_info(self, idx, row):
        info = "=== INFORMATIONS ===\n\n"
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val and str(val) not in ['nan', 'None']:
                    info += f"{col}: {val}\n"
        self.info_text.setText(info)
    
    def search_features(self, text):
        if not text or self.map_canvas.current_gdf is None:
            self.search_results.clear()
            return
        text = text.lower()
        self.search_results.clear()
        gdf = self.map_canvas.current_gdf
        name_col = self.map_canvas.find_name_column(gdf)
        for idx, row in gdf.iterrows():
            for col in gdf.columns:
                if col != 'geometry' and text in str(row[col]).lower():
                    display = str(row[name_col]) if name_col and row[name_col] else f"Entite {idx}"
                    self.search_results.addItem(display)
                    self.search_results.item(self.search_results.count()-1).setData(Qt.UserRole, idx)
                    break
    
    def on_search_click(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None and self.map_canvas.current_gdf is not None:
            geom = self.map_canvas.current_gdf.iloc[idx].geometry
            bounds = geom.bounds
            margin_x = (bounds[2] - bounds[0]) * 0.2
            margin_y = (bounds[3] - bounds[1]) * 0.2
            self.map_canvas.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.map_canvas.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.map_canvas.canvas.draw()
            self.statusBar().showMessage(f"Recherche: {item.text()}")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
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
    print("JOMAN - Pret !")
    print("Glissez-de posez vos fichiers")
    print("Formats: SHP, GeoJSON, KML")
    print("=" * 60)
    sys.exit(app.exec())





