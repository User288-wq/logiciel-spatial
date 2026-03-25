#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CHARGEUR DE CARTES SIMPLE
==========================
- Interface PySide6
- Charge un fichier vectoriel (.shp, .geojson)
- Affiche la carte avec matplotlib
- Zoom et pan basiques
- Gestionnaire de couches rudimentaire
"""

import os
import sys
import geopandas as gpd
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Configuration Qt/Matplotlib
os.environ["QT_API"] = "pyside6"

class CarteWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
    def afficher_gdf(self, gdf):
        """Affiche un GeoDataFrame sur la carte"""
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        gdf.plot(ax=self.ax, alpha=0.7, edgecolor='white')
        self.ax.tick_params(colors='white')
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Chargeur de cartes")
        self.setGeometry(100, 100, 1000, 700)
        
        # Liste des couches chargées
        self.layers = []
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panneau gauche (contrôles)
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Bouton charger
        self.btn_charger = QPushButton("📂 Charger un fichier")
        self.btn_charger.clicked.connect(self.charger_fichier)
        left_layout.addWidget(self.btn_charger)
        
        # Liste des couches
        self.liste_couches = QListWidget()
        self.liste_couches.itemClicked.connect(self.selection_couche)
        left_layout.addWidget(QLabel("Couches chargées :"))
        left_layout.addWidget(self.liste_couches)
        
        # Bouton supprimer
        self.btn_supprimer = QPushButton("🗑️ Supprimer la couche")
        self.btn_supprimer.clicked.connect(self.supprimer_couche)
        self.btn_supprimer.setEnabled(False)
        left_layout.addWidget(self.btn_supprimer)
        
        layout.addWidget(left_panel)
        
        # Zone centrale (carte)
        self.carte = CarteWidget()
        layout.addWidget(self.carte, 1)
        
        # Barre d'état
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Prêt")
        
    def charger_fichier(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger un fichier", "",
            "Fichiers supportés (*.shp *.geojson *.json);;Shapefile (*.shp);;GeoJSON (*.geojson);;Tous (*.*)"
        )
        if not filename:
            return
        
        try:
            gdf = gpd.read_file(filename)
            nom = os.path.basename(filename)
            self.layers.append({'name': nom, 'gdf': gdf})
            self.liste_couches.addItem(nom)
            self.mettre_a_jour_carte()
            self.status.showMessage(f"✅ {nom} chargé")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier :\n{e}")
            self.status.showMessage("❌ Erreur de chargement")
    
    def supprimer_couche(self):
        current = self.liste_couches.currentRow()
        if current >= 0:
            del self.layers[current]
            self.liste_couches.takeItem(current)
            self.mettre_a_jour_carte()
            self.btn_supprimer.setEnabled(False)
            self.status.showMessage("Couche supprimée")
    
    def selection_couche(self):
        self.btn_supprimer.setEnabled(True)
    
    def mettre_a_jour_carte(self):
        if not self.layers:
            self.carte.ax.clear()
            self.carte.ax.set_facecolor('#0a1a2a')
            self.carte.canvas.draw()
            return
        
        # On affiche toutes les couches superposées
        self.carte.ax.clear()
        self.carte.ax.set_facecolor('#0a1a2a')
        for layer in self.layers:
            layer['gdf'].plot(ax=self.carte.ax, alpha=0.7, edgecolor='white')
        self.carte.ax.tick_params(colors='white')
        self.carte.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
