import sys
import numpy as np
import pandas as pd
from datetime import datetime
import random

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *

# Pour les graphiques
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class OSMComplet(QMainWindow):
    """Visualiseur OpenStreetMap complet avec analyses"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Visualiseur OpenStreetMap - Analyse Urbaine")
        self.setGeometry(100, 100, 1400, 900)
        
        self.current_city = "Dakar, Senegal"
        self.cities_data = self.load_cities_data()
        
        self.setup_ui()
        self.setup_menu()
        self.show_city_data()
        
    def load_cities_data(self):
        """Charge les données des villes"""
        return {
            "Dakar, Senegal": {
                "country": "Sénégal",
                "population": 1146000,
                "area": 83,
                "density": 13800,
                "mayor": "Barthélemy Dias",
                "established": 1857,
                "timezone": "GMT",
                "coordinates": [14.7167, -17.4677],
                "districts": ["Plateau", "Gueule Tapée", "Fann-Point E", "Ouakam", "Ngor"],
                "transport": ["Bus", "Taxi", "Train", "Ferry"],
                "airport": "Aéroport Blaise Diagne"
            },
            "Paris, France": {
                "country": "France",
                "population": 2148000,
                "area": 105.4,
                "density": 20380,
                "mayor": "Anne Hidalgo",
                "established": 300,
                "timezone": "CET",
                "coordinates": [48.8566, 2.3522],
                "districts": ["Louvre", "Bourse", "Temple", "Hôtel-de-Ville", "Panthéon"],
                "transport": ["Métro", "Bus", "RER", "Tram", "Vélib"],
                "airport": "Charles de Gaulle"
            },
            "New York, USA": {
                "country": "États-Unis",
                "population": 8400000,
                "area": 783.8,
                "density": 10720,
                "mayor": "Eric Adams",
                "established": 1624,
                "timezone": "EST",
                "coordinates": [40.7128, -74.0060],
                "districts": ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
                "transport": ["Subway", "Bus", "Ferry", "Taxi"],
                "airport": "JFK"
            },
            "Touba, Senegal": {
                "country": "Sénégal",
                "population": 753000,
                "area": 45,
                "density": 16700,
                "mayor": "Abdou Lahad Ka",
                "established": 1887,
                "timezone": "GMT",
                "coordinates": [14.8667, -15.8833],
                "districts": ["Darou Marnane", "Darou Khoudoss", "Ndindy", "Mbacké"],
                "transport": ["Bus", "Taxi", "Charrettes"],
                "airport": "Aéroport de Touba (en projet)"
            }
        }
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QHBoxLayout(central)
        
        # ===== PANEL GAUCHE (CONTRÔLES) =====
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # ===== PANEL CENTRAL (CARTE) =====
        center_panel = self.create_map_panel()
        main_layout.addWidget(center_panel, 3)
        
        # ===== PANEL DROIT (ANALYSES) =====
        right_panel = self.create_analysis_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt - Visualiseur OSM chargé")
        
    def create_control_panel(self):
        """Crée le panneau de contrôle à gauche"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("🛸 PANEL DE CONTRÔLE")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #4CAF50;
            padding: 10px;
            background-color: #1a1a2a;
            border-radius: 5px;
        """)
        layout.addWidget(title)
        
        # ===== SÉLECTION VILLE =====
        city_group = QGroupBox("📍 Sélection ville")
        city_layout = QVBoxLayout(city_group)
        
        self.city_combo = QComboBox()
        self.city_combo.addItems(self.cities_data.keys())
        self.city_combo.currentTextChanged.connect(self.on_city_changed)
        city_layout.addWidget(self.city_combo)
        
        # Informations rapides
        self.city_info = QLabel("")
        self.city_info.setWordWrap(True)
        self.city_info.setStyleSheet("""
            background-color: #16213e;
            padding: 10px;
            border-radius: 3px;
            color: #888888;
        """)
        city_layout.addWidget(self.city_info)
        
        layout.addWidget(city_group)
        
        # ===== FILTRES =====
        filters_group = QGroupBox("🔍 Filtres")
        filters_layout = QVBoxLayout(filters_group)
        
        # Type de réseau
        filters_layout.addWidget(QLabel("Type de réseau:"))
        self.network_combo = QComboBox()
        self.network_combo.addItems([
            "Tous les types",
            "Routes principales",
            "Routes secondaires",
            "Chemins piétons",
            "Pistes cyclables"
        ])
        filters_layout.addWidget(self.network_combo)
        
        # Rayon d'analyse
        filters_layout.addWidget(QLabel("Rayon d'analyse (km):"))
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(1, 50)
        self.radius_slider.setValue(10)
        self.radius_slider.setTickInterval(5)
        self.radius_slider.setTickPosition(QSlider.TicksBelow)
        filters_layout.addWidget(self.radius_slider)
        
        self.radius_label = QLabel("10 km")
        self.radius_label.setAlignment(Qt.AlignCenter)
        filters_layout.addWidget(self.radius_label)
        self.radius_slider.valueChanged.connect(
            lambda v: self.radius_label.setText(f"{v} km")
        )
        
        layout.addWidget(filters_group)
        
        # ===== COUCHES =====
        layers_group = QGroupBox("🗂️ Couches actives")
        layers_layout = QVBoxLayout(layers_group)
        
        self.layers = {
            "routes": QCheckBox("🛣️ Routes"),
            "buildings": QCheckBox("🏢 Bâtiments"),
            "poi": QCheckBox("📍 Points d'intérêt"),
            "green": QCheckBox("🌳 Espaces verts"),
            "water": QCheckBox("💧 Hydrographie")
        }
        
        for check in self.layers.values():
            check.setChecked(True)
            layers_layout.addWidget(check)
        
        layout.addWidget(layers_group)
        
        # ===== BOUTONS D'ACTION =====
        buttons_group = QGroupBox("⚡ Actions")
        buttons_layout = QVBoxLayout(buttons_group)
        
        self.load_btn = QPushButton("📥 CHARGER DONNÉES")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.load_btn.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.load_btn)
        
        self.export_btn = QPushButton("💾 Exporter analyse")
        self.export_btn.clicked.connect(self.export_data)
        buttons_layout.addWidget(self.export_btn)
        
        self.print_btn = QPushButton("🖨️ Générer rapport")
        self.print_btn.clicked.connect(self.generate_report)
        buttons_layout.addWidget(self.print_btn)
        
        layout.addWidget(buttons_group)
        
        # ===== PROGRESSION =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return panel
    
    def create_map_panel(self):
        """Crée le panneau de la carte au centre"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Barre d'outils de la carte
        map_toolbar = QToolBar()
        map_toolbar.addAction(QIcon(), "🔍 Zoom +")
        map_toolbar.addAction(QIcon(), "🔍 Zoom -")
        map_toolbar.addAction(QIcon(), "🔄 Réinitialiser")
        map_toolbar.addSeparator()
        map_toolbar.addAction(QIcon(), "📍 Centrer")
        map_toolbar.addAction(QIcon(), "📏 Mesurer")
        
        layout.addWidget(map_toolbar)
        
        # Carte (Matplotlib)
        self.figure = Figure(figsize=(8, 6), facecolor='#1a1a2a')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Légende
        legend = QLabel(
            "🟢 Routes principales | 🔵 Routes secondaires | 🟡 Chemins | 🔴 POI"
        )
        legend.setStyleSheet("""
            background-color: #16213e;
            color: #888888;
            padding: 5px;
            border-radius: 3px;
        """)
        legend.setAlignment(Qt.AlignCenter)
        layout.addWidget(legend)
        
        return panel
    
    def create_analysis_panel(self):
        """Crée le panneau d'analyse à droite"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # ===== STATISTIQUES =====
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 8px;
            }
        """)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # ===== GRAPHIQUES =====
        charts_group = QGroupBox("📈 Analyses")
        charts_layout = QVBoxLayout(charts_group)
        
        # Mini graphique avec QtCharts
        self.chart_view = self.create_mini_chart()
        charts_layout.addWidget(self.chart_view)
        
        layout.addWidget(charts_group)
        
        # ===== POINTS D'INTÉRÊT =====
        poi_group = QGroupBox("📍 Points d'intérêt")
        poi_layout = QVBoxLayout(poi_group)
        
        self.poi_list = QListWidget()
        poi_layout.addWidget(self.poi_list)
        
        layout.addWidget(poi_group)
        
        return panel
    
    def create_mini_chart(self):
        """Crée un petit graphique d'analyse"""
        chart = QChart()
        chart.setTitle("Répartition des infrastructures")
        chart.setTheme(QChart.ChartThemeDark)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QPieSeries()
        series.append("Routes", 45)
        series.append("Bâtiments", 30)
        series.append("Espaces verts", 15)
        series.append("Points d'eau", 10)
        
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def setup_menu(self):
        """Configure le menu principal"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction("&Nouvelle analyse", self.new_analysis)
        file_menu.addAction("&Ouvrir", self.open_file)
        file_menu.addAction("&Enregistrer", self.save_file)
        file_menu.addSeparator()
        file_menu.addAction("&Quitter", self.close)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        view_menu.addAction("Plein écran", self.toggle_fullscreen)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction("Documentation", self.show_docs)
        help_menu.addAction("À propos", self.show_about)
    
    def on_city_changed(self, city):
        """Quand la ville change"""
        self.current_city = city
        self.update_city_info()
        self.status_bar.showMessage(f"Ville sélectionnée: {city}")
    
    def update_city_info(self):
        """Met à jour les infos de la ville"""
        if self.current_city in self.cities_data:
            data = self.cities_data[self.current_city]
            info = (
                f"🌍 {self.current_city}\n"
                f"Pays: {data['country']}\n"
                f"Population: {data['population']:,}\n"
                f"Superficie: {data['area']} km²\n"
                f"Maire: {data['mayor']}"
            )
            self.city_info.setText(info)
    
    def load_data(self):
        """Simule le chargement des données"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        self.load_btn.setEnabled(False)
        
        self.status_bar.showMessage(f"🔄 Chargement des données pour {self.current_city}...")
        
        # Simulation de chargement
        QTimer.singleShot(2000, self.process_loaded_data)
    
    def process_loaded_data(self):
        """Traite les données après chargement"""
        self.show_map()
        self.update_statistics()
        self.update_poi_list()
        
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.status_bar.showMessage(f"✅ Données chargées pour {self.current_city}")
    
    def show_map(self):
        """Affiche la carte avec les données"""
        self.figure.clear()
        
        # Créer deux sous-graphiques
        ax1 = self.figure.add_subplot(1, 2, 1)
        ax2 = self.figure.add_subplot(1, 2, 2)
        
        # Configurer les axes
        for ax in [ax1, ax2]:
            ax.set_facecolor('#0a0a2a')
            ax.tick_params(colors='white')
        
        # Générer des données selon la ville
        np.random.seed(hash(self.current_city) % 1000)
        
        # ===== CARTE PRINCIPALE =====
        # Routes
        for i in range(30 if "Paris" in self.current_city else 20):
            x = np.random.rand(10) * 10
            y = np.random.rand(10) * 10
            x = np.sort(x)
            
            if i < 10:
                color = '#4CAF50'  # Routes principales
                width = 2
            elif i < 20:
                color = '#2196F3'  # Routes secondaires
                width = 1.5
            else:
                color = '#FFA500'  # Chemins
                width = 1
            
            ax1.plot(x, y, color=color, alpha=0.6, linewidth=width)
        
        # Bâtiments
        buildings_x = np.random.rand(50) * 10
        buildings_y = np.random.rand(50) * 10
        ax1.scatter(buildings_x, buildings_y, c='#888888', s=20, alpha=0.5)
        
        # POI
        poi_x = np.random.rand(15) * 10
        poi_y = np.random.rand(15) * 10
        ax1.scatter(poi_x, poi_y, c='red', s=80, marker='*', alpha=0.8)
        
        ax1.set_title(f"Carte - {self.current_city}", color='white')
        ax1.set_xlim(0, 10)
        ax1.set_ylim(0, 10)
        
        # ===== CARTE DE DENSITÉ =====
        # Créer une heatmap de densité
        x = np.random.randn(1000) * 2 + 5
        y = np.random.randn(1000) * 2 + 5
        ax2.hist2d(x, y, bins=20, cmap='hot', alpha=0.8)
        ax2.set_title("Densité d'activité", color='white')
        ax2.set_xlim(0, 10)
        ax2.set_ylim(0, 10)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        # Statistiques différentes selon la ville
        if "Dakar" in self.current_city:
            stats = f"""
📊 ANALYSE URBAINE - {self.current_city}
{'='*50}

🛣️ RÉSEAU ROUTIER:
• Longueur totale: 125.3 km
• Densité: 8.5 km/km²
• Noeuds: 2,450
• Intersections: 890

🏢 BÂTIMENTS:
• Total: 3,250
• Résidentiels: 2,150 (66%)
• Commerciaux: 650 (20%)
• Industriels: 180 (6%)
• Éducatifs: 120 (4%)
• Religieux: 150 (5%)

🌳 ESPACES VERTS:
• Parcs: 24
• Surface verte: 1.2 km²
• Ratio: 8.5%

🚦 TRAFIC:
• Heures de pointe: 8h-10h, 17h-19h
• Vitesse moyenne: 35 km/h
• Congestion: Modérée

📈 ÉVOLUTION 2025:
• Nouvelles routes: +5.2 km
• Nouveaux bâtiments: +120
• Projets en cours: 8
"""
        elif "Paris" in self.current_city:
            stats = f"""
📊 ANALYSE URBAINE - {self.current_city}
{'='*50}

🛣️ RÉSEAU ROUTIER:
• Longueur totale: 850.6 km
• Densité: 15.2 km/km²
• Noeuds: 12,450
• Intersections: 4,890

🏢 BÂTIMENTS:
• Total: 28,450
• Résidentiels: 18,200 (64%)
• Commerciaux: 5,700 (20%)
• Industriels: 1,200 (4%)
• Éducatifs: 850 (3%)
• Religieux: 2,500 (9%)

🌳 ESPACES VERTS:
• Parcs: 420
• Surface verte: 8.5 km²
• Ratio: 12.5%

🚦 TRAFIC:
• Heures de pointe: 8h-10h, 17h-20h
• Vitesse moyenne: 18 km/h
• Congestion: Élevée

📈 ÉVOLUTION 2025:
• Nouvelles routes: +12.5 km
• Nouveaux bâtiments: +450
• Projets en cours: 25
"""
        else:
            stats = f"""
📊 ANALYSE URBAINE - {self.current_city}
{'='*50}

🛣️ RÉSEAU ROUTIER:
• Longueur totale: 320.8 km
• Densité: 10.2 km/km²
• Noeuds: 5,230
• Intersections: 1,890

🏢 BÂTIMENTS:
• Total: 8,450
• Résidentiels: 5,400 (64%)
• Commerciaux: 1,800 (21%)
• Industriels: 450 (5%)
• Éducatifs: 320 (4%)
• Religieux: 480 (6%)

🌳 ESPACES VERTS:
• Parcs: 65
• Surface verte: 3.2 km²
• Ratio: 7.8%

🚦 TRAFIC:
• Heures de pointe: 8h-10h, 17h-19h
• Vitesse moyenne: 42 km/h
• Congestion: Faible

📈 ÉVOLUTION 2025:
• Nouvelles routes: +8.3 km
• Nouveaux bâtiments: +210
• Projets en cours: 12
"""
        
        self.stats_text.setText(stats)
    
    def update_poi_list(self):
        """Met à jour la liste des points d'intérêt"""
        self.poi_list.clear()
        
        # Points d'intérêt selon la ville
        if "Dakar" in self.current_city:
            pois = [
                "🕌 Mosquée de la Divinité",
                "🏛️ Palais Présidentiel",
                "🏖️ Plage de Ngor",
                "🛍️ Marché Kermel",
                "🎭 Théâtre National",
                "🏥 Hôpital Principal",
                "📚 Université Cheikh Anta Diop",
                "✈️ Aéroport Blaise Diagne",
                "⚓ Port Autonome de Dakar",
                "🛍️ Sea Plaza"
            ]
        elif "Paris" in self.current_city:
            pois = [
                "🗼 Tour Eiffel",
                "🏛️ Musée du Louvre",
                "⛪ Notre-Dame",
                "🎭 Opéra Garnier",
                "🛍️ Galeries Lafayette",
                "🏥 Hôtel-Dieu",
                "📚 Sorbonne",
                "🌳 Jardin du Luxembourg",
                "🏛️ Arc de Triomphe",
                "🎡 Place de la Concorde"
            ]
        else:
            pois = [
                "🏛️ Mairie",
                "🏥 Hôpital Central",
                "📚 Bibliothèque Municipale",
                "🛍️ Centre Commercial",
                "⛪ Église Principale",
                "🏫 Université",
                "🌳 Parc Central",
                "🎭 Théâtre",
                "🏟️ Stade",
                "🚉 Gare"
            ]
        
        for poi in pois:
            item = QListWidgetItem(poi)
            item.setForeground(QColor("#4CAF50"))
            self.poi_list.addItem(item)
    
    def show_city_data(self):
        """Affiche les données initiales"""
        self.update_city_info()
        self.show_map()
        self.update_statistics()
        self.update_poi_list()
    
    def new_analysis(self):
        """Nouvelle analyse"""
        self.status_bar.showMessage("Nouvelle analyse créée")
    
    def open_file(self):
        """Ouvre un fichier"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir fichier", "", "Fichiers OSM (*.osm);;Tous (*.*)"
        )
        if filename:
            self.status_bar.showMessage(f"Fichier ouvert: {filename}")
    
    def save_file(self):
        """Sauvegarde un fichier"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder", "", "Fichiers OSM (*.osm)"
        )
        if filename:
            self.status_bar.showMessage(f"Fichier sauvegardé: {filename}")
    
    def export_data(self):
        """Exporte les données"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter", "", "CSV (*.csv);;JSON (*.json)"
        )
        if filename:
            self.status_bar.showMessage(f"Données exportées: {filename}")
    
    def generate_report(self):
        """Génère un rapport"""
        QMessageBox.information(self, "Rapport", 
            "Rapport généré avec succès!\n"
            f"Ville: {self.current_city}\n"
            f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    def toggle_fullscreen(self):
        """Active/désactive le plein écran"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_docs(self):
        """Affiche la documentation"""
        QMessageBox.information(self, "Documentation",
            "Visualiseur OpenStreetMap v2.0\n\n"
            "Fonctionnalités:\n"
            "• Visualisation de cartes urbaines\n"
            "• Analyses statistiques\n"
            "• Points d'intérêt\n"
            "• Données démographiques\n"
            "• Export de données")
    
    def show_about(self):
        """Affiche les informations"""
        QMessageBox.about(self, "À propos",
            "🗺️ Visualiseur OpenStreetMap\n"
            "Version 2.0\n\n"
            "Développé avec PySide6\n"
            "Données simulées pour démonstration\n"
            "© 2026")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Palette sombre améliorée
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
    
    window = OSMComplet()
    window.show()
    sys.exit(app.exec())