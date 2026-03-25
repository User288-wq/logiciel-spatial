# -*- coding: utf-8 -*-
"""
JOMAN - GIS Software
Version 1.0.0
"""

import sys
import os
import math
import geopandas as gpd
import pandas as pd
import pyogrio
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from shapely.geometry import Point, Polygon

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=" * 60)
print("JOMAN - GIS Software")
print("Version 1.0.0")
print("=" * 60)

class JomanCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.figure = Figure(figsize=(10, 8), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor
                self.ax.grid(True, alpha=0.3, linestyle='--', color='#888888')('#0a1a2a')
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
        self.show_labels = True
        
        self.cid = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
    
    def get_name_column(self):
        if self.current_gdf is None:
            return None
        name_cols = ['name', 'NAME', 'NOM', 'nom', 'label', 'LABEL', 'admin', 'ADMIN', 'adm_level']
        for col in name_cols:
            if col in self.current_gdf.columns:
                val = self.current_gdf[col].iloc[0]
                if val and val != 'None' and str(val) != 'nan':
                    return col
        return None
    
    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.draw_map()
        return self.show_labels
    
    def on_mouse_move(self, event):
        if event.inaxes != self.ax or self.current_gdf is None:
            return
        x, y = event.xdata, event.ydata
        point = Point(x, y)
        for idx, row in self.current_gdf.iterrows():
            if row.geometry and row.geometry.contains(point):
                if self.hover_index != idx:
                    self.hover_index = idx
                    name_col = self.get_name_column()
                    if name_col and row[name_col]:
                        self.main_window.statusBar().showMessage(f"JOMAN - Hover: {row[name_col]}")
                return
        if self.hover_index is not None:
            self.hover_index = None
            self.main_window.statusBar().showMessage("JOMAN ready")
    
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
                    self.main_window.show_attributes(idx, row)
                    return
            self.selected_index = None
            self.draw_map()
            self.main_window.clear_attributes()
    
    def draw_map(self):
        self.ax.clear()
        self.ax.set_facecolor
                self.ax.grid(True, alpha=0.3, linestyle='--', color='#888888')('#0a1a2a')
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            geom_type = self.current_gdf.geometry.type.iloc[0]
            if 'Point' in geom_type:
                color = '#FF6B6B'
            elif 'Line' in geom_type:
                color = '#FFB347'
            else:
                color = '#4ECDC4'
            
            self.current_gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=0.8, alpha=0.7)
            
            if self.selected_index is not None:
                selected = self.current_gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color='#FFE66D', edgecolor='#FFAA33', linewidth=2, alpha=0.9)
            
            if self.show_labels:
                label_col = self.get_name_column()
                if label_col:
                    level_names = {0: 'National', 1: 'Regional', 2: 'Department', 3: 'Arrondissement'}
                    for idx, row in self.current_gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                if label_col == 'adm_level':
                                    val = row[label_col]
                                    label_text = level_names.get(val, f'Level {val}')
                                else:
                                    label_text = str(row[label_col])[:25]
                                
                                if label_text and label_text != 'nan' and label_text != 'None':
                                    if 'Point' in geom_type:
                                        x, y = row.geometry.x, row.geometry.y
                                    elif 'Line' in geom_type:
                                        line = row.geometry
                                        if line.length > 0:
                                            point = line.interpolate(line.length / 2)
                                            x, y = point.x, point.y
                                        else:
                                            continue
                                    else:
                                        centroid = row.geometry.centroid
                                        x, y = centroid.x, centroid.y
                                    
                                    if self.selected_index == idx:
                                        self.ax.text(x, y, label_text, fontsize=8, color='#FFE66D',
                                                   fontweight='bold', ha='center', va='center',
                                                   bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a2a', alpha=0.7))
                                    else:
                                        self.ax.text(x, y, label_text, fontsize=7, color='white',
                                                   ha='center', va='center',
                                                   bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a2a', alpha=0.6))
                            except:
                                pass
                else:
                    for idx, row in self.current_gdf.iterrows():
                        if row.geometry and not row.geometry.is_empty:
                            try:
                                if 'Point' in geom_type:
                                    x, y = row.geometry.x, row.geometry.y
                                elif 'Line' in geom_type:
                                    line = row.geometry
                                    if line.length > 0:
                                        point = line.interpolate(line.length / 2)
                                        x, y = point.x, point.y
                                    else:
                                        continue
                                else:
                                    centroid = row.geometry.centroid
                                    x, y = centroid.x, centroid.y
                                
                                self.ax.text(x, y, str(idx), fontsize=6, color='#888888',
                                           ha='center', va='center')
                            except:
                                pass
            
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            self.ax.set_title(f"JOMAN - {self.current_name} ({len(self.current_gdf)} features)", color='white')
        else:
            self.ax.text(0.5, 0.5, "JOMAN\nClick 'Add' to load file", transform=self.ax.transAxes, ha='center', va='center', color='white', fontsize=14)
        
        self.ax.tick_params(colors='white')
        self.canvas.draw()
    
    def draw_measure(self):
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FF6B6B', linewidth=2, alpha=0.8)
            total = 0
            for i in range(len(self.measure_points)-1):
                x1, y1 = self.measure_points[i]
                x2, y2 = self.measure_points[i+1]
                total += math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111
            x_last, y_last = self.measure_points[-1]
            self.ax.text(x_last, y_last, f"{total:.2f} km", fontsize=9, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#FF6B6B', alpha=0.8))
            self.canvas.draw()
    
    def draw_area(self):
        self.draw_map()
        if len(self.measure_points) >= 3:
            from matplotlib.patches import Polygon as MplPolygon
            polygon = Polygon(self.measure_points)
            patch = MplPolygon(self.measure_points, facecolor='#4ECDC4', alpha=0.3, edgecolor='#FF6B6B', linewidth=2)
            self.ax.add_patch(patch)
            area_km2 = polygon.area * 111 * 111
            centroid = polygon.centroid
            self.ax.text(centroid.x, centroid.y, f"{area_km2:.2f} km2", fontsize=10, color='white',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='#4ECDC4', alpha=0.8))
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JOMAN - GIS Software v1.0")
        self.setGeometry(100, 100, 1400, 850)
        self.setAcceptDrops(True)
        
        self.current_gdf = None
        self.current_name = None
        self.dark_theme = True
        
        self.setup_ui()
        self.setup_menu()
        self.statusBar().showMessage("JOMAN ready - Load a file")
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(150)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        logo = QLabel("JOMAN")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ECDC4; padding: 10px;")
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo)
        
        self.btn_load = QPushButton("Add File")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_load.setStyleSheet("padding: 10px; background-color: #4ECDC4; color: #1a1a2a;")
        left_layout.addWidget(self.btn_load)
        
        self.btn_measure = QPushButton("Distance (OFF)")
        self.btn_measure.clicked.connect(self.toggle_measure)
        left_layout.addWidget(self.btn_measure)
        
        self.btn_area = QPushButton("Area (OFF)")
        self.btn_area.clicked.connect(self.toggle_area)
        left_layout.addWidget(self.btn_area)
        
        self.btn_labels = QPushButton("Labels (ON)")
        self.btn_labels.clicked.connect(self.toggle_labels)
        self.btn_labels.setCheckable(True)
        self.btn_labels.setChecked(True)
        self.btn_labels.setStyleSheet("padding: 8px; background-color: #4ECDC4; color: #1a1a2a;")
        left_layout.addWidget(self.btn_labels)
        
        self.btn_export = QPushButton("Export Map")
        self.btn_export.clicked.connect(self.export_map)
        left_layout.addWidget(self.btn_export)
        
        left_layout.addWidget(QLabel(""))
        left_layout.addWidget(QLabel("Layers:"))
        self.layer_list = QListWidget()
        self.layer_list.itemClicked.connect(self.on_layer_click)
        left_layout.addWidget(self.layer_list)
        
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.search_features)
        search_layout.addWidget(self.search_edit)
        self.search_results = QListWidget()
        self.search_results.itemClicked.connect(self.zoom_to_feature)
        search_layout.addWidget(self.search_results)
        left_layout.addWidget(search_group)
        
        self.attr_group = QGroupBox("Attributes")
        attr_layout = QVBoxLayout(self.attr_group)
        self.attr_text = QTextEdit()
        self.attr_text.setReadOnly(True)
        self.attr_text.setMaximumHeight(150)
        attr_layout.addWidget(self.attr_text)
        left_layout.addWidget(self.attr_group)
        
        self.info_group = QGroupBox("Info")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        self.stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(self.stats_group)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        stats_layout.addWidget(self.stats_text)
        left_layout.addWidget(self.stats_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        self.map_canvas = JomanCanvas(self)
        layout.addWidget(self.map_canvas, 1)
        
        right_panel = QWidget()
        right_panel.setMaximumWidth(80)
        right_layout = QVBoxLayout(right_panel)
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QVBoxLayout(zoom_group)
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setRange(0, 100)
        self.zoom_slider.setValue(50)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider)
        zoom_layout.addWidget(self.zoom_slider)
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        right_layout.addWidget(zoom_group)
        right_layout.addStretch()
        layout.addWidget(right_panel)
    
    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Add", self.load_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("Export", self.export_map, "Ctrl+E")
        file_menu.addAction("Print", self.print_map, "Ctrl+P")
        file_menu.addAction("Quit", self.close, "Ctrl+Q")
    
    def load_file(self):
        formats = "Files (*.shp *.geojson *.json *.kml *.kmz);;Geodatabase (*.gdb)"
        filename, _ = QFileDialog.getOpenFileName(self, "Load", "", formats)
        if filename:
            try:
                if filename.endswith('.gdb'):
                    layers = pyogrio.list_layers(filename)
                    layer_names = [l[0] for l in layers]
                    if layer_names:
                        layer, ok = QInputDialog.getItem(self, "JOMAN", "Select layer:", layer_names, 0, False)
                        if ok and layer:
                            gdf = gpd.read_file(filename, layer=layer)
                            name = os.path.basename(filename) + f" ({layer})"
                        else:
                            return
                    else:
                        raise ValueError("No layer found")
                else:
                    gdf = gpd.read_file(filename)
                    name = os.path.basename(filename)
                
                self.current_gdf = gdf
                self.current_name = name
                self.map_canvas.current_gdf = gdf
                self.map_canvas.current_name = name
                self.map_canvas.draw_map()
                self.layer_list.clear()
                self.layer_list.addItem(f"{name} ({len(gdf)} features)")
                
                geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Unknown"
                cols = [c for c in gdf.columns if c != 'geometry']
                info = f"File: {name}\nType: {geom_type}\nFeatures: {len(gdf)}\nColumns: {', '.join(cols[:5])}"
                if len(cols) > 5:
                    info += f" (+{len(cols)-5})"
                self.info_text.setText(info)
                
                self.update_stats()
                self.statusBar().showMessage(f"Loaded: {name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def update_stats(self):
        if self.current_gdf is None:
            return
        gdf = self.current_gdf
        stats = f"Features: {len(gdf)}\nColumns: {len(gdf.columns)-1}"
        self.stats_text.setText(stats)
    
    def show_attributes(self, idx, row):
        text = f"Feature {idx}\n" + "=" * 30 + "\n"
        for col in row.index:
            if col != 'geometry':
                text += f"> {col}: {row[col]}\n"
        self.attr_text.setText(text)
    
    def clear_attributes(self):
        self.attr_text.clear()
    
    def toggle_measure(self):
        mode = self.map_canvas.toggle_measure_mode()
        if mode:
            self.btn_measure.setText("Distance (ON)")
            self.btn_measure.setStyleSheet("padding: 8px; background-color: #FF6B6B;")
        else:
            self.btn_measure.setText("Distance (OFF)")
            self.btn_measure.setStyleSheet("padding: 8px;")
    
    def toggle_area(self):
        mode = self.map_canvas.toggle_area_mode()
        if mode:
            self.btn_area.setText("Area (ON)")
            self.btn_area.setStyleSheet("padding: 8px; background-color: #4ECDC4;")
        else:
            self.btn_area.setText("Area (OFF)")
            self.btn_area.setStyleSheet("padding: 8px;")
    
    def toggle_labels(self):
        show = self.map_canvas.toggle_labels()
        if show:
            self.btn_labels.setText("Labels (ON)")
            self.btn_labels.setStyleSheet("padding: 8px; background-color: #4ECDC4; color: #1a1a2a;")
            self.statusBar().showMessage("Labels ON")
        else:
            self.btn_labels.setText("Labels (OFF)")
            self.btn_labels.setStyleSheet("padding: 8px; background-color: #555; color: white;")
            self.statusBar().showMessage("Labels OFF")
    
    def export_map(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export", "", "PNG (*.png)")
        if filename:
            self.map_canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
            self.statusBar().showMessage("Map exported")
    
    def search_features(self):
        if self.current_gdf is None:
            return
        search_text = self.search_edit.text().lower()
        if not search_text:
            self.search_results.clear()
            return
        self.search_results.clear()
        name_col = self.map_canvas.get_name_column()
        for idx, row in self.current_gdf.iterrows():
            for col in self.current_gdf.columns:
                if col != 'geometry' and search_text in str(row[col]).lower():
                    display = str(row[name_col]) if name_col and row[name_col] else f"Feature {idx}"
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
    
    def on_layer_click(self, item):
        pass


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
    print("=" * 60)
    print("JOMAN - GIS Software")
    print("Version 1.0.0")
    print("=" * 60)
    print("READY - Drag and drop your files")
    print("Supported formats: SHP, GeoJSON, KML, CSV")
    print("=" * 60)
    sys.exit(app.exec())







