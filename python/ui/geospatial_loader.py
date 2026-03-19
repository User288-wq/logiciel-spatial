import geopandas as gpd
import matplotlib.pyplot as plt
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class GeospatialLoader(QWidget):
    """Charge et visualise des fichiers géospatiaux"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Chargeur de données géospatiales")
        self.setGeometry(100, 100, 1000, 700)
        
        self.current_gdf = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QToolBar()
        
        self.load_btn = QPushButton("📂 Charger Shapefile")
        self.load_btn.clicked.connect(self.load_shapefile)
        toolbar.addWidget(self.load_btn)
        
        self.load_raster_btn = QPushButton("🖼️ Charger GeoTIFF")
        self.load_raster_btn.clicked.connect(self.load_raster)
        toolbar.addWidget(self.load_raster_btn)
        
        toolbar.addSeparator()
        
        self.export_btn = QPushButton("💾 Exporter GeoJSON")
        self.export_btn.clicked.connect(self.export_geojson)
        toolbar.addWidget(self.export_btn)
        
        layout.addWidget(toolbar)
        
        # Zone d'information
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
        
        # Message d'aide
        self.help_label = QLabel(
            "💡 Téléchargez des données gratuites sur:\n"
            "• https://www.naturalearthdata.com/ (données mondiales)\n"
            "• https://data.humdata.org/ (données humanitaires)\n"
            "• https://www.diva-gis.org/ (données administratives)"
        )
        self.help_label.setStyleSheet("""
            background-color: #16213e;
            color: #4CAF50;
            padding: 10px;
            border-radius: 5px;
        """)
        layout.addWidget(self.help_label)
        
    def load_shapefile(self):
        """Charge un fichier shapefile"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger Shapefile", "", 
            "Shapefile (*.shp);;GeoJSON (*.geojson);;Tous (*.*)"
        )
        
        if filename:
            try:
                self.current_gdf = gpd.read_file(filename)
                self.show_info()
                QMessageBox.information(self, "Succès", 
                    f"Fichier chargé: {len(self.current_gdf)} entités")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def load_raster(self):
        """Charge un fichier raster GeoTIFF"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger GeoTIFF", "", "GeoTIFF (*.tif *.tiff)"
        )
        
        if filename:
            QMessageBox.information(self, "Info", 
                "Fonctionnalité à implémenter avec rasterio")
    
    def export_geojson(self):
        """Exporte en GeoJSON"""
        if self.current_gdf is None:
            QMessageBox.warning(self, "Attention", "Aucune donnée chargée")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter GeoJSON", "", "GeoJSON (*.geojson)"
        )
        
        if filename:
            try:
                self.current_gdf.to_file(filename, driver="GeoJSON")
                QMessageBox.information(self, "Succès", "Export terminé!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def show_info(self):
        """Affiche les informations sur les données chargées"""
        if self.current_gdf is None:
            return
        
        info = f"📊 INFORMATIONS SUR LES DONNÉES\n"
        info += "="*40 + "\n\n"
        info += f"Nombre d'entités: {len(self.current_gdf)}\n"
        info += f"Type de géométrie: {self.current_gdf.geometry.type.iloc[0]}\n"
        info += f"Système de coordonnées: {self.current_gdf.crs}\n"
        info += f"Étendue:\n"
        info += f"  X: {self.current_gdf.total_bounds[0]:.2f} à {self.current_gdf.total_bounds[2]:.2f}\n"
        info += f"  Y: {self.current_gdf.total_bounds[1]:.2f} à {self.current_gdf.total_bounds[3]:.2f}\n\n"
        info += f"Colonnes disponibles:\n"
        
        for col in self.current_gdf.columns:
            if col != 'geometry':
                info += f"  • {col}\n"
        
        self.info_text.setText(info)