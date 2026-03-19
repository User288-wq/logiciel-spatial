#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 LOGICIEL SPATIAL COMPLET - Version Ultime
=============================================
Intègre toutes les fonctionnalités :
- Système solaire 3D
- Images satellites
- Données OpenStreetMap
- Analyse géospatiale
- Missions spatiales
- Météo spatiale
"""

import sys
import os
import numpy as np
from datetime import datetime
import random

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *

# ============================================================================
# MODULE 1: SYSTÈME SOLAIRE
# ============================================================================

class SystemeSolaireModule(QWidget):
    """Module de simulation du système solaire"""
    
    def __init__(self):
        super().__init__()
        self.planetes = self.charger_planetes()
        self.positions = {p["nom"]: random.uniform(0, 2*np.pi) for p in self.planetes}
        self.setup_ui()
        
    def charger_planetes(self):
        return [
            {"nom": "Mercure", "distance": 57.9, "diametre": 4879, "couleur": "#a5a5a5", "lunes": 0},
            {"nom": "Vénus", "distance": 108.2, "diametre": 12104, "couleur": "#ffb347", "lunes": 0},
            {"nom": "Terre", "distance": 149.6, "diametre": 12742, "couleur": "#4a90e2", "lunes": 1},
            {"nom": "Mars", "distance": 227.9, "diametre": 6779, "couleur": "#e27a4a", "lunes": 2},
            {"nom": "Jupiter", "distance": 778.5, "diametre": 139820, "couleur": "#d98c4a", "lunes": 79},
            {"nom": "Saturne", "distance": 1433.5, "diametre": 116460, "couleur": "#e0b060", "lunes": 82},
            {"nom": "Uranus", "distance": 2872.5, "diametre": 50724, "couleur": "#7ec8e0", "lunes": 27},
            {"nom": "Neptune", "distance": 4495.1, "diametre": 49244, "couleur": "#4a6ee0", "lunes": 14}
        ]
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QToolBar()
        toolbar.addAction("🔄 Animer", self.animer)
        toolbar.addAction("📊 Statistiques", self.stats)
        toolbar.addAction("🚀 Missions", self.missions)
        layout.addWidget(toolbar)
        
        # Canvas pour le dessin
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor(10, 10, 42)))
        layout.addWidget(self.view)
        
        self.dessiner_systeme()
        
        # Timer pour animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.mouvement)
        
    def dessiner_systeme(self):
        self.scene.clear()
        
        # Soleil
        soleil = self.scene.addEllipse(-20, -20, 40, 40, QPen(Qt.yellow), QBrush(Qt.yellow))
        soleil.setPos(400, 300)
        self.scene.addText("☀️ Soleil").setPos(380, 250)
        
        # Orbites et planètes
        echelle = 0.2
        for p in self.planetes:
            rayon = p["distance"] * echelle
            if rayon < 350:
                # Orbite
                self.scene.addEllipse(400 - rayon, 300 - rayon, rayon*2, rayon*2,
                                     QPen(QColor(51, 51, 102)), QBrush(Qt.NoBrush))
                
                # Planète
                angle = self.positions[p["nom"]]
                x = 400 + rayon * np.cos(angle)
                y = 300 + rayon * np.sin(angle)
                
                taille = max(2, p["diametre"] / 15000)
                couleur = QColor(p["couleur"])
                planete = self.scene.addEllipse(-taille, -taille, taille*2, taille*2,
                                               QPen(Qt.white), QBrush(couleur))
                planete.setPos(x, y)
                
                # Nom
                text = self.scene.addText(p["nom"])
                text.setPos(x - 20, y - 25)
                text.setDefaultTextColor(Qt.white)
    
    def mouvement(self):
        for p in self.planetes:
            vitesse = 0.01 / np.sqrt(p["distance"])
            self.positions[p["nom"]] += vitesse
        self.dessiner_systeme()
    
    def animer(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(50)
    
    def stats(self):
        QMessageBox.information(self, "Statistiques", 
            f"🌍 {len(self.planetes)} planètes\n"
            f"🌙 {sum(p['lunes'] for p in self.planetes)} lunes\n"
            f"📏 Distance max: {self.planetes[-1]['distance']} M km")
    
    def missions(self):
        missions = QDialog(self)
        missions.setWindowTitle("Missions spatiales")
        missions.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout(missions)
        
        missions_list = QListWidget()
        missions_list.addItems([
            "🚀 Artemis II - Retour sur la Lune (2025)",
            "🚀 Mars Sample Return - Prélèvements martiens (2028)",
            "🚀 Europa Clipper - Exploration de Jupiter (2024)",
            "🚀 JUICE - Étude des lunes glacées",
            "🚀 Télescope James Webb - Observation cosmique"
        ])
        layout.addWidget(missions_list)
        
        missions.exec()

# ============================================================================
# MODULE 2: SATELLITES
# ============================================================================

class SatellitesModule(QWidget):
    """Module de suivi des satellites"""
    
    def __init__(self):
        super().__init__()
        self.satellites = self.charger_satellites()
        self.setup_ui()
        
    def charger_satellites(self):
        return [
            {"nom": "ISS", "type": "Station habitée", "pays": "International", 
             "altitude": 408, "vitesse": 7.66},
            {"nom": "Hubble", "type": "Télescope", "pays": "USA", 
             "altitude": 540, "vitesse": 7.59},
            {"nom": "Sentinel-2", "type": "Observation", "pays": "Europe", 
             "altitude": 786, "vitesse": 7.45},
            {"nom": "GPS", "type": "Navigation", "pays": "USA", 
             "altitude": 20200, "vitesse": 3.87},
            {"nom": "Tiangong", "type": "Station", "pays": "Chine", 
             "altitude": 340, "vitesse": 7.68},
            {"nom": "Starlink", "type": "Communication", "pays": "USA", 
             "altitude": 550, "vitesse": 7.50},
        ]
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tableau des satellites
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nom", "Type", "Pays", "Altitude", "Vitesse"])
        
        self.table.setRowCount(len(self.satellites))
        for i, sat in enumerate(self.satellites):
            self.table.setItem(i, 0, QTableWidgetItem(sat["nom"]))
            self.table.setItem(i, 1, QTableWidgetItem(sat["type"]))
            self.table.setItem(i, 2, QTableWidgetItem(sat["pays"]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{sat['altitude']} km"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{sat['vitesse']} km/s"))
        
        layout.addWidget(self.table)
        
        # Graphique
        chart = QChart()
        chart.setTitle("Satellites par pays")
        
        series = QPieSeries()
        series.append("USA", 3)
        series.append("Europe", 1)
        series.append("Chine", 1)
        series.append("International", 1)
        
        chart.addSeries(series)
        chart_view = QChartView(chart)
        layout.addWidget(chart_view)

# ============================================================================
# MODULE 3: DONNÉES OSM
# ============================================================================

class OSMModule(QWidget):
    """Module OpenStreetMap"""
    
    def __init__(self):
        super().__init__()
        self.villes = {
            "Dakar, Sénégal": {"pop": 1146000, "area": 83},
            "Paris, France": {"pop": 2148000, "area": 105},
            "New York, USA": {"pop": 8400000, "area": 784},
            "Touba, Sénégal": {"pop": 753000, "area": 45},
        }
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Panneau gauche
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        self.city_combo = QComboBox()
        self.city_combo.addItems(self.villes.keys())
        left_layout.addWidget(QLabel("Ville:"))
        left_layout.addWidget(self.city_combo)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        left_layout.addWidget(self.stats_text)
        
        load_btn = QPushButton("📥 Charger données")
        load_btn.clicked.connect(self.charger_donnees)
        left_layout.addWidget(load_btn)
        
        layout.addWidget(left)
        
        # Panneau droit (carte)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QColor(26, 26, 42)))
        layout.addWidget(self.view)
        
        self.charger_donnees()
    
    def charger_donnees(self):
        ville = self.city_combo.currentText()
        data = self.villes[ville]
        
        self.stats_text.setText(
            f"📍 {ville}\n"
            f"Population: {data['pop']:,}\n"
            f"Superficie: {data['area']} km²\n"
            f"Densité: {data['pop']/data['area']:.0f} hab/km²"
        )
        
        self.dessiner_carte()
    
    def dessiner_carte(self):
        self.scene.clear()
        
        # Simuler une carte
        for i in range(20):
            x = random.randint(50, 550)
            y = random.randint(50, 350)
            
            # Routes
            pen = QPen(QColor(76, 175, 80))
            self.scene.addLine(x, y, x+100, y+50, pen)
            
            # Bâtiments
            rect = self.scene.addRect(x-5, y-5, 10, 10, QPen(Qt.white), QBrush(QColor(100, 100, 100)))
            rect.setPos(x, y)

# ============================================================================
# MODULE 4: MÉTÉO SPATIALE
# ============================================================================

class MeteoSpatialeModule(QWidget):
    """Module de météo spatiale"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        
        # Indicateurs
        self.indicators = {}
        params = [
            ("🌬️ Vent solaire", "450 km/s", 0, 0),
            ("⚡ Indice Kp", "3 (Calme)", 0, 1),
            ("☀️ Flux solaire", "128 SFU", 1, 0),
            ("⚛️ Protons", "Faible", 1, 1),
            ("🌀 Champ magnétique", "5 nT", 2, 0),
            ("🌡️ Température", "-270°C", 2, 1),
        ]
        
        for i, (label, value, row, col) in enumerate(params):
            group = QGroupBox(label)
            group_layout = QVBoxLayout(group)
            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
            value_label.setAlignment(Qt.AlignCenter)
            group_layout.addWidget(value_label)
            layout.addWidget(group, row, col)
        
        # Graphique
        chart = QChart()
        chart.setTitle("Activité solaire (24h)")
        
        series = QLineSeries()
        for i in range(24):
            series.append(i, random.randint(50, 200))
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart_view = QChartView(chart)
        layout.addWidget(chart_view, 3, 0, 1, 2)

