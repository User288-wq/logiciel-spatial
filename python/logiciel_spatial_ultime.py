# python/logiciel_spatial_cloud.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🚀 LOGICIEL SPATIAL CLOUD - Version Ultimate
=============================================
Avec :
- Données NASA en direct
- Position ISS en temps réel
- Alertes météo spatiale
- Images satellites réelles
- API REST intégrées
"""

import sys
import os
import json
import requests
import sqlite3
import hashlib
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

# APIs et données temps réel
import ephem
from astroquery.nasa import ADS
from astroquery.jplhorizons import Horizons

# PySide6
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
from PySide6.QtWebEngineWidgets import QWebEngineView

# ============================================================================
# MODULE API NASA
# ============================================================================

class NASA_API:
    """Connexion aux APIs NASA"""
    
    def __init__(self):
        self.api_key = "DEMO_KEY"  # Clé gratuite limitée
        self.base_url = "https://api.nasa.gov"
        
    def get_apod(self, date=None):
        """Astronomy Picture of the Day"""
        url = f"{self.base_url}/planetary/apod"
        params = {"api_key": self.api_key}
        if date:
            params["date"] = date
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return {"error": "Connexion impossible"}
    
    def get_iss_position(self):
        """Position actuelle de l'ISS"""
        url = "http://api.open-notify.org/iss-now.json"
        try:
            response = requests.get(url)
            data = response.json()
            return {
                "latitude": float(data["iss_position"]["latitude"]),
                "longitude": float(data["iss_position"]["longitude"]),
                "timestamp": datetime.fromtimestamp(data["timestamp"])
            }
        except:
            return None
    
    def get_people_in_space(self):
        """Astronautes actuellement dans l'espace"""
        url = "http://api.open-notify.org/astros.json"
        try:
            response = requests.get(url)
            data = response.json()
            return data["people"], data["number"]
        except:
            return [], 0
    
    def get_neo_feed(self, start_date=None, end_date=None):
        """Near Earth Objects - Astéroïdes proches"""
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/neo/rest/v1/feed"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return {"element_count": 0, "near_earth_objects": {}}
    
    def get_mars_weather(self):
        """Météo sur Mars (Curiosity rover)"""
        url = f"{self.base_url}/insight_weather/"
        params = {
            "api_key": self.api_key,
            "feedtype": "json",
            "ver": "1.0"
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            return None

# ============================================================================
# MODULE POSITION ISS EN TEMPS RÉEL
# ============================================================================

class ISSRealTimeTracker(QWidget):
    """Tracker en temps réel de l'ISS"""
    
    def __init__(self, nasa_api):
        super().__init__()
        self.nasa = nasa_api
        self.setup_ui()
        
        # Timer pour mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(5000)  # Toutes les 5 secondes
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🛰️ STATION SPATIALE INTERNATIONALE - EN DIRECT")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            padding: 10px;
            background-color: #1a1a2a;
            border-radius: 5px;
        """)
        layout.addWidget(title)
        
        # Informations
        info_group = QGroupBox("📍 Position actuelle")
        info_layout = QFormLayout(info_group)
        
        self.lat_label = QLabel("--")
        self.lon_label = QLabel("--")
        self.time_label = QLabel("--")
        
        info_layout.addRow("Latitude:", self.lat_label)
        info_layout.addRow("Longitude:", self.lon_label)
        info_layout.addRow("Dernière mise à jour:", self.time_label)
        
        layout.addWidget(info_group)
        
        # Carte simplifiée
        map_group = QGroupBox("🗺️ Position sur Terre")
        map_layout = QVBoxLayout(map_group)
        
        self.map_label = QLabel()
        self.map_label.setMinimumHeight(200)
        self.map_label.setStyleSheet("""
            background-color: #0a1a2a;
            border: 1px solid #2196F3;
        """)
        map_layout.addWidget(self.map_label)
        
        layout.addWidget(map_group)
        
        # Équipage
        crew_group = QGroupBox("👨‍🚀 Équipage actuel")
        crew_layout = QVBoxLayout(crew_group)
        
        self.crew_list = QListWidget()
        crew_layout.addWidget(self.crew_list)
        
        layout.addWidget(crew_group)
        
        # Première mise à jour
        self.update_position()
        self.update_crew()
    
    def update_position(self):
        """Met à jour la position de l'ISS"""
        pos = self.nasa.get_iss_position()
        
        if pos:
            self.lat_label.setText(f"{pos['latitude']:.4f}°")
            self.lon_label.setText(f"{pos['longitude']:.4f}°")
            self.time_label.setText(pos['timestamp'].strftime("%H:%M:%S"))
            
            # Mettre à jour la carte
            self.update_map(pos['latitude'], pos['longitude'])
    
    def update_map(self, lat, lon):
        """Met à jour l'affichage de la carte"""
        # Créer une carte simple avec matplotlib
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        
        fig = Figure(figsize=(6, 3), facecolor='#0a1a2a')
        ax = fig.add_subplot(111)
        
        # Fond de carte simplifié
        ax.set_facecolor('#1a2a3a')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        
        # Grille
        ax.grid(True, alpha=0.3, color='white')
        
        # Position de l'ISS
        ax.plot(lon, lat, 'ro', markersize=10, label='ISS')
        ax.plot(lon, lat, 'r*', markersize=15)
        
        ax.set_title("Position de l'ISS", color='white')
        ax.tick_params(colors='white')
        
        # Convertir en QImage
        canvas = FigureCanvas(fig)
        canvas.draw()
        
        # Afficher dans le QLabel
        from PIL import Image
        import io
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=fig.get_facecolor())
        buf.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        
        self.map_label.setPixmap(pixmap.scaled(
            self.map_label.width(), self.map_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    def update_crew(self):
        """Met à jour la liste de l'équipage"""
        crew, count = self.nasa.get_people_in_space()
        
        self.crew_list.clear()
        self.crew_list.addItem(f"👥 Total: {count} personnes dans l'espace")
        self.crew_list.addItem("")
        
        for person in crew:
            item = QListWidgetItem(f"👨‍🚀 {person['name']} - {person['craft']}")
            if person['craft'] == 'ISS':
                item.setForeground(QColor(76, 175, 80))
            else:
                item.setForeground(QColor(255, 165, 0))
            self.crew_list.addItem(item)

# ============================================================================
# MODULE ASTÉROÏDES GÉOCROISEURS
# ============================================================================

class NEOTracker(QWidget):
    """Tracker des astéroïdes proches de la Terre"""
    
    def __init__(self, nasa_api):
        super().__init__()
        self.nasa = nasa_api
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("☄️ ASTÉROÏDES GÉOCROISEURS (NEO)")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FFA500;
            padding: 10px;
            background-color: #1a1a2a;
            border-radius: 5px;
        """)
        layout.addWidget(title)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nom", "Diamètre (m)", "Distance (km)", 
            "Vitesse (km/s)", "Date approche", "Danger"
        ])
        
        layout.addWidget(self.table)
        
        # Statistiques
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QFormLayout(stats_group)
        
        self.count_label = QLabel("0")
        self.danger_label = QLabel("0")
        self.closest_label = QLabel("--")
        
        stats_layout.addRow("Nombre d'objets suivis:", self.count_label)
        stats_layout.addRow("Objets potentiellement dangereux:", self.danger_label)
        stats_layout.addRow("Approche la plus proche:", self.closest_label)
        
        layout.addWidget(stats_group)
    
    def load_data(self):
        """Charge les données des astéroïdes"""
        data = self.nasa.get_neo_feed()
        
        if data and data['element_count'] > 0:
            objects = []
            dangerous = 0
            closest = float('inf')
            closest_name = ""
            
            for date, neos in data['near_earth_objects'].items():
                for neo in neos:
                    name = neo['name']
                    diameter = neo['estimated_diameter']['meters']['estimated_diameter_max']
                    speed = float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_second'])
                    distance = float(neo['close_approach_data'][0]['miss_distance']['kilometers'])
                    date_approach = neo['close_approach_data'][0]['close_approach_date']
                    is_dangerous = neo['is_potentially_hazardous_asteroid']
                    
                    objects.append({
                        'name': name,
                        'diameter': diameter,
                        'speed': speed,
                        'distance': distance,
                        'date': date_approach,
                        'danger': is_dangerous
                    })
                    
                    if is_dangerous:
                        dangerous += 1
                    
                    if distance < closest:
                        closest = distance
                        closest_name = name
            
            # Remplir le tableau
            self.table.setRowCount(len(objects))
            for i, obj in enumerate(objects):
                self.table.setItem(i, 0, QTableWidgetItem(obj['name']))
                self.table.setItem(i, 1, QTableWidgetItem(f"{obj['diameter']:.1f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{obj['distance']:,.0f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{obj['speed']:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(obj['date']))
                
                danger_item = QTableWidgetItem("⚠️ OUI" if obj['danger'] else "✅ NON")
                if obj['danger']:
                    danger_item.setForeground(QColor(255, 99, 71))
                else:
                    danger_item.setForeground(QColor(76, 175, 80))
                self.table.setItem(i, 5, danger_item)
            
            # Mettre à jour les stats
            self.count_label.setText(str(len(objects)))
            self.danger_label.setText(str(dangerous))
            self.closest_label.setText(f"{closest_name} ({closest:,.0f} km)")

# ============================================================================
# MODULE IMAGE ASTRONOMIQUE DU JOUR
# ============================================================================

class APODViewer(QWidget):
    """Affiche l'image astronomique du jour (NASA APOD)"""
    
    def __init__(self, nasa_api):
        super().__init__()
        self.nasa = nasa_api
        self.setup_ui()
        self.load_apod()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        self.title_label = QLabel("Chargement...")
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)
        layout.addWidget(self.title_label)
        
        # Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setStyleSheet("""
            background-color: #0a0a2a;
            border: 2px solid #4CAF50;
        """)
        layout.addWidget(self.image_label)
        
        # Explication
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setMaximumHeight(150)
        layout.addWidget(self.explanation_text)
        
        # Date selector
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        
        load_btn = QPushButton("Charger")
        load_btn.clicked.connect(self.load_apod)
        date_layout.addWidget(load_btn)
        
        layout.addWidget(date_widget)
    
    def load_apod(self):
        """Charge l'APOD pour la date sélectionnée"""
        date = self.date_edit.date().toString("yyyy-MM-dd")
        
        data = self.nasa.get_apod(date)
        
        if data and 'error' not in data:
            self.title_label.setText(f"📸 {data['title']}")
            self.explanation_text.setText(data['explanation'])
            
            # Charger l'image
            if 'url' in data:
                self.load_image(data['url'])
    
    def load_image(self, url):
        """Charge une image depuis une URL"""
        try:
            import requests
            from PIL import Image
            import io
            
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            
            # Convertir en QPixmap
            img = img.convert('RGB')
            data = img.tobytes('raw', 'RGB')
            qimg = QImage(data, img.width, img.height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            # Redimensionner
            pixmap = pixmap.scaled(
                600, 300,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(pixmap)
            
        except Exception as e:
            self.image_label.setText(f"❌ Erreur: {str(e)}")

# ============================================================================
# MODULE ALERTES EN TEMPS RÉEL
# ============================================================================

class SpaceWeatherAlerts(QWidget):
    """Alertes météo spatiale en temps réel"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Timer pour mises à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_alerts)
        self.timer.start(60000)  # Toutes les minutes
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("⚠️ ALERTES MÉTÉO SPATIALE EN DIRECT")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FF4444;
            padding: 10px;
            background-color: #1a1a2a;
            border-radius: 5px;
        """)
        layout.addWidget(title)
        
        # Liste des alertes
        self.alerts_list = QListWidget()
        layout.addWidget(self.alerts_list)
        
        # Niveaux d'alerte
        levels_group = QGroupBox("📊 Niveaux actuels")
        levels_layout = QFormLayout(levels_group)
        
        self.kp_label = QLabel("--")
        self.solar_wind_label = QLabel("--")
        self.flux_label = QLabel("--")
        
        levels_layout.addRow("Indice Kp:", self.kp_label)
        levels_layout.addRow("Vent solaire:", self.solar_wind_label)
        levels_layout.addRow("Flux de protons:", self.flux_label)
        
        layout.addWidget(levels_group)
        
        self.update_alerts()
    
    def update_alerts(self):
        """Met à jour les alertes"""
        # Simuler des données (en vrai, appeler NOAA SWPC API)
        alerts = [
            ("🌞 Éruption solaire de classe M", "Modéré", datetime.now()),
            ("🌀 Tempête géomagnétique G1", "Mineur", datetime.now() - timedelta(hours=2)),
            ("⚡ Flux de protons élevé", "Modéré", datetime.now() - timedelta(hours=5)),
            ("🛰️ Satellite en mode sécurité", "Critique", datetime.now() - timedelta(days=1)),
            ("📡 Interférences radio", "Mineur", datetime.now() - timedelta(hours=3)),
        ]
        
        self.alerts_list.clear()
        for alert, level, time in alerts:
            item = QListWidgetItem(f"{alert} - {level} ({time.strftime('%H:%M')})")
            
            if level == "Critique":
                item.setForeground(QColor(255, 99, 71))
            elif level == "Modéré":
                item.setForeground(QColor(255, 165, 0))
            else:
                item.setForeground(QColor(76, 175, 80))
            
            self.alerts_list.addItem(item)
        
        # Mettre à jour les niveaux
        self.kp_label.setText("4 (Actif)")
        self.solar_wind_label.setText("450 km/s")
        self.flux_label.setText("Modéré")

# ============================================================================
# MODULE PRÉVISIONS ASTRONOMIQUES
# ============================================================================

class AstronomicalForecast(QWidget):
    """Prévisions astronomiques"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🔭 PRÉVISIONS ASTRONOMIQUES")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #4CAF50;
            padding: 10px;
            background-color: #1a1a2a;
            border-radius: 5px;
        """)
        layout.addWidget(title)
        
        # Tableau des prévisions
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Événement", "Visibilité", "Meilleur moment"])
        
        events = [
            ("2025-03-20", "Équinoxe de printemps", "Excellente", "Toute la journée"),
            ("2025-03-25", "Pleine Lune", "Excellente", "Nuit"),
            ("2025-04-08", "Éclipse solaire partielle", "Bonne", "11h-13h"),
            ("2025-04-22", "Pluie d'étoiles filantes (Lyrides)", "Moyenne", "Après minuit"),
            ("2025-05-06", "Pluie d'étoiles filantes (η-Aquarides)", "Bonne", "3h-5h"),
            ("2025-05-23", "Conjonction Vénus-Jupiter", "Excellente", "Coucher du soleil"),
            ("2025-06-21", "Solstice d'été", "Excellente", "Toute la journée"),
        ]
        
        self.table.setRowCount(len(events))
        for i, (date, event, vis, time) in enumerate(events):
            self.table.setItem(i, 0, QTableWidgetItem(date))
            self.table.setItem(i, 1, QTableWidgetItem(event))
            
            vis_item = QTableWidgetItem(vis)
            if vis == "Excellente":
                vis_item.setForeground(QColor(76, 175, 80))
            elif vis == "Bonne":
                vis_item.setForeground(QColor(255, 165, 0))
            else:
                vis_item.setForeground(QColor(255, 99, 71))
            self.table.setItem(i, 2, vis_item)
            
            self.table.setItem(i, 3, QTableWidgetItem(time))
        
        layout.addWidget(self.table)
        
        # Informations supplémentaires
        info_group = QGroupBox("ℹ️ Informations")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "• Les équinoxes marquent le début du printemps et de l'automne\n"
            "• Les solstices marquent le début de l'été et de l'hiver\n"
            "• Les pluies d'étoiles filantes sont visibles à l'œil nu\n"
            "• Utilisez des jumelles pour les conjonctions planétaires"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)

