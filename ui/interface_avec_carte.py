import sys
import os
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=== DÉMARRAGE DE L'INTERFACE AVEC CARTE ===")

class MapCanvas(QWidget):
    """Canvas pour afficher la carte Matplotlib"""
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
    
    def draw_data(self, gdf, name):
        """Affiche les données sur la carte"""
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        if gdf is not None and len(gdf) > 0:
            # Déterminer le type de géométrie
            geom_type = gdf.geometry.type.iloc[0]
            
            # Choisir la couleur selon le type
            if 'Point' in geom_type:
                color = '#FF4444'
                marker = 'o'
                size = 50
                gdf.plot(ax=self.ax, color=color, marker=marker, markersize=size, alpha=0.8)
            elif 'Line' in geom_type:
                color = '#FFA500'
                gdf.plot(ax=self.ax, color=color, linewidth=1.5, alpha=0.8)
            else:
                color = '#4CAF50'
                gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=0.5, alpha=0.6)
            
            # Ajuster les limites
            bounds = gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            # Ajouter un titre
            self.ax.set_title(f"{name} - {len(gdf)} entités", color='white', fontsize=12)
        else:
            self.ax.text(0.5, 0.5, "Aucune donnée à afficher\nCliquez sur 'Ajouter' pour charger un fichier",
                        transform=self.ax.transAxes, ha='center', va='center',
                        color='white', fontsize=12)
        
        self.ax.tick_params(colors='white')
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Logiciel de Cartographie - Version avec Carte")
        self.setGeometry(100, 100, 1300, 800)
        
        self.current_gdf = None
        self.current_name = None
        
        self.setup_ui()
        self.statusBar().showMessage("Prêt - Chargez un fichier")
        print("Interface initialisée")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # ===== PANNAU GAUCHE =====
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre
        title = QLabel("📂 GESTIONNAIRE DE COUCHES")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50; padding: 5px;")
        left_layout.addWidget(title)
        
        # Liste des couches chargées
        left_layout.addWidget(QLabel("Couches chargées:"))
        self.layer_list = QListWidget()
        self.layer_list.itemClicked.connect(self.on_layer_selected)
        left_layout.addWidget(self.layer_list)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter un fichier")
        self.btn_add.clicked.connect(self.load_file)
        self.btn_clear = QPushButton("🗑️ Effacer tout")
        self.btn_clear.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)
        
        # Informations
        self.info_group = QGroupBox("📋 Informations")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("background-color: #16213e; color: #00ff00; font-family: 'Courier New'; font-size: 10px;")
        info_layout.addWidget(self.info_text)
        left_layout.addWidget(self.info_group)
        
        # Légende
        legend_group = QGroupBox("📖 Légende")
        legend_layout = QVBoxLayout(legend_group)
        legend_items = [
            ('🟩', 'Polygones (Régions, communes)', '#4CAF50'),
            ('🟧', 'Lignes (Routes)', '#FFA500'),
            ('🔴', 'Points (Villes)', '#FF4444'),
        ]
        for icon, name, color in legend_items:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.addWidget(QLabel(icon))
            layout.addWidget(QLabel(name))
            layout.addStretch()
            legend_layout.addWidget(widget)
        left_layout.addWidget(legend_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # ===== ZONE CENTRALE (CARTE) =====
        self.map_canvas = MapCanvas(self)
        layout.addWidget(self.map_canvas, 1)
    
    def load_file(self):
        """Charge un fichier"""
        formats = "Fichiers supportés (*.shp *.geojson *.json *.kml *.kmz *.csv *.txt);;Shapefile (*.shp);;GeoJSON (*.geojson *.json);;KML/KMZ (*.kml *.kmz);;CSV (*.csv *.txt)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", formats)
        
        if filename:
            print(f"\n📂 Chargement: {filename}")
            try:
                gdf = gpd.read_file(filename)
                name = os.path.basename(filename)
                
                # Stocker la couche courante
                self.current_gdf = gdf
                self.current_name = name
                
                # Ajouter à la liste
                geom_type = gdf.geometry.type.iloc[0] if len(gdf) > 0 else "Unknown"
                icon = '📍' if 'Point' in geom_type else ('📏' if 'Line' in geom_type else '🔲')
                self.layer_list.addItem(f"{icon} {name} ({len(gdf)} entités)")
                self.layer_list.setCurrentRow(self.layer_list.count() - 1)
                
                # Afficher sur la carte
                self.map_canvas.draw_data(gdf, name)
                
                # Afficher les informations
                info = f"Fichier: {name}\n"
                info += f"Type: {geom_type}\n"
                info += f"Entités: {len(gdf)}\n"
                info += f"Colonnes: {len(gdf.columns) - 1}\n\n"
                info += "Colonnes:\n"
                for col in gdf.columns:
                    if col != 'geometry':
                        info += f"  • {col}\n"
                self.info_text.setText(info)
                
                self.statusBar().showMessage(f"✅ {name} chargé ({len(gdf)} entités)")
                print(f"   ✅ Chargé: {len(gdf)} entités")
                print(f"   📊 Géométrie: {geom_type}")
                print(f"   🌍 Étendue: {gdf.total_bounds}")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                self.statusBar().showMessage(f"❌ Erreur: {e}")
                QMessageBox.warning(self, "Erreur", f"Impossible de charger {os.path.basename(filename)}\n{str(e)}")
    
    def on_layer_selected(self, item):
        """Quand une couche est sélectionnée dans la liste"""
        # Pour l'instant, on garde la couche courante
        # On pourrait gérer plusieurs couches
        pass
    
    def clear_all(self):
        """Efface tout"""
        self.layer_list.clear()
        self.current_gdf = None
        self.current_name = None
        self.map_canvas.draw_data(None, None)
        self.info_text.clear()
        self.statusBar().showMessage("Tout effacé")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    print(" Fenêtre affichée")
    
    sys.exit(app.exec())