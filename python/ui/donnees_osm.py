import sys
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OSMDataViewer(QMainWindow):
    """Visualiseur de données OpenStreetMap - Version autonome"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗺️ Visualiseur OpenStreetMap")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_city = "Dakar, Senegal"
        self.setup_ui()
        
    def setup_ui(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Barre d'outils
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Zone d'affichage avec onglets
        self.tabs = QTabWidget()
        
        # Onglet Carte
        self.map_widget = QWidget()
        map_layout = QVBoxLayout(self.map_widget)
        
        self.figure = plt.figure(figsize=(10, 8), facecolor='#1a1a2a')
        self.canvas = FigureCanvas(self.figure)
        map_layout.addWidget(self.canvas)
        
        self.tabs.addTab(self.map_widget, "🗺️ Carte")
        
        # Onglet Statistiques
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 10px;
            }
        """)
        stats_layout.addWidget(self.stats_text)
        
        self.tabs.addTab(self.stats_widget, "📈 Statistiques")
        
        # Onglet Bâtiments
        self.buildings_widget = QWidget()
        buildings_layout = QVBoxLayout(self.buildings_widget)
        
        self.buildings_list = QTableWidget()
        self.buildings_list.setColumnCount(4)
        self.buildings_list.setHorizontalHeaderLabels([
            "Type", "Nombre", "Surface moy. (m²)", "Étages moy."
        ])
        self.buildings_list.horizontalHeader().setStretchLastSection(True)
        buildings_layout.addWidget(self.buildings_list)
        
        self.tabs.addTab(self.buildings_widget, "🏢 Bâtiments")
        
        layout.addWidget(self.tabs)
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt - Choisissez une ville")
        
        # Afficher la carte initiale
        self.show_sample_map()
        self.update_stats()
        self.update_buildings()
    
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2a2a3a;
                border: none;
                padding: 5px;
            }
            QToolButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
            QComboBox {
                background-color: #16213e;
                color: white;
                border: 1px solid #0f3460;
                padding: 5px;
                border-radius: 3px;
                min-width: 150px;
            }
            QLabel {
                color: white;
                padding: 5px;
            }
        """)
        
        # Sélection de ville
        toolbar.addWidget(QLabel("Ville:"))
        self.city_combo = QComboBox()
        self.city_combo.addItems([
            "Dakar, Senegal",
            "Paris, France",
            "New York, USA",
            "Tokyo, Japan",
            "Touba, Senegal",
            "Saint-Louis, Senegal"
        ])
        self.city_combo.currentTextChanged.connect(self.on_city_changed)
        toolbar.addWidget(self.city_combo)
        
        toolbar.addSeparator()
        
        # Type de réseau
        toolbar.addWidget(QLabel("Réseau:"))
        self.network_combo = QComboBox()
        self.network_combo.addItems([
            "Rue (drive)",
            "Marche (walk)",
            "Vélo (bike)",
            "Tous (all)"
        ])
        toolbar.addWidget(self.network_combo)
        
        toolbar.addSeparator()
        
        # Boutons
        self.load_btn = QPushButton("📥 Charger données")
        self.load_btn.clicked.connect(self.load_osm_data)
        toolbar.addWidget(self.load_btn)
        
        self.stats_btn = QPushButton("📊 MàJ statistiques")
        self.stats_btn.clicked.connect(self.update_all)
        toolbar.addWidget(self.stats_btn)
        
        return toolbar
    
    def on_city_changed(self, city):
        self.current_city = city
        self.status_bar.showMessage(f"Ville sélectionnée: {city}")
    
    def load_osm_data(self):
        """Simule le chargement des données OSM"""
        self.status_bar.showMessage(f"🔄 Chargement de {self.current_city}...")
        self.load_btn.setEnabled(False)
        
        # Simulation de chargement
        QTimer.singleShot(1500, self._process_osm_data)
    
    def _process_osm_data(self):
        """Traite les données simulées"""
        self.show_sample_map()
        self.update_stats()
        self.update_buildings()
        
        self.status_bar.showMessage(f"✅ Données chargées pour {self.current_city}")
        self.load_btn.setEnabled(True)
    
    def show_sample_map(self):
        """Affiche une carte simulée"""
        self.figure.clear()
        
        # Créer un graphique
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#0a0a2a')
        
        # Générer des données aléatoires pour simuler un réseau routier
        np.random.seed(hash(self.current_city) % 1000)
        
        # Simuler des routes
        for i in range(15):
            # Points de contrôle pour une route
            x = np.cumsum(np.random.rand(10) * 0.5)
            y = np.cumsum(np.random.rand(10) * 0.5)
            
            # Lisser un peu
            from scipy import interpolate
            t = np.linspace(0, 1, 50)
            fx = interpolate.interp1d(np.linspace(0, 1, 10), x, kind='cubic')
            fy = interpolate.interp1d(np.linspace(0, 1, 10), y, kind='cubic')
            x_smooth = fx(t)
            y_smooth = fy(t)
            
            # Couleur différente selon le type de route
            color = ['#4CAF50', '#2196F3', '#FFA500'][i % 3]
            ax.plot(x_smooth, y_smooth, color=color, alpha=0.6, linewidth=2)
        
        # Ajouter des points d'intérêt
        poi_x = np.random.rand(20) * 5
        poi_y = np.random.rand(20) * 5
        ax.scatter(poi_x, poi_y, c='red', s=50, marker='*', alpha=0.8)
        
        ax.set_title(f"Réseau routier - {self.current_city}", color='white', fontsize=14)
        ax.set_xlabel("Longitude (km)", color='white')
        ax.set_ylabel("Latitude (km)", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.2)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_stats(self):
        """Met à jour les statistiques"""
        # Statistiques différentes selon la ville
        stats_data = {
            "Dakar, Senegal": {
                "routes": "125 km",
                "segments": 1250,
                "densite": "8.5 km/km²",
                "population": "1.5 M",
                "quartiers": 24,
                "surface": "125 km²"
            },
            "Paris, France": {
                "routes": "850 km",
                "segments": 5200,
                "densite": "15.2 km/km²",
                "population": "2.1 M",
                "quartiers": 80,
                "surface": "105 km²"
            },
            "New York, USA": {
                "routes": "1200 km",
                "segments": 7800,
                "densite": "12.8 km/km²",
                "population": "8.4 M",
                "quartiers": 150,
                "surface": "783 km²"
            }
        }
        
        data = stats_data.get(self.current_city, stats_data["Dakar, Senegal"])
        
        stats = f"""
