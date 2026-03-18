# main_window.py
import sys
import math
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Logiciel Spatial Professionnel v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Données
        self.planetes = self.charger_donnees_planetes()
        self.satellites = self.charger_donnees_satellites()
        
        # Interface
        self.setup_ui()
        self.creer_menu()
        self.creer_barre_outils()
        self.creer_barre_statut()
        
    def charger_donnees_planetes(self):
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
    
    def charger_donnees_satellites(self):
        return [
            {"nom": "ISS", "type": "Station", "pays": "International", "annee": 1998},
            {"nom": "Hubble", "type": "Télescope", "pays": "USA", "annee": 1990},
            {"nom": "James Webb", "type": "Télescope", "pays": "USA", "annee": 2021},
            {"nom": "Sentinel-2", "type": "Observation", "pays": "Europe", "annee": 2015}
        ]
    
    def setup_ui(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        layout = QHBoxLayout(central)
        
        # Panneau gauche (outils)
        self.creer_panneau_gauche(layout)
        
        # Zone centrale (visualisation)
        self.creer_zone_centrale(layout)
        
        # Panneau droit (propriétés)
        self.creer_panneau_droit(layout)
    
    def creer_panneau_gauche(self, parent_layout):
        panel = QDockWidget("🛸 Outils", self)
        panel.setAllowedAreas(Qt.LeftDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Planètes
        planet_tab = QWidget()
        p_layout = QVBoxLayout(planet_tab)
        
        # Liste des planètes
        self.planet_list = QListWidget()
        for p in self.planetes:
            item = QListWidgetItem(f"🪐 {p['nom']}")
            item.setData(Qt.UserRole, p)
            self.planet_list.addItem(item)
        self.planet_list.currentItemChanged.connect(self.on_planet_selected)
        p_layout.addWidget(QLabel("Planètes:"))
        p_layout.addWidget(self.planet_list)
        
        # Boutons planètes
        btn_frame = QWidget()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.addWidget(QPushButton("📊 Détails"))
        btn_layout.addWidget(QPushButton("🔄 Orbite"))
        btn_layout.addWidget(QPushButton("🌙 Lunes"))
        p_layout.addWidget(btn_frame)
        
        tabs.addTab(planet_tab, "🪐 Planètes")
        
        # Onglet Satellites
        sat_tab = QWidget()
        s_layout = QVBoxLayout(sat_tab)
        
        self.satellite_list = QListWidget()
        for s in self.satellites:
            self.satellite_list.addItem(f"📡 {s['nom']} ({s['pays']})")
        s_layout.addWidget(QLabel("Satellites artificiels:"))
        s_layout.addWidget(self.satellite_list)
        
        # Boutons satellites
        sat_btn_frame = QWidget()
        sat_btn_layout = QHBoxLayout(sat_btn_frame)
        sat_btn_layout.addWidget(QPushButton("📍 Position"))
        sat_btn_layout.addWidget(QPushButton("🛰️ Trajectoire"))
        s_layout.addWidget(sat_btn_frame)
        
        tabs.addTab(sat_tab, "📡 Satellites")
        
        # Onglet Missions
        mission_tab = QWidget()
        m_layout = QVBoxLayout(mission_tab)
        
        missions = [
            "🚀 Apollo 11 (1969) - Premier pas sur la Lune",
            "🚀 Voyager 1 (1977) - Exploration interstellaire",
            "🚀 ISS (1998) - Station spatiale",
            "🚀 Perseverance (2020) - Rover martien",
            "🚀 Artemis (2025) - Retour sur la Lune"
        ]
        
        for mission in missions:
            m_layout.addWidget(QCheckBox(mission))
        
        tabs.addTab(mission_tab, "🚀 Missions")
        
        # Onglet Calculs
        calc_tab = QWidget()
        c_layout = QVBoxLayout(calc_tab)
        
        c_layout.addWidget(QLabel("Planète départ:"))
        self.depart_combo = QComboBox()
        self.depart_combo.addItems([p["nom"] for p in self.planetes])
        c_layout.addWidget(self.depart_combo)
        
        c_layout.addWidget(QLabel("Planète arrivée:"))
        self.arrivee_combo = QComboBox()
        self.arrivee_combo.addItems([p["nom"] for p in self.planetes])
        self.arrivee_combo.setCurrentText("Mars")
        c_layout.addWidget(self.arrivee_combo)
        
        c_layout.addWidget(QLabel("Vitesse (km/s):"))
        self.vitesse_spin = QSpinBox()
        self.vitesse_spin.setRange(1000, 200000)
        self.vitesse_spin.setValue(50000)
        self.vitesse_spin.setSingleStep(1000)
        self.vitesse_spin.setSuffix(" km/s")
        c_layout.addWidget(self.vitesse_spin)
        
        btn_calculer = QPushButton("🚀 Calculer distance")
        btn_calculer.clicked.connect(self.calculer_distance)
        c_layout.addWidget(btn_calculer)
        
        btn_temps = QPushButton("⏱️ Calculer temps")
        btn_temps.clicked.connect(self.calculer_temps)
        c_layout.addWidget(btn_temps)
        
        self.resultat_label = QLabel("Résultats...")
        self.resultat_label.setWordWrap(True)
        self.resultat_label.setStyleSheet("background: #1a1a2a; color: #00ff00; padding: 10px;")
        c_layout.addWidget(self.resultat_label)
        
        tabs.addTab(calc_tab, "🧮 Calculs")
        
        layout.addWidget(tabs)
        
        panel.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, panel)
    
    def creer_zone_centrale(self, parent_layout):
        # Zone de visualisation avec onglets
        tabs = QTabWidget()
        
        # Vue 2D
        vue2d = QWidget()
        v2_layout = QVBoxLayout(vue2d)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        v2_layout.addWidget(self.view)
        
        # Barre d'outils de la vue
        toolbar = QToolBar()
        toolbar.addAction(QIcon(), "🔍 Zoom +")
        toolbar.addAction(QIcon(), "🔍 Zoom -")
        toolbar.addAction(QIcon(), "🔄 Réinitialiser")
        v2_layout.addWidget(toolbar)
        
        tabs.addTab(vue2d, "🪐 Vue 2D")
        
        # Vue 3D (simulée)
        vue3d = QLabel("Vue 3D (en développement)")
        vue3d.setAlignment(Qt.AlignCenter)
        vue3d.setStyleSheet("background: #000000; color: white; font-size: 20px;")
        tabs.addTab(vue3d, "🌍 Vue 3D")
        
        # Graphiques
        chart_view = self.creer_graphique()
        tabs.addTab(chart_view, "📊 Graphiques")
        
        parent_layout.addWidget(tabs)
        
        # Dessiner le système
        self.dessiner_systeme()
    
    def creer_graphique(self):
        # Créer un graphique des distances
        chart = QChart()
        chart.setTitle("Distances des planètes au Soleil")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QBarSeries()
        
        for p in self.planetes:
            bar_set = QBarSet(p["nom"])
            bar_set.append(p["distance"])
            series.append(bar_set)
        
        chart.addSeries(series)
        
        chart.createDefaultAxes()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def creer_panneau_droit(self, parent_layout):
        panel = QDockWidget("📋 Propriétés", self)
        panel.setAllowedAreas(Qt.RightDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Informations détaillées
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background: #f5f5f5;")
        layout.addWidget(self.info_text)
        
        # Statistiques
        stats_group = QGroupBox("Statistiques")
        stats_layout = QFormLayout(stats_group)
        stats_layout.addRow("Planètes:", QLabel(str(len(self.planetes))))
        stats_layout.addRow("Satellites:", QLabel(str(len(self.satellites))))
        stats_layout.addRow("Missions:", QLabel("5 actives"))
        layout.addWidget(stats_group)
        
        # Barre de progression
        progress = QProgressBar()
        progress.setValue(75)
        progress.setFormat("Mission en cours: %p%")
        layout.addWidget(QLabel("Progression Artemis:"))
        layout.addWidget(progress)
        
        panel.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, panel)
    
    def creer_menu(self):
        menubar = self.menuBar()
        
        # Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("&Nouveau projet", self.nouveau_projet, "Ctrl+N")
        file_menu.addAction("&Ouvrir", self.ouvrir_fichier, "Ctrl+O")
        file_menu.addAction("&Enregistrer", self.enregistrer, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("&Quitter", self.close, "Ctrl+Q")
        
        # Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("Plein écran", self.toggle_fullscreen, "F11")
        view_menu.addSeparator()
        
        # Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("Documentation", self.show_docs)
        help_menu.addAction("À propos", self.show_about)
    
    def creer_barre_outils(self):
        toolbar = self.addToolBar("Outils")
        toolbar.addAction("🪐 Planètes")
        toolbar.addAction("📡 Satellites")
        toolbar.addAction("🚀 Missions")
        toolbar.addSeparator()
        toolbar.addAction("🔍 Rechercher")
    
    def creer_barre_statut(self):
        self.statusBar().showMessage("Prêt")
        
        # Horloge
        self.clock_label = QLabel()
        self.statusBar().addPermanentWidget(self.clock_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
    
    def dessiner_systeme(self):
        self.scene.clear()
        
        # Soleil
        soleil = self.scene.addEllipse(-20, -20, 40, 40, QPen(Qt.yellow), QBrush(Qt.yellow))
        soleil.setPos(300, 250)
        self.scene.addText("☀️ Soleil").setPos(280, 200)
        
        # Planètes
        echelle = 0.3
        for i, p in enumerate(self.planetes):
            rayon = p["distance"] * echelle
            angle = i * 0.5
            
            # Orbite
            self.scene.addEllipse(300 - rayon, 250 - rayon, rayon*2, rayon*2, 
                                  QPen(QColor("#333366")))
            
            # Planète
            x = 300 + rayon * math.cos(angle)
            y = 250 + rayon * math.sin(angle)
            
            couleur = QColor(p["couleur"])
            planet = self.scene.addEllipse(-5, -5, 10, 10, QPen(Qt.white), QBrush(couleur))
            planet.setPos(x, y)
            
            # Nom
            text = self.scene.addText(p["nom"])
            text.setPos(x - 20, y - 20)
    
    def calculer_distance(self):
        depart = self.depart_combo.currentText()
        arrivee = self.arrivee_combo.currentText()
        
        p1 = next(p for p in self.planetes if p["nom"] == depart)
        p2 = next(p for p in self.planetes if p["nom"] == arrivee)
        
        distance = abs(p2["distance"] - p1["distance"])
        distance_min = distance
        distance_max = p1["distance"] + p2["distance"]
        
        self.resultat_label.setText(
            f"🌍 DISTANCE {depart} → {arrivee}\n\n"
            f"Distance moyenne: {distance:.1f} M km\n"
            f"({distance*1e6:.0f} km)\n\n"
            f"Minimale: {distance_min:.1f} M km\n"
            f"Maximale: {distance_max:.1f} M km"
        )
        
        self.statusBar().showMessage(f"Distance calculée: {distance:.1f} M km")
    
    def calculer_temps(self):
        depart = self.depart_combo.currentText()
        arrivee = self.arrivee_combo.currentText()
        vitesse = self.vitesse_spin.value()
        
        p1 = next(p for p in self.planetes if p["nom"] == depart)
        p2 = next(p for p in self.planetes if p["nom"] == arrivee)
        
        distance_km = abs(p2["distance"] - p1["distance"]) * 1e6
        temps_s = distance_km / vitesse
        
        heures = temps_s / 3600
        jours = heures / 24
        mois = jours / 30.44
        annees = jours / 365.25
        
        self.resultat_label.setText(
            f"⏱️ TEMPS DE VOYAGE\n\n"
            f"Distance: {distance_km/1e6:.1f} M km\n"
            f"Vitesse: {vitesse:,} km/s\n\n"
            f"Temps: {temps_s:.1f} s\n"
            f"Soit {heures:.1f} heures\n"
            f"Soit {jours:.1f} jours\n"
            f"Soit {mois:.1f} mois\n"
            f"Soit {annees:.2f} ans"
        )
    
    def on_planet_selected(self, current, previous):
        if current:
            p = current.data(Qt.UserRole)
            self.info_text.setText(
                f"🪐 {p['nom']}\n\n"
                f"Distance du Soleil: {p['distance']} M km\n"
                f"Diamètre: {p['diametre']} km\n"
                f"Lunes: {p['lunes']}\n"
                f"Couleur: {p['couleur']}"
            )
    
    def nouveau_projet(self):
        self.statusBar().showMessage("Nouveau projet créé")
    
    def ouvrir_fichier(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir fichier")
        if filename:
            self.statusBar().showMessage(f"Fichier ouvert: {filename}")
    
    def enregistrer(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer")
        if filename:
            self.statusBar().showMessage(f"Fichier enregistré: {filename}")
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation", 
                               "Documentation disponible sur GitHub\n\n"
                               "https://github.com/votre-projet")
    
    def show_about(self):
        QMessageBox.about(self, "À propos", 
                         "🚀 Logiciel Spatial Professionnel\n"
                         "Version 1.0\n\n"
                         "Développé avec PySide6\n"
                         "© 2026")
    
    def update_clock(self):
        from datetime import datetime
        self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())