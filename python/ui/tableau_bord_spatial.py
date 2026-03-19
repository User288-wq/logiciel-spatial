import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import math

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class SpatialDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Tableau de Bord Spatial - Centre de Contrôle")
        self.setGeometry(100, 100, 1400, 900)
        
        # Données simulées
        self.generer_donnees()
        
        # Interface
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Timer pour mise à jour en temps réel
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_realtime_data)
        self.timer.start(1000)  # Mise à jour chaque seconde
        
    def generer_donnees(self):
        """Génère des données spatiales simulées"""
        
        # Satellites en orbite
        self.satellites = [
            {"nom": "ISS", "type": "Station habitée", "pays": "International", 
             "altitude": 408, "vitesse": 7.66, "inclinaison": 51.64,
             "position": [random.uniform(-180, 180), random.uniform(-90, 90)]},
            {"nom": "Hubble", "type": "Télescope", "pays": "USA", 
             "altitude": 540, "vitesse": 7.59, "inclinaison": 28.47,
             "position": [random.uniform(-180, 180), random.uniform(-90, 90)]},
            {"nom": "Sentinel-2", "type": "Observation Terre", "pays": "Europe", 
             "altitude": 786, "vitesse": 7.45, "inclinaison": 98.5,
             "position": [random.uniform(-180, 180), random.uniform(-90, 90)]},
            {"nom": "GPS BIIF-2", "type": "Navigation", "pays": "USA", 
             "altitude": 20200, "vitesse": 3.87, "inclinaison": 55,
             "position": [random.uniform(-180, 180), random.uniform(-90, 90)]},
            {"nom": "Tiangong", "type": "Station habitée", "pays": "Chine", 
             "altitude": 340, "vitesse": 7.68, "inclinaison": 41.5,
             "position": [random.uniform(-180, 180), random.uniform(-90, 90)]},
        ]
        
        # Missions spatiales
        self.missions = [
            {"nom": "Artemis II", "agence": "NASA", "type": "Lunaire", 
             "date": "2025-09", "statut": "Préparation", "progression": 75},
            {"nom": "Chang'e 6", "agence": "CNSA", "type": "Lunaire", 
             "date": "2024-05", "statut": "En cours", "progression": 100},
            {"nom": "Mars Sample Return", "agence": "NASA/ESA", "type": "Martien", 
             "date": "2028", "statut": "Développement", "progression": 30},
            {"nom": "Europa Clipper", "agence": "NASA", "type": "Planétaire", 
             "date": "2024-10", "statut": "Prêt", "progression": 95},
            {"nom": "JUICE", "agence": "ESA", "type": "Planétaire", 
             "date": "2023-04", "statut": "En route", "progression": 100},
        ]
        
        # Planètes (données astronomiques)
        self.planetes = [
            {"nom": "Mercure", "distance_soleil": 57.9, "diametre": 4879, 
             "lunes": 0, "periode": 88, "couleur": "#a5a5a5"},
            {"nom": "Vénus", "distance_soleil": 108.2, "diametre": 12104, 
             "lunes": 0, "periode": 225, "couleur": "#ffb347"},
            {"nom": "Terre", "distance_soleil": 149.6, "diametre": 12742, 
             "lunes": 1, "periode": 365, "couleur": "#4a90e2"},
            {"nom": "Mars", "distance_soleil": 227.9, "diametre": 6779, 
             "lunes": 2, "periode": 687, "couleur": "#e27a4a"},
            {"nom": "Jupiter", "distance_soleil": 778.5, "diametre": 139820, 
             "lunes": 79, "periode": 4333, "couleur": "#d98c4a"},
        ]
        
        # Données météo spatiale
        self.meteo_spatiale = {
            "vent_solaire": random.uniform(300, 800),
            "indice_Kp": random.randint(0, 9),
            "flux_solaire": random.uniform(70, 250),
            "protons_energetiques": random.choice(["Faible", "Modéré", "Élevé"]),
        }
        
    def setup_ui(self):
        """Configure l'interface utilisateur avec onglets"""
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QVBoxLayout(central)
        
        # Barre de navigation
        nav_bar = self.create_nav_bar()
        main_layout.addWidget(nav_bar)
        
        # Zone de contenu avec onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabBar().setExpanding(True)
        
        # Création des onglets
        self.tab_widget.addTab(self.create_dashboard_tab(), "📊 Tableau de bord")
        self.tab_widget.addTab(self.create_satellites_tab(), "🛰️ Satellites")
        self.tab_widget.addTab(self.create_missions_tab(), "🚀 Missions")
        self.tab_widget.addTab(self.create_planetes_tab(), "🪐 Planètes")
        self.tab_widget.addTab(self.create_meteo_tab(), "🌤️ Météo spatiale")
        self.tab_widget.addTab(self.create_carte_tab(), "🗺️ Carte du monde")
        
        main_layout.addWidget(self.tab_widget)
        
    def create_nav_bar(self):
        """Crée une barre de navigation avec indicateurs"""
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo / Titre
        title = QLabel("🚀 CENTRE DE CONTRÔLE SPATIAL")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #4CAF50;
            padding: 5px;
        """)
        nav_layout.addWidget(title)
        
        nav_layout.addStretch()
        
        # Indicateurs en temps réel
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #888888;")
        nav_layout.addWidget(self.time_label)
        
        self.sat_count_label = QLabel(f"🛰️ {len(self.satellites)} actifs")
        self.sat_count_label.setStyleSheet("color: #4CAF50; margin-right: 15px;")
        nav_layout.addWidget(self.sat_count_label)
        
        self.mission_count_label = QLabel(f"🚀 {len(self.missions)} missions")
        self.mission_count_label.setStyleSheet("color: #FFA500; margin-right: 15px;")
        nav_layout.addWidget(self.mission_count_label)
        
        return nav_bar
    
    def create_dashboard_tab(self):
        """Onglet principal avec vue d'ensemble"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Panneau gauche (statistiques)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Cartes statistiques
        stats_group = QGroupBox("📈 Statistiques en direct")
        stats_layout = QGridLayout(stats_group)
        
        # Création de cartes de statistiques
        self.create_stat_card(stats_layout, 0, 0, "🛰️ Satellites", str(len(self.satellites)), "#4CAF50")
        self.create_stat_card(stats_layout, 0, 1, " Missions", str(len(self.missions)), "#FFA500")
        self.create_stat_card(stats_layout, 1, 0, "🌍 Pays", "12", "#2196F3")
        self.create_stat_card(stats_layout, 1, 1, "📡 Orbite basse", "150+", "#9C27B0")
        
        left_layout.addWidget(stats_group)
        
        # Dernières actualités
        news_group = QGroupBox("📰 Dernières actualités spatiales")
        news_layout = QVBoxLayout(news_group)
        
        news = [
            "🚀 Artemis II: Préparatifs en cours",
            "🛰️ Nouveau satellite météo lancé",
            "🔭 Découverte d'exoplanètes",
            "🌕 Mission lunaire chinoise réussie",
        ]
        
        for item in news:
            label = QLabel(f"• {item}")
            label.setStyleSheet("padding: 5px;")
            news_layout.addWidget(label)
        
        left_layout.addWidget(news_group)
        
        # Prochains lancements
        launches_group = QGroupBox("📅 Prochains lancements")
        launches_layout = QVBoxLayout(launches_group)
        
        launches = [
            "15 Avril 2026 - Falcon 9 (Starlink)",
            "22 Avril 2026 - Soyouz (Progress)",
            "30 Avril 2026 - Ariane 6 (Démo)",
        ]
        
        for item in launches:
            label = QLabel(f"⏰ {item}")
            label.setStyleSheet("padding: 3px; color: #FFA500;")
            launches_layout.addWidget(label)
        
        left_layout.addWidget(launches_group)
        
        left_layout.addStretch()
        
        # Panneau droit (graphiques)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Graphique des missions
        chart_group = QGroupBox("📊 Répartition des missions")
        chart_layout = QVBoxLayout(chart_group)
        
        chart = self.create_mission_chart()
        chart_layout.addWidget(chart)
        
        right_layout.addWidget(chart_group)
        
        # Graphique des satellites par pays
        country_chart_group = QGroupBox("🌍 Satellites par pays")
        country_chart_layout = QVBoxLayout(country_chart_group)
        
        country_chart = self.create_country_chart()
        country_chart_layout.addWidget(country_chart)
        
        right_layout.addWidget(country_chart_group)
        
        # Assemblage
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        return tab
    
    def create_stat_card(self, layout, row, col, title, value, color):
        """Crée une carte de statistique"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}10;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        card_layout.addWidget(value_label)
        
        layout.addWidget(card, row, col)
    
    def create_mission_chart(self):
        """Crée un graphique des missions"""
        chart = QChart()
        chart.setTitle("Missions spatiales par type")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        
        series = QPieSeries()
        series.append("Lunaire", 3)
        series.append("Martien", 2)
        series.append("Planétaire", 4)
        series.append("Observation", 6)
        
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignRight)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def create_country_chart(self):
        """Crée un graphique des satellites par pays"""
        chart = QChart()
        chart.setTitle("Satellites par pays")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        
        series = QBarSeries()
        
        usa_set = QBarSet("USA")
        europe_set = QBarSet("Europe")
        china_set = QBarSet("Chine")
        russia_set = QBarSet("Russie")
        
        usa_set.append(120)
        europe_set.append(80)
        china_set.append(60)
        russia_set.append(50)
        
        series.append(usa_set)
        series.append(europe_set)
        series.append(china_set)
        series.append(russia_set)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def create_satellites_tab(self):
        """Onglet de gestion des satellites"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barre d'outils
        toolbar = QToolBar()
        toolbar.addAction(QIcon(), "➕ Ajouter")
        toolbar.addAction(QIcon(), "✏️ Modifier")
        toolbar.addAction(QIcon(), "🗑️ Supprimer")
        toolbar.addSeparator()
        toolbar.addAction(QIcon(), "🔄 Actualiser")
        toolbar.addAction(QIcon(), "📊 Statistiques")
        
        layout.addWidget(toolbar)
        
        # Tableau des satellites
        self.satellite_table = QTableWidget()
        self.satellite_table.setColumnCount(7)
        self.satellite_table.setHorizontalHeaderLabels([
            "Nom", "Type", "Pays", "Altitude (km)", 
            "Vitesse (km/s)", "Inclinaison (°)", "Statut"
        ])
        
        self.update_satellite_table()
        layout.addWidget(self.satellite_table)
        
        # Informations détaillées
        info_group = QGroupBox("📡 Informations détaillées")
        info_layout = QHBoxLayout(info_group)
        
        self.sat_info_text = QTextEdit()
        self.sat_info_text.setReadOnly(True)
        self.sat_info_text.setMaximumHeight(100)
        info_layout.addWidget(self.sat_info_text)
        
        layout.addWidget(info_group)
        
        # Connexion de la sélection
        self.satellite_table.itemSelectionChanged.connect(self.show_satellite_info)
        
        return tab
    
    def update_satellite_table(self):
        """Met à jour le tableau des satellites"""
        self.satellite_table.setRowCount(len(self.satellites))
        
        for i, sat in enumerate(self.satellites):
            self.satellite_table.setItem(i, 0, QTableWidgetItem(sat["nom"]))
            self.satellite_table.setItem(i, 1, QTableWidgetItem(sat["type"]))
            self.satellite_table.setItem(i, 2, QTableWidgetItem(sat["pays"]))
            self.satellite_table.setItem(i, 3, QTableWidgetItem(str(sat["altitude"])))
            self.satellite_table.setItem(i, 4, QTableWidgetItem(str(sat["vitesse"])))
            self.satellite_table.setItem(i, 5, QTableWidgetItem(str(sat["inclinaison"])))
            
            # Statut (couleur)
            status_item = QTableWidgetItem("Actif")
            if random.random() > 0.8:
                status_item = QTableWidgetItem("Maintenance")
                status_item.setForeground(QColor(255, 165, 0))
            else:
                status_item.setForeground(QColor(76, 175, 80))
            
            self.satellite_table.setItem(i, 6, status_item)
    
    def show_satellite_info(self):
        """Affiche les infos détaillées du satellite sélectionné"""
        current_row = self.satellite_table.currentRow()
        if current_row >= 0:
            sat = self.satellites[current_row]
            
            info = f"""
            📡 Satellite: {sat['nom']}
            Type: {sat['type']}
            Pays: {sat['pays']}
            
            Paramètres orbitaux:
            • Altitude: {sat['altitude']} km
            • Vitesse: {sat['vitesse']} km/s
            • Inclinaison: {sat['inclinaison']}°
            
            Position actuelle:
            • Latitude: {sat['position'][1]:.2f}°
            • Longitude: {sat['position'][0]:.2f}°
            
            Prochain passage: {datetime.now() + timedelta(hours=random.randint(1, 12))}
            """
            
            self.sat_info_text.setText(info)
    
    def create_missions_tab(self):
        """Onglet des missions spatiales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filtres
        filter_bar = QWidget()
        filter_layout = QHBoxLayout(filter_bar)
        
        filter_layout.addWidget(QLabel("Filtrer par:"))
        self.mission_filter = QComboBox()
        self.mission_filter.addItems(["Toutes", "En cours", "Préparation", "Terminées"])
        filter_layout.addWidget(self.mission_filter)
        
        filter_layout.addStretch()
        
        search_label = QLabel("Rechercher:")
        filter_layout.addWidget(search_label)
        
        self.mission_search = QLineEdit()
        self.mission_search.setPlaceholderText("Nom de mission...")
        filter_layout.addWidget(self.mission_search)
        
        layout.addWidget(filter_bar)
        
        # Tableau des missions
        self.mission_table = QTableWidget()
        self.mission_table.setColumnCount(6)
        self.mission_table.setHorizontalHeaderLabels([
            "Nom", "Agence", "Type", "Date", "Statut", "Progression"
        ])
        
        self.update_mission_table()
        layout.addWidget(self.mission_table)
        
        # Barre de progression globale
        progress_group = QGroupBox("📊 Progression globale des missions")
        progress_layout = QVBoxLayout(progress_group)
        
        self.global_progress = QProgressBar()
        self.global_progress.setValue(65)
        self.global_progress.setFormat("65% - Objectifs atteints")
        progress_layout.addWidget(self.global_progress)
        
        layout.addWidget(progress_group)
        
        return tab
    
    def update_mission_table(self):
        """Met à jour le tableau des missions"""
        self.mission_table.setRowCount(len(self.missions))
        
        for i, mission in enumerate(self.missions):
            self.mission_table.setItem(i, 0, QTableWidgetItem(mission["nom"]))
            self.mission_table.setItem(i, 1, QTableWidgetItem(mission["agence"]))
            self.mission_table.setItem(i, 2, QTableWidgetItem(mission["type"]))
            self.mission_table.setItem(i, 3, QTableWidgetItem(mission["date"]))
            
            # Statut avec couleur
            status_item = QTableWidgetItem(mission["statut"])
            if mission["statut"] == "En cours":
                status_item.setForeground(QColor(76, 175, 80))
            elif mission["statut"] == "Préparation":
                status_item.setForeground(QColor(255, 165, 0))
            elif mission["statut"] == "Développement":
                status_item.setForeground(QColor(33, 150, 243))
            else:
                status_item.setForeground(QColor(255, 255, 255))
            
            self.mission_table.setItem(i, 4, status_item)
            
            # Progression avec barre
            progress_item = QTableWidgetItem(f"{mission['progression']}%")
            progress_item.setForeground(QColor(76, 175, 80))
            self.mission_table.setItem(i, 5, progress_item)
    
    def create_planetes_tab(self):
        """Onglet des planètes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sélecteur de planète
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Sélectionner une planète:"))
        
        self.planet_combo = QComboBox()
        self.planet_combo.addItems([p["nom"] for p in self.planetes])
        self.planet_combo.currentTextChanged.connect(self.show_planet_info)
        selector_layout.addWidget(self.planet_combo)
        
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Informations sur la planète
        info_group = QGroupBox("🪐 Informations planétaires")
        info_layout = QHBoxLayout(info_group)
        
        # Texte des infos
        self.planet_info = QTextEdit()
        self.planet_info.setReadOnly(True)
        self.planet_info.setMaximumWidth(400)
        info_layout.addWidget(self.planet_info)
        
        # Graphique de comparaison
        chart = self.create_planet_chart()
        info_layout.addWidget(chart)
        
        layout.addWidget(info_group)
        
        # Simulation d'orbite
        orbit_group = QGroupBox("🔄 Simulation d'orbite")
        orbit_layout = QVBoxLayout(orbit_group)
        
        # Canvas pour la simulation (simplifié)
        orbit_canvas = QLabel("🎨 Visualisation orbitale (simulation)")
        orbit_canvas.setAlignment(Qt.AlignCenter)
        orbit_canvas.setMinimumHeight(200)
        orbit_canvas.setStyleSheet("""
            background-color: #0a0a2a;
            color: white;
            border: 1px solid #333366;
        """)
        orbit_layout.addWidget(orbit_canvas)
        
        layout.addWidget(orbit_group)
        
        # Afficher la première planète
        self.show_planet_info(self.planetes[0]["nom"])
        
        return tab
    
    def show_planet_info(self, planet_name):
        """Affiche les informations d'une planète"""
        planet = next(p for p in self.planetes if p["nom"] == planet_name)
        
        info = f"""
        🌍 PLANÈTE: {planet['nom']}
        ===========================
        
        📏 Caractéristiques physiques:
        • Diamètre: {planet['diametre']} km
        • Distance du Soleil: {planet['distance_soleil']} M km
        • Période orbitale: {planet['periode']} jours
        • Lunes: {planet['lunes']}
        
        ⚡ Données orbitales:
        • Vitesse orbitale moyenne: {random.uniform(5, 50):.2f} km/s
        • Inclinaison: {random.uniform(0, 10):.2f}°
        • Excentricité: {random.uniform(0, 0.2):.3f}
        
        🔭 Observation:
        • Magnitude apparente: {random.uniform(-5, 5):.1f}
        • Distance actuelle de la Terre: {random.uniform(50, 4000):.1f} M km
        • Prochaine opposition: {datetime.now() + timedelta(days=random.randint(30, 365))}
        """
        
        self.planet_info.setText(info)
    
    def create_planet_chart(self):
        """Crée un graphique comparatif des planètes"""
        chart = QChart()
        chart.setTitle("Comparaison des distances au Soleil")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        
        series = QBarSeries()
        
        for planet in self.planetes:
            bar_set = QBarSet(planet["nom"])
            bar_set.append(planet["distance_soleil"])
            bar_set.setColor(QColor(planet["couleur"]))
            series.append(bar_set)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def create_meteo_tab(self):
        """Onglet de météo spatiale"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Indicateurs principaux
        indicators_group = QGroupBox("🌤️ Indicateurs de météo spatiale")
        indicators_layout = QGridLayout(indicators_group)
        
        # Vent solaire
        vent_frame = self.create_meteo_indicator("🌬️ Vent solaire", 
                                                  f"{self.meteo_spatiale['vent_solaire']:.0f} km/s",
                                                  "#4CAF50")
        indicators_layout.addWidget(vent_frame, 0, 0)
        
        # Indice Kp
        kp_color = "#4CAF50" if self.meteo_spatiale['indice_Kp'] < 5 else "#FFA500"
        kp_frame = self.create_meteo_indicator("⚡ Indice Kp", 
                                                str(self.meteo_spatiale['indice_Kp']),
                                                kp_color)
        indicators_layout.addWidget(kp_frame, 0, 1)
        
        # Flux solaire
        flux_frame = self.create_meteo_indicator("☀️ Flux solaire", 
                                                  f"{self.meteo_spatiale['flux_solaire']:.0f} SFU",
                                                  "#2196F3")
        indicators_layout.addWidget(flux_frame, 1, 0)
        
        # Protons énergétiques
        proton_color = {"Faible": "#4CAF50", "Modéré": "#FFA500", "Élevé": "#F44336"}
        proton_frame = self.create_meteo_indicator("⚛️ Protons", 
                                                    self.meteo_spatiale['protons_energetiques'],
                                                    proton_color[self.meteo_spatiale['protons_energetiques']])
        indicators_layout.addWidget(proton_frame, 1, 1)
        
        layout.addWidget(indicators_group)
        
        # Graphique d'activité solaire
        chart_group = QGroupBox("📈 Activité solaire (dernières 24h)")
        chart_layout = QVBoxLayout(chart_group)
        
        # Créer un graphique simple
        chart = QChart()
        chart.setTheme(QChart.ChartThemeDark)
        
        series = QLineSeries()
        for i in range(24):
            series.append(i, random.uniform(50, 200))
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Flux de rayons X")
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(chart_view)
        
        layout.addWidget(chart_group)
        
        # Alertes
        alerts_group = QGroupBox("⚠️ Alertes en cours")
        alerts_layout = QVBoxLayout(alerts_group)
        
        alerts = [
            "🟡 Tempête géomagnétique mineure (G1)",
            "🟢 Conditions nominales",
            "🟠 Éruption solaire de classe M détectée",
        ]
        
        for alert in alerts:
            label = QLabel(alert)
            alerts_layout.addWidget(label)
        
        layout.addWidget(alerts_group)
        
        return tab
    
    def create_meteo_indicator(self, title, value, color):
        """Crée un indicateur météo"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(value_label)
        
        return frame
    
    def create_carte_tab(self):
        """Onglet avec carte interactive"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Contrôles de la carte
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        
        controls_layout.addWidget(QLabel("Type de carte:"))
        
        self.map_type = QComboBox()
        self.map_type.addItems(["Satellite", "Route", "Terrain", "Relief"])
        controls_layout.addWidget(self.map_type)
        
        controls_layout.addStretch()
        
        self.refresh_map_btn = QPushButton("🔄 Actualiser")
        self.refresh_map_btn.clicked.connect(self.refresh_map)
        controls_layout.addWidget(self.refresh_map_btn)
        
        layout.addWidget(controls)
        
        # Carte (simulée avec QLabel pour l'instant)
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setStyleSheet("""
            background-color: #1a1a2a;
            color: white;
            border: 1px solid #333366;
            font-size: 24px;
        """)
        self.map_label.setMinimumHeight(500)
        
        self.refresh_map()
        
        layout.addWidget(self.map_label)
        
        return tab
    
    def refresh_map(self):
        """Rafraîchit l'affichage de la carte"""
        map_type = self.map_type.currentText()
        
        # Simulation de différentes cartes
        if map_type == "Satellite":
            self.map_label.setText("🛰️ Vue satellite\n[Simulation d'image satellite]")
        elif map_type == "Route":
            self.map_label.setText("🗺️ Carte routière\n[Simulation de carte routière]")
        elif map_type == "Terrain":
            self.map_label.setText("⛰️ Carte de terrain\n[Simulation de relief]")
        elif map_type == "Relief":
            self.map_label.setText("🏔️ Carte de relief\n[Simulation de topographie]")
        
        # Ajouter quelques positions de satellites
        positions_text = "\n\nSatellites en vue:\n"
        for sat in self.satellites[:3]:
            positions_text += f"• {sat['nom']} ({sat['position'][0]:.1f}°, {sat['position'][1]:.1f}°)\n"
        
        self.map_label.setText(self.map_label.text() + positions_text)
    
    def setup_menu(self):
        """Configure le menu principal"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("&Nouveau", self.new_project, "Ctrl+N")
        file_menu.addAction("&Ouvrir", self.open_project, "Ctrl+O")
        file_menu.addAction("&Enregistrer", self.save_project, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("&Exporter", self.export_data)
        file_menu.addAction("&Imprimer", self.print_view, "Ctrl+P")
        file_menu.addSeparator()
        file_menu.addAction("&Quitter", self.close, "Ctrl+Q")
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("Plein écran", self.toggle_fullscreen, "F11")
        view_menu.addSeparator()
        view_menu.addAction("Actualiser", self.refresh_all, "F5")
        
        # Menu Outils
        tools_menu = menubar.addMenu("&Outils")
        tools_menu.addAction("Calculateur orbital", self.show_orbital_calc)
        tools_menu.addAction("Prévisions météo", self.show_weather_forecast)
        tools_menu.addAction("Trajectoires", self.show_trajectories)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("Documentation", self.show_docs)
        help_menu.addAction("À propos", self.show_about)
    
    def setup_toolbar(self):
        """Configure la barre d'outils"""
        toolbar = QToolBar("Outils principaux")
        self.addToolBar(toolbar)
        
        toolbar.addAction(QIcon(), "📁 Nouveau")
        toolbar.addAction(QIcon(), "📂 Ouvrir")
        toolbar.addAction(QIcon(), "💾 Sauvegarder")
        toolbar.addSeparator()
        toolbar.addAction(QIcon(), "🔄 Actualiser")
        toolbar.addAction(QIcon(), "📊 Graphiques")
        toolbar.addSeparator()
        toolbar.addAction(QIcon(), "❓ Aide")
    
    def setup_statusbar(self):
        """Configure la barre d'état"""
        self.statusBar().showMessage("Prêt - Système opérationnel")
        
        # Horloge
        self.clock_label = QLabel()
        self.statusBar().addPermanentWidget(self.clock_label)
        
        # Connexions
        self.conn_label = QLabel("🟢 Connecté")
        self.conn_label.setStyleSheet("color: #4CAF50;")
        self.statusBar().addPermanentWidget(self.conn_label)
    
    def update_realtime_data(self):
        """Met à jour les données en temps réel"""
        # Mettre à jour l'horloge
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(f"🕐 {current_time}")
        
        # Simuler le mouvement des satellites
        for sat in self.satellites:
            sat["position"][0] += random.uniform(-5, 5)
            sat["position"][1] += random.uniform(-5, 5)
            
            # Garder dans les limites
            sat["position"][0] = max(-180, min(180, sat["position"][0]))
            sat["position"][1] = max(-90, min(90, sat["position"][1]))
    
    # Actions du menu
    def new_project(self):
        self.statusBar().showMessage("Nouveau projet créé")
    
    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Ouvrir projet", "", "Projet spatial (*.json)")
        if filename:
            self.statusBar().showMessage(f"Projet ouvert: {filename}")
    
    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder projet", "", "Projet spatial (*.json)")
        if filename:
            self.statusBar().showMessage(f"Projet sauvegardé: {filename}")
    
    def export_data(self):
        self.statusBar().showMessage("Export des données...")
    
    def print_view(self):
        self.statusBar().showMessage("Préparation de l'impression...")
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def refresh_all(self):
        self.statusBar().showMessage("Actualisation en cours...")
        self.update_satellite_table()
        self.update_mission_table()
    
    def show_orbital_calc(self):
        QMessageBox.information(self, "Calculateur orbital", 
                               "Calculateur orbital en développement")
    
    def show_weather_forecast(self):
        QMessageBox.information(self, "Prévisions météo", 
                               "Prévisions météo spatiales")
    
    def show_trajectories(self):
        QMessageBox.information(self, "Trajectoires", 
                               "Visualisation des trajectoires")
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation", 
                               "Documentation disponible sur GitHub")
    
    def show_about(self):
        QMessageBox.about(self, "À propos", 
                          "🚀 Tableau de Bord Spatial v2.0\n"
                          "Centre de contrôle des missions spatiales\n"
                          "Développé avec PySide6\n"
                          "© 2026")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Palette sombre personnalisée
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
    
    window = SpatialDashboard()
    window.show()
    sys.exit(app.exec())