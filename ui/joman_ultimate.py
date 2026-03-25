# -*- coding: utf-8 -*-
"""
JOMAN - LEAD ULTIMATE EDITION
Interface complete avec toutes les fonctionnalités
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
from shapely.geometry import Point, Polygon
from matplotlib.patches import Polygon as MplPolygon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=" * 60)
print("JOMAN - LEAD ULTIMATE EDITION")
print("Toutes les fonctionnalités")
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
        self.measure_mode = None
        self.measure_points = []
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        
        if self.measure_mode == "distance":
            self.measure_points.append((event.xdata, event.ydata))
            if len(self.measure_points) >= 2:
                self.draw_distance_measure()
        elif self.measure_mode == "area":
            self.measure_points.append((event.xdata, event.ydata))
            if len(self.measure_points) >= 3:
                self.draw_area_measure()
        else:
            point = Point(event.xdata, event.ydata)
            if self.current_gdf is not None:
                for idx, row in self.current_gdf.iterrows():
                    if row.geometry and row.geometry.contains(point):
                        self.main_window.show_info(idx, row)
                        break
    
    def find_name_column(self, gdf):
        name_patterns = ['name', 'NAME', 'NOM', 'adm1_name', 'admin_name', 
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
    
    def draw_distance_measure(self):
        if len(self.measure_points) >= 2:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FFB347', linewidth=2, alpha=0.8)
            self.ax.plot(x, y, 'o', color='#FFB347', markersize=6)
            
            total = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
                total += dist
            
            x_last, y_last = self.measure_points[-1]
            self.ax.text(x_last, y_last, f"{total:.2f} km", fontsize=9, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFB347', alpha=0.8))
            self.canvas.draw()
    
    def draw_area_measure(self):
        if len(self.measure_points) >= 3:
            polygon = Polygon(self.measure_points)
            patch = MplPolygon(self.measure_points, facecolor='#4ECDC4', 
                               alpha=0.3, edgecolor='#FFB347', linewidth=2)
            self.ax.add_patch(patch)
            area_km2 = polygon.area * 111 * 111
            centroid = polygon.centroid
            self.ax.text(centroid.x, centroid.y, f"{area_km2:.2f} km2", 
                        fontsize=9, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#4ECDC4', alpha=0.8))
            self.canvas.draw()
    
    def display_data(self, gdf, filename):
        self.current_gdf = gdf
        self.current_name = filename
        self.draw_map()
    
    def draw_map(self):
        self.ax.clear()
        self.ax.set_facecolor('#1a2a3a')
        self.ax.grid(True, alpha=0.3, linestyle='--', color='#88aacc')
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            geom_type = self.current_gdf.geometry.type.iloc[0]
            if 'Polygon' in geom_type:
                self.current_gdf.plot(ax=self.ax, color='#4ECDC4', edgecolor='white', linewidth=0.8, alpha=0.7)
            elif 'Line' in geom_type:
                self.current_gdf.plot(ax=self.ax, color='#FFB347', linewidth=1.5, alpha=0.8)
            else:
                self.current_gdf.plot(ax=self.ax, color='#FF6B6B', markersize=30, marker='o', alpha=0.8)
            
            name_col = self.find_name_column(self.current_gdf)
            if name_col:
                for idx, row in self.current_gdf.iterrows():
                    try:
                        if row.geometry and not row.geometry.is_empty:
                            centroid = row.geometry.centroid
                            label = str(row[name_col])[:30]
                            if label and label not in ['nan', 'None']:
                                self.ax.text(centroid.x, centroid.y, label, fontsize=9, color='#FFE66D',
                                           fontweight='bold', ha='center', va='center',
                                           bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a2a3a', alpha=0.8))
                    except:
                        pass
            
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            self.add_scale_bar()
            self.ax.set_title(f"JOMAN - {self.current_name} ({len(self.current_gdf)} entites)", color='white')
        else:
            self.ax.text(0.5, 0.5, "JOMAN\nGlissez-de posez un fichier", 
                        transform=self.ax.transAxes, ha='center', va='center',
                        color='white', fontsize=14)
        
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
    
    def clear_measure(self):
        self.measure_points = []
        self.measure_mode = None
        self.draw_map()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JOMAN - LEAD ULTIMATE EDITION")
        self.setGeometry(100, 100, 1400, 900)
        self.setAcceptDrops(True)
        self.dark_theme = True
        
        self.setup_ui()
        self.statusBar().showMessage("JOMAN pret - Glissez-de posez un fichier")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # ========== PANNAU GAUCHE ==========
        left_panel = QWidget()
        left_panel.setMaximumWidth(380)
        left_panel.setMinimumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        
        # Titre
        title = QLabel("🏆 JOMAN")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # --- SECTION FICHIER ---
        file_group = QGroupBox("📁 Fichier")
        file_layout = QVBoxLayout(file_group)
        
        self.btn_load = QPushButton("📂 Charger un fichier")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 10px; background-color: #4ECDC4; color: #1a2a3a; font-weight: bold; font-size: 12px;")
        file_layout.addWidget(self.btn_load)
        
        self.btn_export = QPushButton("💾 Exporter PNG")
        self.btn_export.clicked.connect(self.export_map)
        self.btn_export.setStyleSheet("padding: 8px; background-color: #4ECDC4;")
        file_layout.addWidget(self.btn_export)
        
        left_layout.addWidget(file_group)
        
        # --- SECTION MESURE ---
        measure_group = QGroupBox("📏 Mesure")
        measure_layout = QVBoxLayout(measure_group)
        
        self.btn_dist = QPushButton("📐 Mesurer distance")
        self.btn_dist.clicked.connect(self.activate_distance)
        self.btn_dist.setStyleSheet("padding: 8px; background-color: #FFB347; font-weight: bold;")
        measure_layout.addWidget(self.btn_dist)
        
        self.btn_area = QPushButton("📏 Mesurer surface")
        self.btn_area.clicked.connect(self.activate_area)
        self.btn_area.setStyleSheet("padding: 8px; background-color: #FFB347; font-weight: bold;")
        measure_layout.addWidget(self.btn_area)
        
        self.btn_clear_meas = QPushButton("🗑️ Effacer mesure")
        self.btn_clear_meas.clicked.connect(self.clear_measure)
        self.btn_clear_meas.setStyleSheet("padding: 8px; background-color: #FF6B6B;")
        measure_layout.addWidget(self.btn_clear_meas)
        
        left_layout.addWidget(measure_group)
        
        # --- SECTION AFFICHAGE ---
        view_group = QGroupBox("🎨 Affichage")
        view_layout = QVBoxLayout(view_group)
        
        self.btn_theme = QPushButton("🌓 Mode nuit/jour")
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_theme.setStyleSheet("padding: 8px; background-color: #4ECDC4;")
        view_layout.addWidget(self.btn_theme)
        
        self.btn_clear = QPushButton("🗑️ Effacer tout")
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear.setStyleSheet("padding: 8px; background-color: #FF6B6B;")
        view_layout.addWidget(self.btn_clear)
        
        left_layout.addWidget(view_group)
        
        # --- SECTION RECHERCHE ---
        search_group = QGroupBox("🔍 Recherche")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un nom...")
        self.search_input.textChanged.connect(self.search_features)
        self.search_input.setStyleSheet("padding: 8px;")
        search_layout.addWidget(self.search_input)
        
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(100)
        self.search_results.itemClicked.connect(self.on_search_click)
        search_layout.addWidget(self.search_results)
        
        left_layout.addWidget(search_group)
        
        # --- SECTION LISTE ---
        list_group = QGroupBox("📋 Liste des entites")
        list_layout = QVBoxLayout(list_group)
        
        self.item_list = QListWidget()
        self.item_list.itemClicked.connect(self.on_item_click)
        list_layout.addWidget(self.item_list)
        
        left_layout.addWidget(list_group)
        
        # --- SECTION INFOS ---
        info_group = QGroupBox("ℹ️ Informations")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("background-color: #1a2a3a; color: #FFE66D; font-size: 11px;")
        info_layout.addWidget(self.info_text)
        
        left_layout.addWidget(info_group)
        
        # --- SECTION STATS ---
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QLabel()
        self.stats_text.setStyleSheet("color: #4ECDC4; font-size: 11px;")
        stats_layout.addWidget(self.stats_text)
        
        left_layout.addWidget(stats_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # ========== CANVAS CENTRAL ==========
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
    
    # ========== FONCTIONS ==========
    
    def load_file(self):
        formats = "Fichiers (*.shp *.geojson *.json *.kml *.kmz);;Shapefile (*.shp);;GeoJSON (*.geojson)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", formats)
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
            stats = f"📌 Entites: {len(gdf)}\n📐 Type: {geom_type}"
            if 'Polygon' in geom_type:
                area = gdf.geometry.area.sum() * 111 * 111
                stats += f"\n🌍 Surface: {area:,.0f} km2"
            self.stats_text.setText(stats)
            self.statusBar().showMessage(f"✅ Charge: {name}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def export_map(self):
        if self.map_canvas.current_gdf is None:
            QMessageBox.warning(self, "Erreur", "Aucune donnee a exporter")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter la carte", "", "PNG (*.png)")
        if filename:
            self.map_canvas.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#1a2a3a')
            self.statusBar().showMessage(f"💾 Carte exportee: {os.path.basename(filename)}")
    
    def activate_distance(self):
        self.map_canvas.measure_mode = "distance"
        self.map_canvas.measure_points = []
        self.statusBar().showMessage("📏 Mode distance - Cliquez 2 points sur la carte")
        self.btn_dist.setStyleSheet("padding: 8px; background-color: #FF8C00; font-weight: bold;")
        self.btn_area.setStyleSheet("padding: 8px; background-color: #FFB347;")
    
    def activate_area(self):
        self.map_canvas.measure_mode = "area"
        self.map_canvas.measure_points = []
        self.statusBar().showMessage("📐 Mode surface - Cliquez 3 points sur la carte")
        self.btn_area.setStyleSheet("padding: 8px; background-color: #FF8C00; font-weight: bold;")
        self.btn_dist.setStyleSheet("padding: 8px; background-color: #FFB347;")
    
    def clear_measure(self):
        self.map_canvas.clear_measure()
        self.map_canvas.measure_mode = None
        self.btn_dist.setStyleSheet("padding: 8px; background-color: #FFB347;")
        self.btn_area.setStyleSheet("padding: 8px; background-color: #FFB347;")
        self.statusBar().showMessage("🗑️ Mesures effacees")
    
    def clear_all(self):
        self.map_canvas.current_gdf = None
        self.map_canvas.clear_measure()
        self.map_canvas.draw_map()
        self.item_list.clear()
        self.search_results.clear()
        self.search_input.clear()
        self.info_text.clear()
        self.stats_text.clear()
        self.statusBar().showMessage("🗑️ Tout efface")
    
    def toggle_theme(self):
        if self.dark_theme:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            self.setPalette(palette)
            self.dark_theme = False
            self.statusBar().showMessage("🌞 Theme clair")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(26, 42, 58))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(26, 42, 58))
            palette.setColor(QPalette.Text, Qt.white)
            self.setPalette(palette)
            self.dark_theme = True
            self.statusBar().showMessage("🌙 Theme sombre")
    
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
            self.statusBar().showMessage(f"🔍 Zoom: {item.text()}")
    
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
            self.statusBar().showMessage(f"🎯 Zoom: {item.text()}")
    
    def show_info(self, idx, row):
        info = "═" * 30 + "\n"
        info += "📋 INFORMATIONS\n"
        info += "═" * 30 + "\n\n"
        for col in row.index:
            if col != 'geometry':
                val = row[col]
                if val and str(val) not in ['nan', 'None']:
                    info += f"📌 {col}: {val}\n"
        self.info_text.setText(info)
        self.statusBar().showMessage(f"📍 Entite {idx} selectionnee")
    
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
    print("🏆 JOMAN - LEAD ULTIMATE EDITION")
    print("=" * 60)
    print("✅ Interface complete")
    print("✅ Mesure distance et surface")
    print("✅ Export PNG")
    print("✅ Mode nuit/jour")
    print("✅ Recherche textuelle")
    print("✅ Glisser-deposer")
    print("=" * 60)
    
    sys.exit(app.exec())
