#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CHARGEUR DE CARTES AVEC COULEURS ET ÉTIQUETTES
================================================
- Interface PySide6
- Charge des fichiers vectoriels (.shp, .geojson)
- Attribue automatiquement une couleur selon le type (région, commune, route, hydro, etc.)
- Affiche les noms des entités (étiquettes) pour les régions et communes
- Cases à cocher pour activer/désactiver chaque couche
- Zoom, pan, export d'image
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

# Palette de couleurs par type de couche
COLORS = {
    'region':   '#4CAF50',  # vert
    'commune':  '#FFA500',  # orange
    'route':    '#808080',  # gris
    'hydro':    '#2196F3',  # bleu
    'point':    '#FF4444',  # rouge
    'line':     '#FFA500',  # orange
    'polygon':  '#4CAF50',  # vert
    'default':  '#888888'   # gris foncé
}

class CarteWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), facecolor='#0a1a2a')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0a1a2a')
        self.ax.tick_params(colors='white')
        
        # Barre de navigation matplotlib (zoom, pan)
        self.nav_toolbar = NavToolbar(self.canvas, self)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)
        
    def afficher_couches(self, couches):
        """Affiche toutes les couches visibles avec leurs couleurs et étiquettes."""
        self.ax.clear()
        self.ax.set_facecolor('#0a1a2a')
        
        for couche in couches:
            if not couche['visible']:
                continue
            gdf = couche['gdf']
            typ = couche['type']
            color = COLORS.get(typ, COLORS['default'])
            
            # Tracé de la géométrie
            gdf.plot(ax=self.ax, color=color, edgecolor='white', linewidth=0.5, alpha=0.7)
            
            # Ajout des étiquettes pour les types qui ont un nom
            if typ in ['region', 'commune']:
                self.ajouter_etiquettes(gdf)
        
        self.ax.tick_params(colors='white')
        self.ax.set_title("Carte", color='white')
        self.canvas.draw()
    
    def ajouter_etiquettes(self, gdf):
        """Ajoute le nom de chaque entité au centroïde."""
        # Chercher une colonne de nom (NAME, name, NOM, etc.)
        nom_col = None
        for col in ['NAME', 'name', 'NOM', 'ADMIN1', 'ADMIN4']:
            if col in gdf.columns:
                nom_col = col
                break
        if not nom_col:
            return
        
        for _, row in gdf.iterrows():
            if row.geometry and not row.geometry.is_empty:
                centroid = row.geometry.centroid
                label = str(row[nom_col])
                self.ax.text(centroid.x, centroid.y, label,
                             fontsize=8, color='white',
                             ha='center', va='center',
                             bbox=dict(boxstyle="round,pad=0.2",
                                       facecolor='#1a1a2a',
                                       alpha=0.7,
                                       edgecolor='none'))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Carte avec couleurs et étiquettes")
        self.setGeometry(100, 100, 1200, 800)
        
        self.couches = []  # liste de dicts : name, gdf, type, visible
        
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
        
        # Liste des couches avec cases à cocher
        left_layout.addWidget(QLabel("Couches chargées :"))
        self.liste_couches = QListWidget()
        self.liste_couches.itemChanged.connect(self.coche_changee)
        left_layout.addWidget(self.liste_couches)
        
        # Bouton supprimer
        self.btn_supprimer = QPushButton("🗑️ Supprimer la sélection")
        self.btn_supprimer.clicked.connect(self.supprimer_couche)
        left_layout.addWidget(self.btn_supprimer)
        
        # Bouton exporter
        self.btn_exporter = QPushButton("💾 Exporter la carte")
        self.btn_exporter.clicked.connect(self.exporter_carte)
        left_layout.addWidget(self.btn_exporter)
        
        left_layout.addStretch()
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
            
            # Déterminer le type à partir du nom (simple heuristique)
            typ = 'default'
            lower = filename.lower()
            if 'region' in lower:
                typ = 'region'
            elif 'commune' in lower:
                typ = 'commune'
            elif 'route' in lower or 'road' in lower:
                typ = 'route'
            elif 'hydro' in lower or 'eau' in lower or 'water' in lower:
                typ = 'hydro'
            elif 'point' in lower:
                typ = 'point'
            elif 'line' in lower:
                typ = 'line'
            elif 'polygon' in lower:
                typ = 'polygon'
            
            # Créer l'item avec case à cocher
            item = QListWidgetItem(nom)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, len(self.couches))  # indice pour retrouver la couche
            
            self.liste_couches.addItem(item)
            self.couches.append({
                'name': nom,
                'gdf': gdf,
                'type': typ,
                'visible': True,
                'item': item
            })
            
            self.mettre_a_jour_carte()
            self.status.showMessage(f"✅ {nom} chargé (type: {typ})")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier :\n{e}")
            self.status.showMessage("❌ Erreur de chargement")
    
    def coche_changee(self, item):
        """Quand on coche/décoche une couche."""
        idx = item.data(Qt.UserRole)
        if idx is not None and 0 <= idx < len(self.couches):
            visible = (item.checkState() == Qt.Checked)
            self.couches[idx]['visible'] = visible
            self.mettre_a_jour_carte()
    
    def supprimer_couche(self):
        """Supprime la ou les couches sélectionnées."""
        for item in self.liste_couches.selectedItems():
            idx = item.data(Qt.UserRole)
            if idx is not None:
                # Supprimer de la liste et des données
                self.liste_couches.takeItem(self.liste_couches.row(item))
                del self.couches[idx]
                # Re-indexer les items restants
                for i, couche in enumerate(self.couches):
                    couche['item'].setData(Qt.UserRole, i)
        self.mettre_a_jour_carte()
        self.status.showMessage("Couche(s) supprimée(s)")
    
    def mettre_a_jour_carte(self):
        """Met à jour l'affichage de la carte avec les couches visibles."""
        self.carte.afficher_couches(self.couches)
    
    def exporter_carte(self):
        """Sauvegarde la carte actuelle en image."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter la carte", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        if filename:
            self.carte.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#0a1a2a')
            self.status.showMessage(f"✅ Carte exportée : {os.path.basename(filename)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
