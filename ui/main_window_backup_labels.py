# -*- coding: utf-8 -*-
"""
================================================================================
🏆 JOMAN - LOGICIEL DE CARTOGRAPHIE PROFESSIONNEL
================================================================================
Version: 1.0.0
"""

import sys
import os
import math
import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from shapely.geometry import Point, Polygon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=== JOMAN - DEMARRAGE ===")

class JomanCanvas(QWidget):
    """Canvas cartographique JOMAN"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        self.current_gdf = None
        self.current_name = None
        self.selected_index = None
        self.measure_points = []
        self.measure_mode = False
        self.area_mode = False
        self.hover_index = None
        
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
    
    def on_mouse_move(self, event):
        """Affiche les infos au survol"""
        if event.inaxes != self.ax or self.current_gdf is None:
            return
        
        x, y = event.xdata, event.ydata
        point = Point(x, y)
        
        for idx, row in self.current_gdf.iterrows():
            if row.geometry and row.geometry.contains(point):
                if self.hover_index != idx:
                    self.hover_index = idx
                    name_col = None
                    for nc in ['name', 'NAME', 'NOM', 'label']:
                        if nc in self.current_gdf.columns:
                            name_col = nc
                            break
                    if name_col:
                        self.parent().statusBar().showMessage(f"JOMAN - Survol: {row[name_col]}")
                return
        
        if self.hover_index is not None:
            self.hover_index = None
            self.parent().statusBar().showMessage("JOMAN pret")
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        
        x, y = event.xdata, event.ydata
        
        if self.area_mode:
            self.measure_points.append((x, y))
            if len(self.measure_points) >= 3:
                self.draw_area()
            else:
                self.draw_map()
            return
        
        if self.measure_mode:
            self.measure_points.append((x, y))
            self.draw_measure()
            return
        
        if self.current_gdf is not None:
            point = Point(x, y)
            for idx, row in self.current_gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    self.selected_index = idx
                    self.draw_map()
                    self.parent().show_attributes(idx, row)
                    return
            self.selected_index = None
            self.draw_map()
            self.parent().clear_attributes()
    
    def draw_map(self):
        """Dessine la carte JOMAN"""
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            geom_type = self.current_gdf.geometry.type.iloc[0]
            if 'Point' in geom_type:
                color = '#FF6B6B'
            elif 'Line' in geom_type:
                color = '#FFB347'
            else:
                color = '#4ECDC4'
            
            self.current_gdf.plot(ax=self.ax, color=color, edgecolor='white', 
                                  linewidth=0.5, alpha=0.7)
            
            if self.selected_index is not None:
                selected = self.current_gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color='#FFE66D', edgecolor='#FFAA33',
                             linewidth=2, alpha=0.9)
            
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            self.ax.set_title(f"JOMAN - {self.current_name} ({len(self.current_gdf)} entites)", color='white')
        else:
            self.ax.text(0.5, 0.5, "JOMAN\nCliquez sur 'Ajouter'", 
                        transform=self.ax.transAxes, ha='center', va='center',
                        color='white', fontsize=14)
        
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def draw_measure(self):
        """Dessine les mesures de distance"""
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FF6B6B', linewidth=2, alpha=0.8)
            self.ax.plot(x, y, 'o', color='#FF6B6B', markersize=5)
            
            total = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
                total += dist
            
            x_last, y_last = self.measure_points[-1]
            self.ax.text(x_last, y_last, f"{total:.2f} km", 
                        fontsize=9, color='white',
                        bbox=dict(boxstyle="round,pad=0.3",
                                 facecolor='#FF6B6B', alpha=0.8))
            self.canvas.draw()
    
    def draw_area(self):
        """Dessine la surface mesuree"""
        self.draw_map()
        
        if len(self.measure_points) >= 3:
            from matplotlib.patches import Polygon as MplPolygon
            polygon = Polygon(self.measure_points)
            
            patch = MplPolygon(self.measure_points, facecolor='#4ECDC4', 
                               alpha=0.3, edgecolor='#FF6B6B', linewidth=2)
            self.ax.add_patch(patch)
            
            area_km2 = polygon.area * 111 * 111
            
            centroid = polygon.centroid
            self.ax.text(centroid.x, centroid.y, f"{area_km2:.2f} km²",
                        fontsize=10, color='white',
                        bbox=dict(boxstyle="round,pad=0.3",
                                 facecolor='#4ECDC4', alpha=0.8))
            self.canvas.draw()
    
    def clear_measure(self):
        self.measure_points = []
        self.draw_map()
    
    def toggle_measure_mode(self):
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.clear_measure()
        return self.measure_mode
    
    def toggle_area_mode(self):
        self.area_mode = not self.area_mode
        if self.area_mode:
            self.measure_points = []
            self.measure_mode = False
        return self.area_mode


class JomanMainWindow(QMainWindow):
    """Fenetre principale JOMAN"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏆 JOMAN - Logiciel de Cartographie v1.0")
        self.setGeometry(100, 100, 1400, 850)
        self.setAcceptDrops(True)
        
        self.current_gdf = None
        self.current_name = None
        self.dark_theme = True
        
        self.setup_ui()
        self.setup_menu()
        self.statusBar().showMessage("JOMAN pret - Chargez un fichier")
        print("JOMAN - Fenetre initialisee")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # ===== PANNEAU GAUCHE =====
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        logo = QLabel("🏆 JOMAN")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo)
        
        self.btn_load = QPushButton("Ajouter un fichier")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4ECDC4; color: #1a1a2a; font-weight: bold;")
        left_layout.addWidget(self.btn_load)
        
        self.btn_measure = QPushButton("Mode distance (OFF)")
        self.btn_measure.clicked.connect(self.toggle_measure)
        self.btn_measure.setStyleSheet("padding: 8px;")
        left_layout.addWidget(self.btn_measure)
        
        self.btn_area = QPushButton("Mode surface (OFF)")
        self.btn_area.clicked.connect(self.toggle_area)
        self.btn_area.setStyleSheet("padding: 8px;")
        left_layout.addWidget(self.btn_area)
        
        self.btn_export = QPushButton("Exporter la carte")
        self.btn_export.clicked.connect(self.export_map)
        left_layout.addWidget(self.btn_export)
        
        left_layout.addWidget(QLabel(""))
        
        left_layout.addWidget(QLabel("Couches JOMAN:"))
        self.layer_list = QListWidget()
        self.layer_list.itemClicked.connect(self.on_layer_click)
        left_layout.addWidget(self.layer_list)
        
        # Recherche
        search_group = QGroupBox("Recherche JOMAN")
        search_layout = QVBoxLayout(search_group)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher...")
        self.search_edit.textChanged.connect(self.search_features)
        search_layout.addWidget(self.search_edit)
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(self.zoom_to_feature)
        search_layout.addWidget(self.search_results)
        left_layout.addWidget(search_group)
        
        # Attributs
        self.attr_group = QGroupBox("Attributs selectionnes")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setMaximumHeight(150)
        self.attr_text.setStyleSheet("background-color: #16213e; color: #FFE66D; font-family: 'Courier New';")
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        # Infos
        self.info_group = QGroupBox("Info JOMAN")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        # Statistiques
        self.stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        self.stats_text.setStyleSheet("background-color: #16213e; color: #4ECDC4; font-size: 10px;")
        stats_layout.addWidget(self.stats_text)
        left_layout.addWidget(self.stats_group)
        
        # Legende
        legend_group = QGroupBox("Legende")
        legend_layout = QVBoxLayout(legend_group)
        legend_layout.addWidget(QLabel("Polygones"))
        legend_layout.addWidget(QLabel("Lignes"))
        legend_layout.addWidget(QLabel("Points"))
        legend_layout.addWidget(QLabel("Selectionne"))
        legend_layout.addWidget(QLabel("Mesure"))
        left_layout.addWidget(legend_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # ===== ZONE CENTRALE =====
        self.map_canvas = JomanCanvas(self)
        layout.addWidget(self.map_canvas, 1)
        
        # ===== PANNEAU DROIT (ZOOM) =====
        right_panel = QWidget()
        right_panel.setMaximumWidth(80)
        right_layout = QVBoxLayout(right_panel)
        
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QVBoxLayout(zoom_group)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setStyleSheet("font-size: 20px; padding: 10px;")
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setRange(0, 100)
        self.zoom_slider.setValue(50)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setStyleSheet("font-size: 20px; padding: 10px;")
        zoom_layout.addWidget(self.zoom_out_btn)
        
        right_layout.addWidget(zoom_group)
        right_layout.addStretch()
        
        layout.addWidget(right_panel)
    
    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("JOMAN")
        file_menu.addAction("Ajouter", self.load_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("Exporter carte", self.export_map, "Ctrl+E")
        file_menu.addAction("Exporter CSV", self.export_attributes)
        file_menu.addSeparator()
        file_menu.addAction("Quitter", self.close, "Ctrl+Q")
        
        view_menu = menubar.addMenu("Affichage")
        view_menu.addAction("Zoom avant", self.zoom_in, "Ctrl++")
        view_menu.addAction("Zoom arriere", self.zoom_out, "Ctrl+-")
        view_menu.addAction("Vue totale", self.zoom_all, "Ctrl+0")
        view_menu.addSeparator()
        view_menu.addAction("Mode nuit/jour", self.toggle_theme)
    
    def load_file(self):
        formats = "Fichiers (*.shp *.geojson *.json *.kml *.kmz)"
        filename, _ = QFileDialog.getOpenFileName(self, "JOMAN - Charger", "", formats)
        
        if filename:
            try:
                gdf = gpd.read_file(filename)
                name = os.path.basename(filename)
                
                self.current_gdf = gdf
                self.current_name = name
                
                self.map_canvas.current_gdf = gdf
                self.map_canvas.current_name = name
                self.map_canvas.selected_index = None
                self.map_canvas.draw_map()
                
                self.layer_list.clear()
                self.layer_list.addItem(f"{name} ({len(gdf)} entites)")
                
                geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Inconnu"
                info = f"Fichier: {name}\nType: {geom_type}\nEntites: {len(gdf)}\nColonnes: {len(gdf.columns)-1}"
                self.info_text.setText(info)
                
                self.update_stats()
                self.statusBar().showMessage(f"JOMAN - {name} charge")
                
            except Exception as e:
                QMessageBox.warning(self, "Erreur JOMAN", str(e))
    
    def update_stats(self):
        if self.current_gdf is None:
            return
        
        gdf = self.current_gdf
        stats = f"Entites: {len(gdf)}\nColonnes: {len(gdf.columns)-1}\n"
        
        geom_types = gdf.geometry.type.value_counts()
        for gtype, count in geom_types.items():
            stats += f"{gtype}: {count}\n"
        
        if 'Polygon' in str(geom_types.index):
            try:
                total_area = gdf.geometry.area.sum() * 111 * 111
                stats += f"Surface: {total_area:,.0f} km²"
            except:
                pass
        
        self.stats_text.setText(stats)
    
    def show_attributes(self, idx, row):
        text = f"Entite {idx}\n" + "=" * 30 + "\n"
        for col in row.index:
            if col != 'geometry':
                text += f"> {col}: {row[col]}\n"
        self.attr_text.setText(text)
    
    def clear_attributes(self):
        self.attr_text.clear()
    
    def toggle_measure(self):
        mode = self.map_canvas.toggle_measure_mode()
        if mode:
            self.btn_measure.setText("Mode distance (ON)")
            self.btn_measure.setStyleSheet("padding: 8px; background-color: #FF6B6B;")
            self.statusBar().showMessage("Mode distance actif")
        else:
            self.btn_measure.setText("Mode distance (OFF)")
            self.btn_measure.setStyleSheet("padding: 8px;")
            self.statusBar().showMessage("Mode distance desactive")
    
    def toggle_area(self):
        mode = self.map_canvas.toggle_area_mode()
        if mode:
            self.btn_area.setText("Mode surface (ON)")
            self.btn_area.setStyleSheet("padding: 8px; background-color: #4ECDC4; color: #1a1a2a;")
            self.statusBar().showMessage("Mode surface actif - Cliquez 3 points")
        else:
            self.btn_area.setText("Mode surface (OFF)")
            self.btn_area.setStyleSheet("padding: 8px;")
            self.statusBar().showMessage("Mode surface desactive")
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter", "", "PNG (*.png)")
        if filename:
            self.map_canvas.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.statusBar().showMessage(f"Carte exportee")
    
    def export_attributes(self):
        if self.current_gdf is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter CSV", "", "CSV (*.csv)")
        if filename:
            df = pd.DataFrame(self.current_gdf.drop(columns='geometry'))
            df.to_csv(filename, index=False, encoding='utf-8')
            self.statusBar().showMessage(f"CSV exporte")
    
    def search_features(self):
        if self.current_gdf is None:
            return
        
        search_text = self.search_edit.text().lower()
        if not search_text:
            self.search_results.clear()
            return
        
        self.search_results.clear()
        name_col = 'name' if 'name' in self.current_gdf.columns else None
        
        for idx, row in self.current_gdf.iterrows():
            for col in self.current_gdf.columns:
                if col != 'geometry' and search_text in str(row[col]).lower():
                    display = str(row[name_col]) if name_col else f"Entite {idx}"
                    self.search_results.addItem(display)
                    self.search_results.item(self.search_results.count()-1).setData(Qt.UserRole, idx)
                    break
    
    def zoom_to_feature(self, item):
        if self.current_gdf is None:
            return
        idx = item.data(Qt.UserRole)
        if idx is not None:
            geom = self.current_gdf.iloc[idx].geometry
            bounds = geom.bounds
            margin_x = (bounds[2] - bounds[0]) * 0.2
            margin_y = (bounds[3] - bounds[1]) * 0.2
            self.map_canvas.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.map_canvas.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.map_canvas.canvas.draw()
            self.map_canvas.selected_index = idx
            self.map_canvas.draw_map()
            self.show_attributes(idx, self.current_gdf.iloc[idx])
    
    def zoom_in(self):
        xlim = self.map_canvas.ax.get_xlim()
        ylim = self.map_canvas.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        width = (xlim[1] - xlim[0]) / 2
        height = (ylim[1] - ylim[0]) / 2
        self.map_canvas.ax.set_xlim(cx - width/2, cx + width/2)
        self.map_canvas.ax.set_ylim(cy - height/2, cy + height/2)
        self.map_canvas.canvas.draw()
    
    def zoom_out(self):
        xlim = self.map_canvas.ax.get_xlim()
        ylim = self.map_canvas.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        width = (xlim[1] - xlim[0]) * 1.5
        height = (ylim[1] - ylim[0]) * 1.5
        self.map_canvas.ax.set_xlim(cx - width/2, cx + width/2)
        self.map_canvas.ax.set_ylim(cy - height/2, cy + height/2)
        self.map_canvas.canvas.draw()
    
    def on_zoom_slider(self, value):
        if self.current_gdf is not None:
            bounds = self.current_gdf.total_bounds
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2
            width = (bounds[2] - bounds[0]) * (1 - value / 100)
            height = (bounds[3] - bounds[1]) * (1 - value / 100)
            self.map_canvas.ax.set_xlim(center_x - width/2, center_x + width/2)
            self.map_canvas.ax.set_ylim(center_y - height/2, center_y + height/2)
            self.map_canvas.canvas.draw()
    
    def zoom_all(self):
        if self.current_gdf is not None:
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.map_canvas.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.map_canvas.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.map_canvas.canvas.draw()
    
    def on_layer_click(self, item):
        pass
    
    def toggle_theme(self):
        if self.dark_theme:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            self.setPalette(palette)
            self.dark_theme = False
            self.statusBar().showMessage("Theme clair")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(18, 18, 18))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.Text, Qt.white)
            self.setPalette(palette)
            self.dark_theme = True
            self.statusBar().showMessage("Theme sombre")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    app.setPalette(palette)
    
    window = JomanMainWindow()
    window.show()
    
    print("=" * 50)
    print("🏆 JOMAN - Logiciel de Cartographie")
    print("Version 1.0.0")
    print("Pret !")
    print("=" * 50)
    
    sys.exit(app.exec())