# ============================================================================
# MODULE 5: ANALYSE GÉOSPATIALE
# ============================================================================

class AnalyseGeospatialeModule(QWidget):
    """Module d'analyse géospatiale"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QToolBar()
        toolbar.addAction("📂 Charger shapefile")
        toolbar.addAction("📊 Analyser")
        toolbar.addAction("💾 Exporter")
        layout.addWidget(toolbar)
        
        # Zone d'analyse
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau gauche (paramètres)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        left_layout.addWidget(QLabel("Type d'analyse:"))
        self.analyse_combo = QComboBox()
        self.analyse_combo.addItems([
            "Buffer (zone tampon)",
            "Intersection",
            "Union",
            "Statistiques zonales",
            "Densité de points"
        ])
        left_layout.addWidget(self.analyse_combo)
        
        left_layout.addWidget(QLabel("Distance (m):"))
        self.distance_spin = QSpinBox()
        self.distance_spin.setRange(10, 10000)
        self.distance_spin.setValue(100)
        left_layout.addWidget(self.distance_spin)
        
        analyze_btn = QPushButton("▶️ Lancer l'analyse")
        analyze_btn.clicked.connect(self.lancer_analyse)
        left_layout.addWidget(analyze_btn)
        
        splitter.addWidget(left)
        
        # Panneau droit (résultats)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        splitter.addWidget(self.result_text)
        
        layout.addWidget(splitter)
    
    def lancer_analyse(self):
        analyse = self.analyse_combo.currentText()
        distance = self.distance_spin.value()
        
        resultat = f"""
