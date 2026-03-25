import sys
import os
import geopandas as gpd
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

print("=== DÉMARRAGE DE L'INTERFACE SIMPLIFIÉE ===")

class SimpleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Logiciel de Cartographie - Version Simplifiée")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panneau gauche
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre
        title = QLabel("📂 Gestionnaire de couches")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4CAF50;")
        left_layout.addWidget(title)
        
        # Liste des couches
        self.layer_list = QListWidget()
        left_layout.addWidget(self.layer_list)
        
        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ajouter un fichier")
        self.btn_add.clicked.connect(self.load_file)
        self.btn_clear = QPushButton("🗑️ Tout effacer")
        self.btn_clear.clicked.connect(self.clear_layers)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)
        
        # Zone d'info
        self.info_label = QLabel("💡 Cliquez sur 'Ajouter' pour charger un fichier\nFormats: .shp, .geojson, .json, .kml, .kmz, .csv")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("background-color: #16213e; color: #ffaa00; padding: 8px; border-radius: 5px;")
        left_layout.addWidget(self.info_label)
        
        layout.addWidget(left_panel)
        
        # Zone centrale (simple message pour l'instant)
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        self.map_label = QLabel("🗺️ CARTE\n\nCliquez sur 'Ajouter' pour charger un fichier\n\nLes données s'afficheront ici")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setStyleSheet("background-color: #0a1a2a; color: white; border: 1px solid #4CAF50;")
        self.map_label.setMinimumHeight(500)
        center_layout.addWidget(self.map_label)
        
        layout.addWidget(center_panel, 1)
        
        # Barre d'état
        self.statusBar().showMessage("Prêt - Chargez un fichier")
        
        print("Interface initialisée")
    
    def load_file(self):
        """Charge un fichier"""
        formats = "Fichiers supportés (*.shp *.geojson *.json *.kml *.kmz *.csv *.txt);;Shapefile (*.shp);;GeoJSON (*.geojson *.json);;KML/KMZ (*.kml *.kmz);;CSV (*.csv *.txt)"
        filename, _ = QFileDialog.getOpenFileName(self, "Charger un fichier", "", formats)
        
        if filename:
            print(f"Fichier sélectionné: {filename}")
            try:
                # Essayer de charger avec GeoPandas
                gdf = gpd.read_file(filename)
                name = os.path.basename(filename)
                self.layer_list.addItem(f"📌 {name}")
                self.statusBar().showMessage(f"✅ {name} chargé avec succès ({len(gdf)} entités)")
                self.info_label.setText(f" {name} chargé\nEntités: {len(gdf)}\nColonnes: {len(gdf.columns)}")
                
                # Afficher les premières lignes dans la console
                print(f"   Entités: {len(gdf)}")
                print(f"   Colonnes: {list(gdf.columns)}")
                print(f"   Étendue: {gdf.total_bounds}")
                
            except Exception as e:
                print(f"Erreur: {e}")
                self.statusBar().showMessage(f"❌ Erreur: {e}")
                QMessageBox.warning(self, "Erreur", f"Impossible de charger {name}\n{str(e)}")
    
    def clear_layers(self):
        """Efface toutes les couches"""
        self.layer_list.clear()
        self.statusBar().showMessage("Toutes les couches supprimées")
        self.info_label.setText("💡 Cliquez sur 'Ajouter' pour charger un fichier")

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
    
    window = SimpleMainWindow()
    window.show()
    print("Fenêtre affichée")
    
    sys.exit(app.exec())