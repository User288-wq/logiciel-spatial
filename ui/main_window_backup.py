# -*- coding: utf-8 -*-
import sys
import os
import math

# Ajouter le dossier parent au chemin
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from map_canvas import MapCanvas
from gis.loaders import loader

APP_NAME = "JOMAN GIS"
APP_VERSION = "3.0.0"

class BrowserTreeWidget(QTreeWidget):
    file_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Navigateur")
        self.setup_tree()
    
    def setup_tree(self):
        xyz = QTreeWidgetItem(self)
        xyz.setText(0, "🌐 XYZ Tiles")
        xyz.addChild(QTreeWidgetItem(xyz, ["OpenStreetMap"]))
        xyz.addChild(QTreeWidgetItem(xyz, ["Satellite"]))
        
        shapefiles = QTreeWidgetItem(self)
        shapefiles.setText(0, "🗺️ Shapefiles")
        
        self.addTopLevelItem(xyz)
        self.addTopLevelItem(shapefiles)
        self.expandAll()

class ProcessingToolboxWidget(QTreeWidget):
    tool_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Boite a outils")
        self.setup_tools()
    
    def setup_tools(self):
        geo = QTreeWidgetItem(self)
        geo.setText(0, "⚙️ Geoprocessing")
        geo.addChild(QTreeWidgetItem(geo, ["Buffer"]))
        geo.addChild(QTreeWidgetItem(geo, ["Intersection"]))
        
        geom = QTreeWidgetItem(self)
        geom.setText(0, "📏 Geometry Tools")
        geom.addChild(QTreeWidgetItem(geom, ["Centroids"]))
        
        self.addTopLevelItem(geo)
        self.addTopLevelItem(geom)
        self.expandAll()

class LayerPropertiesWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layer = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QTabWidget::pane { background-color: #1a1a2a; border: none; }
            QTabBar::tab { background-color: #16213e; color: white; padding: 6px 12px; }
            QTabBar::tab:selected { background-color: #4CAF50; }
        """)
        
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background: #16213e; color: #00ff00;")
        info_layout.addWidget(self.info_text)
        self.addTab(self.info_tab, "Info")
        
        self.attr_tab = QWidget()
        attr_layout = QVBoxLayout(self.attr_tab)
        self.attr_table = QTableWidget()
        self.attr_table.setColumnCount(3)
        self.attr_table.setHorizontalHeaderLabels(["Champ", "Type", "Exemple"])
        attr_layout.addWidget(self.attr_table)
        self.addTab(self.attr_tab, "Attributs")
    
    def update_layer(self, layer):
        self.current_layer = layer
        if not layer or not layer.get('gdf'):
            self.info_text.setText("Aucune couche")
            return
        
        gdf = layer['gdf']
        info = f"""
Nom: {layer['name']}
Type: {layer['type']}
Entites: {len(gdf)}
Projection: {gdf.crs or 'WGS84'}
"""
        self.info_text.setText(info)
        
        self.attr_table.setRowCount(len(gdf.columns) - 1)
        row = 0
        for col in gdf.columns:
            if col != 'geometry':
                self.attr_table.setItem(row, 0, QTableWidgetItem(col))
                self.attr_table.setItem(row, 1, QTableWidgetItem(str(gdf[col].dtype)))
                row += 1

class LegendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("LEGENDE")
        title.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)
        
        self.legend_tree = QTreeWidget()
        self.legend_tree.setHeaderHidden(True)
        layout.addWidget(self.legend_tree)
    
    def update_legend(self, layers):
        self.legend_tree.clear()
        for layer in layers:
            item = QTreeWidgetItem(self.legend_tree)
            icon = {'Point': '🔴', 'LineString': '🟠', 'Polygon': '🟢'}.get(layer['type'], '📌')
            item.setText(0, f"{icon} {layer['name']}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(50, 50, 1400, 800)
        self.setAcceptDrops(True)
        
        self.layers = []
        self.current_layer = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        
        self.statusBar().showMessage("Pret")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        
        self.browser = BrowserTreeWidget()
        left_layout.addWidget(QLabel("Navigateur"))
        left_layout.addWidget(self.browser)
        
        self.processing = ProcessingToolboxWidget()
        left_layout.addWidget(QLabel("Outils"))
        left_layout.addWidget(self.processing)
        
        layout.addWidget(left_panel)
        
        # Centre - Carte
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
        
        # Panneau droit
        right_panel = QWidget()
        right_panel.setMaximumWidth(320)
        right_layout = QVBoxLayout(right_panel)
        
        # Couches
        right_layout.addWidget(QLabel("Couches"))
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Couches")
        self.layer_tree.itemClicked.connect(self.on_layer_clicked)
        right_layout.addWidget(self.layer_tree)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(self.load_file)
        btn_remove = QPushButton("Supprimer")
        btn_remove.clicked.connect(self.remove_current_layer)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        right_layout.addLayout(btn_layout)
        
        # Proprietes
        right_layout.addWidget(QLabel("Proprietes"))
        self.properties = LayerPropertiesWidget()
        right_layout.addWidget(self.properties)
        
        # Legende
        right_layout.addWidget(QLabel("Legende"))
        self.legend = LegendWidget()
        right_layout.addWidget(self.legend)
        
        layout.addWidget(right_panel)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Fichier")
        file_menu.addAction("Ouvrir", self.load_file, "Ctrl+O")
        file_menu.addAction("Quitter", self.close, "Ctrl+Q")
        
        view_menu = menubar.addMenu("Affichage")
        view_menu.addAction("Zoom +", self.map_canvas.zoom_in, "Ctrl++")
        view_menu.addAction("Zoom -", self.map_canvas.zoom_out, "Ctrl+-")
        view_menu.addAction("Vue ensemble", self.map_canvas.zoom_all, "Ctrl+0")
        
        tools_menu = menubar.addMenu("Outils")
        tools_menu.addAction("Mesure", self.toggle_measure, "Ctrl+M")
        
        help_menu = menubar.addMenu("Aide")
        help_menu.addAction("A propos", self.about)
    
    def setup_toolbars(self):
        toolbar = self.addToolBar("Outils")
        toolbar.addAction("Ouvrir", self.load_file)
        toolbar.addAction("Zoom +", self.map_canvas.zoom_in)
        toolbar.addAction("Zoom -", self.map_canvas.zoom_out)
        toolbar.addAction("Vue ensemble", self.map_canvas.zoom_all)
        toolbar.addAction("Mesure", self.toggle_measure)
    
    def load_file(self):
        formats = "Fichiers (*.shp *.geojson *.json *.kml *.kmz *.csv)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger", "", formats)
        if filename:
            self.load_file_from_path(filename)
    
    def load_file_from_path(self, filename):
        try:
            gdf = loader.load(filename)
            name = os.path.basename(filename)
            
            geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Polygon"
            layer_type = 'Point' if 'Point' in geom_type else ('LineString' if 'Line' in geom_type else 'Polygon')
            
            layer = {'id': len(self.layers), 'name': name, 'gdf': gdf, 'type': layer_type}
            self.layers.append(layer)
            
            item = QTreeWidgetItem(self.layer_tree)
            icon = '🔴' if layer_type == 'Point' else ('🟠' if layer_type == 'LineString' else '🟢')
            item.setText(0, f"{icon} {name}")
            item.setData(0, Qt.UserRole, layer)
            
            self.legend.update_legend(self.layers)
            
            if not self.current_layer:
                self.current_layer = layer
                color = '#FF4444' if layer_type == 'Point' else ('#FFA500' if layer_type == 'LineString' else '#4CAF50')
                self.map_canvas.draw_layer(gdf, name, color)
                self.properties.update_layer(layer)
            
            self.statusBar().showMessage(f"Charge: {name} ({len(gdf)} entites)")
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
    
    def remove_current_layer(self):
        if self.current_layer:
            self.layers = [l for l in self.layers if l['id'] != self.current_layer['id']]
            self.layer_tree.clear()
            for layer in self.layers:
                item = QTreeWidgetItem(self.layer_tree)
                icon = '🔴' if layer['type'] == 'Point' else ('🟠' if layer['type'] == 'LineString' else '🟢')
                item.setText(0, f"{icon} {layer['name']}")
                item.setData(0, Qt.UserRole, layer)
            
            self.current_layer = self.layers[0] if self.layers else None
            if self.current_layer:
                color = '#FF4444' if self.current_layer['type'] == 'Point' else ('#FFA500' if self.current_layer['type'] == 'LineString' else '#4CAF50')
                self.map_canvas.draw_layer(self.current_layer['gdf'], self.current_layer['name'], color)
                self.properties.update_layer(self.current_layer)
            else:
                self.map_canvas.clear()
                self.properties.update_layer(None)
            
            self.legend.update_legend(self.layers)
    
    def on_layer_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if data:
            self.current_layer = data
            color = '#FF4444' if data['type'] == 'Point' else ('#FFA500' if data['type'] == 'LineString' else '#4CAF50')
            self.map_canvas.draw_layer(data['gdf'], data['name'], color)
            self.properties.update_layer(data)
    
    def toggle_measure(self):
        mode = self.map_canvas.toggle_measure_mode()
        self.statusBar().showMessage("Mesure ON" if mode else "Mesure OFF")
    
    def about(self):
        QMessageBox.about(self, "A propos", f"JOMAN GIS v{APP_VERSION}\nLogiciel SIG")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