📊 STATISTIQUES DU RÉSEAU - {self.current_city}
{'='*50}

🛣️ ROUTES:
• Longueur totale: {data['routes']}
• Nombre de segments: {data['segments']}
• Densité: {data['densite']}

🏘️ QUARTIERS:
• Nombre de quartiers: {data['quartiers']}
• Surface totale: {data['surface']}
• Population estimée: {data['population']}

🚦 INFO TRAFIC:
• Heures de pointe: 8h-10h, 17h-19h
• Vitesse moyenne: 35 km/h
• Congestion: Modérée

🏗️ INFRASTRUCTURES:
• Nouvelles routes (2025): 12 km
• Projets en cours: 3
• Budget annuel: 15 M€

🌳 ESPACES VERTS:
• Parcs: 24
• Surface verte: 8.5 km²
• Ratio: 6.8%
"""
        
        self.stats_text.setText(stats)
    
    def update_buildings(self):
        """Met à jour la liste des bâtiments"""
        self.buildings_list.setRowCount(5)
        
        # Données différentes selon la ville
        if "Dakar" in self.current_city:
            buildings_data = [
                ("Résidentiel", "1250", "120", "2"),
                ("Commercial", "320", "350", "3"),
                ("Industriel", "85", "850", "1"),
                ("Éducatif", "45", "1200", "3"),
                ("Religieux", "62", "400", "2"),
            ]
        elif "Paris" in self.current_city:
            buildings_data = [
                ("Résidentiel", "8500", "85", "4"),
                ("Commercial", "2100", "280", "5"),
                ("Industriel", "320", "1200", "2"),
                ("Éducatif", "580", "1500", "4"),
                ("Religieux", "180", "600", "3"),
            ]
        else:
            buildings_data = [
                ("Résidentiel", "4500", "150", "3"),
                ("Commercial", "1200", "400", "4"),
                ("Industriel", "250", "1000", "1"),
                ("Éducatif", "180", "1300", "3"),
                ("Religieux", "95", "500", "2"),
            ]
        
        for i, (typ, nb, surface, etages) in enumerate(buildings_data):
            self.buildings_list.setItem(i, 0, QTableWidgetItem(typ))
            self.buildings_list.setItem(i, 1, QTableWidgetItem(nb))
            self.buildings_list.setItem(i, 2, QTableWidgetItem(surface))
            self.buildings_list.setItem(i, 3, QTableWidgetItem(etages))
        
        # Ajuster la largeur des colonnes
        self.buildings_list.resizeColumnsToContents()
    
    def update_all(self):
        """Met à jour toutes les données"""
        self.show_sample_map()
        self.update_stats()
        self.update_buildings()
        self.status_bar.showMessage("✅ Données mises à jour")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Palette sombre
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
    app.setPalette(palette)
    
    window = OSMDataViewer()
    window.show()
    sys.exit(app.exec())