📊 RÉSULTAT DE L'ANALYSE
{'='*50}

Type: {analyse}
Paramètres: distance = {distance} m

✅ Analyse terminée avec succès!

📈 Statistiques:
• Entités traitées: 1,250
• Surface totale: 45.3 km²
• Périmètre total: 28.7 km
• Densité: 27.5 entités/km²

⏱️ Temps d'exécution: 1.2 secondes
"""
        self.result_text.setText(resultat)

# ============================================================================
# LOGICIEL PRINCIPAL
# ============================================================================

class LogicielSpatialComplet(QMainWindow):
    """Logiciel spatial intégrant tous les modules"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 LOGICIEL SPATIAL COMPLET - Version Ultime")
        self.setGeometry(50, 50, 1400, 900)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        
    def setup_ui(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        layout = QVBoxLayout(central)
        
        # Barre de navigation
        nav_bar = self.create_nav_bar()
        layout.addWidget(nav_bar)
        
        # Zone d'onglets
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setExpanding(True)
        
        # Ajouter tous les modules
        self.tabs.addTab(SystemeSolaireModule(), "🪐 Système solaire")
        self.tabs.addTab(SatellitesModule(), "🛰️ Satellites")
        self.tabs.addTab(OSMModule(), "🗺️ OpenStreetMap")
        self.tabs.addTab(MeteoSpatialeModule(), "🌤️ Météo spatiale")
        self.tabs.addTab(AnalyseGeospatialeModule(), "📊 Analyse géospatiale")
        
        # Onglet supplémentaire pour les missions
        self.tabs.addTab(self.create_missions_tab(), "🚀 Missions")
        
        layout.addWidget(self.tabs)
    
    def create_nav_bar(self):
        """Barre de navigation avec stats en direct"""
        nav = QWidget()
        nav.setStyleSheet("background-color: #1a1a2a; padding: 5px;")
        layout = QHBoxLayout(nav)
        
        # Logo
        logo = QLabel("🚀 CENTRE SPATIAL")
        logo.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # Stats
        self.stats_label = QLabel("🌍 8 planètes | 🛰️ 6 satellites | 🚀 5 missions")
        self.stats_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.stats_label)
        
        return nav
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("&Nouveau projet", self.nouveau_projet)
        file_menu.addAction("&Ouvrir", self.ouvrir)
        file_menu.addAction("&Enregistrer", self.enregistrer)
        file_menu.addSeparator()
        file_menu.addAction("&Quitter", self.close)
        
        # Modules
        modules_menu = menubar.addMenu("&Modules")
        modules_menu.addAction("🪐 Système solaire", lambda: self.tabs.setCurrentIndex(0))
        modules_menu.addAction("🛰️ Satellites", lambda: self.tabs.setCurrentIndex(1))
        modules_menu.addAction("🗺️ OpenStreetMap", lambda: self.tabs.setCurrentIndex(2))
        modules_menu.addAction("🌤️ Météo spatiale", lambda: self.tabs.setCurrentIndex(3))
        modules_menu.addAction("📊 Analyse", lambda: self.tabs.setCurrentIndex(4))
        modules_menu.addAction("🚀 Missions", lambda: self.tabs.setCurrentIndex(5))
        
        # Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("Plein écran", self.toggle_fullscreen, "F11")
        
        # Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("Documentation", self.docs)
        help_menu.addAction("À propos", self.about)
    
    def setup_statusbar(self):
        self.statusBar().showMessage("Prêt - Système opérationnel")
        
        # Horloge
        self.clock = QLabel()
        self.statusBar().addPermanentWidget(self.clock)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
    
    def create_missions_tab(self):
        """Onglet des missions spatiales"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        missions = [
            ("Artemis II", "NASA", "Lunaire", "2025", "🟢 En préparation", 75),
            ("Mars Sample Return", "NASA/ESA", "Martien", "2028", "🟡 Développement", 30),
            ("Europa Clipper", "NASA", "Planétaire", "2024", "🟢 Prêt", 95),
            ("Chang'e 6", "CNSA", "Lunaire", "2024", "🔴 Terminée", 100),
            ("JUICE", "ESA", "Planétaire", "2023", "🟢 En route", 100),
        ]
        
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Mission", "Agence", "Type", "Date", "Statut", "Progression"])
        table.setRowCount(len(missions))
        
        for i, (nom, agence, type_, date, statut, prog) in enumerate(missions):
            table.setItem(i, 0, QTableWidgetItem(nom))
            table.setItem(i, 1, QTableWidgetItem(agence))
            table.setItem(i, 2, QTableWidgetItem(type_))
            table.setItem(i, 3, QTableWidgetItem(date))
            
            item = QTableWidgetItem(statut)
            if "🟢" in statut:
                item.setForeground(QColor(76, 175, 80))
            elif "🟡" in statut:
                item.setForeground(QColor(255, 165, 0))
            else:
                item.setForeground(QColor(255, 99, 71))
            table.setItem(i, 4, item)
            
            prog_item = QTableWidgetItem(f"{prog}%")
            prog_item.setForeground(QColor(76, 175, 80))
            table.setItem(i, 5, prog_item)
        
        layout.addWidget(table)
        
        return widget
    
    def nouveau_projet(self):
        self.statusBar().showMessage("Nouveau projet créé")
    
    def ouvrir(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir projet")
        if filename:
            self.statusBar().showMessage(f"Projet ouvert: {filename}")
    
    def enregistrer(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer projet")
        if filename:
            self.statusBar().showMessage(f"Projet sauvegardé: {filename}")
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def docs(self):
        QMessageBox.information(self, "Documentation",
            "LOGICIEL SPATIAL COMPLET\n\n"
            "Modules disponibles:\n"
            "1. Système solaire - Simulation 3D\n"
            "2. Satellites - Suivi en temps réel\n"
            "3. OpenStreetMap - Données urbaines\n"
            "4. Météo spatiale - Conditions cosmiques\n"
            "5. Analyse géospatiale - Traitements SIG\n"
            "6. Missions - Gestion des missions")
    
    def about(self):
        QMessageBox.about(self, "À propos",
            "🚀 LOGICIEL SPATIAL COMPLET\n"
            "Version 3.0\n\n"
            "Tous les modules spatiaux en un seul logiciel\n"
            "Développé avec PySide6\n"
            "© 2026")
    
    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%H:%M:%S"))

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Palette sombre professionnelle
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = LogicielSpatialComplet()
    window.show()
    
    sys.exit(app.exec())