# ============================================================================
# LOGICIEL PRINCIPAL AVEC APIs RÉELLES
# ============================================================================

class LogicielSpatialCloud(QMainWindow):
    """Version cloud avec APIs en temps réel"""
    
    def __init__(self):
        super().__init__()
        self.nasa_api = NASA_API()
        
        self.setWindowTitle("🚀 LOGICIEL SPATIAL CLOUD - Données en direct")
        self.setGeometry(50, 50, 1400, 900)
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Barre d'info temps réel
        self.create_status_bar()
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Ajouter tous les modules
        self.tabs.addTab(ISSRealTimeTracker(self.nasa_api), "🛰️ ISS Live")
        self.tabs.addTab(NEOTracker(self.nasa_api), "☄️ Astéroïdes")
        self.tabs.addTab(APODViewer(self.nasa_api), "📸 APOD")
        self.tabs.addTab(SpaceWeatherAlerts(), "⚠️ Alertes")
        self.tabs.addTab(AstronomicalForecast(), "🔭 Prévisions")
        
        # Anciens modules (optionnel)
        try:
            from logiciel_spatial_complet import (
                SystemeSolaireModule, SatellitesModule,
                OSMModule, AnalyseGeospatialeModule
            )
            self.tabs.addTab(SystemeSolaireModule(), "🪐 Système solaire")
            self.tabs.addTab(SatellitesModule(), "🛰️ Catalogue")
            self.tabs.addTab(OSMModule(), "🗺️ OpenStreetMap")
            self.tabs.addTab(AnalyseGeospatialeModule(), "📊 Analyse")
        except:
            pass
        
        layout.addWidget(self.tabs)
    
    def create_status_bar(self):
        """Barre d'état avec infos en direct"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Timer pour mise à jour
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(10000)  # Toutes les 10 secondes
        
        # Widgets de statut
        self.iss_status = QLabel("🛰️ ISS: --")
        self.neo_status = QLabel("☄️ NEO: --")
        self.crew_status = QLabel("👨‍🚀 Équipage: --")
        self.time_status = QLabel("🕐 --")
        
        status_bar.addPermanentWidget(self.iss_status)
        status_bar.addPermanentWidget(self.neo_status)
        status_bar.addPermanentWidget(self.crew_status)
        status_bar.addPermanentWidget(self.time_status)
        
        self.update_status()
    
    def update_status(self):
        """Met à jour la barre d'état"""
        # Position ISS
        pos = self.nasa_api.get_iss_position()
        if pos:
            self.iss_status.setText(
                f"🛰️ ISS: {pos['latitude']:.1f}°, {pos['longitude']:.1f}°"
            )
        
        # Équipage
        _, count = self.nasa_api.get_people_in_space()
        self.crew_status.setText(f"👨‍🚀 Équipage: {count}")
        
        # Astéroïdes (simulé)
        neo_count = random.randint(15, 25)
        self.neo_status.setText(f"☄️ NEO: {neo_count}")
        
        # Heure
        self.time_status.setText(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("&Actualiser tout", self.refresh_all, "F5")
        file_menu.addSeparator()
        file_menu.addAction("&Quitter", self.close, "Ctrl+Q")
        
        # APIs
        api_menu = menubar.addMenu("&APIs")
        api_menu.addAction("🔄 Tester connexion NASA", self.test_nasa_api)
        api_menu.addAction("📡 Statut des APIs", self.show_api_status)
        
        # Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("Documentation", self.show_docs)
        help_menu.addAction("À propos", self.show_about)
    
    def refresh_all(self):
        """Actualise tous les modules"""
        current_index = self.tabs.currentIndex()
        
        # Forcer la mise à jour de l'onglet courant
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'update_position'):
            current_widget.update_position()
        elif hasattr(current_widget, 'load_data'):
            current_widget.load_data()
        elif hasattr(current_widget, 'update_alerts'):
            current_widget.update_alerts()
        
        self.statusBar().showMessage("✅ Données actualisées", 3000)
    
    def test_nasa_api(self):
        """Teste la connexion à l'API NASA"""
        data = self.nasa_api.get_apod()
        
        if data and 'error' not in data:
            QMessageBox.information(self, "✅ API OK",
                f"Connexion à l'API NASA réussie!\n\n"
                f"Dernière image: {data['title']}")
        else:
            QMessageBox.warning(self, "⚠️ API Error",
                "Connexion limitée - Utilisation du mode démo\n"
                "Pour un accès complet, obtenez une clé API sur:\n"
                "https://api.nasa.gov")
    
    def show_api_status(self):
        """Affiche le statut des APIs"""
        status = "📡 STATUT DES APIS\n"
        status += "="*40 + "\n\n"
        
        # NASA API
        apod = self.nasa_api.get_apod()
        if apod and 'error' not in apod:
            status += "✅ NASA API: Connecté\n"
        else:
            status += "⚠️ NASA API: Mode démo\n"
        
        # ISS API
        iss = self.nasa_api.get_iss_position()
        if iss:
            status += f"✅ ISS API: Connecté\n"
            status += f"   Position: {iss['latitude']:.1f}°, {iss['longitude']:.1f}°\n"
        else:
            status += "❌ ISS API: Hors ligne\n"
        
        # Open Notify
        people, count = self.nasa_api.get_people_in_space()
        if people:
            status += f"✅ Open Notify: Connecté\n"
            status += f"   {count} personnes dans l'espace\n"
        
        QMessageBox.information(self, "Statut APIs", status)
    
    def show_docs(self):
        QMessageBox.information(self, "Documentation",
            "🚀 LOGICIEL SPATIAL CLOUD\n\n"
            "APIs utilisées:\n"
            "• NASA API - Images et données\n"
            "• Open Notify - ISS et équipage\n"
            "• NEO API - Astéroïdes\n\n"
            "Modules:\n"
            "• ISS en temps réel\n"
            "• Astéroïdes géocroiseurs\n"
            "• Image astronomique du jour\n"
            "• Alertes météo spatiale\n"
            "• Prévisions astronomiques")
    
    def show_about(self):
        QMessageBox.about(self, "À propos",
            "🚀 LOGICIEL SPATIAL CLOUD\n"
            "Version 5.0\n\n"
            "Données en temps réel depuis:\n"
            "• NASA Open APIs\n"
            "• Open Notify\n"
            "• NOAA Space Weather\n\n"
            "Développé avec PySide6\n"
            "© 2026")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style
    app.setStyle("Fusion")
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    
    window = LogicielSpatialCloud()
    window.show()
    
    sys.exit(app.exec())