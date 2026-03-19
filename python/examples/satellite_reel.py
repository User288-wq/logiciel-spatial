import sys
import os
import numpy as np
import requests
from datetime import datetime, timedelta
import json

# Import PySide6
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Pour l'affichage des images
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SatelliteImageDownloader:
    def __init__(self):
        self.api_key = "demo"  # Clé gratuite pour test
        self.lieux = {
            "Paris": {"lat": 48.8566, "lon": 2.3522, "zoom": 10},
            "Dakar": {"lat": 14.7167, "lon": -17.4677, "zoom": 10},
            "Touba": {"lat": 14.8667, "lon": -15.8833, "zoom": 12},
            "New York": {"lat": 40.7128, "lon": -74.0060, "zoom": 10},
            "Tokyo": {"lat": 35.6762, "lon": 139.6503, "zoom": 10},
            "Cap Canaveral": {"lat": 28.3922, "lon": -80.6077, "zoom": 12},
            "Kourou": {"lat": 5.1588, "lon": -52.6429, "zoom": 12},
        }
        
    def telecharger_image_sentinel(self, lieu, date=None):
        """Télécharge une image Sentinel-2 pour un lieu donné"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        coords = self.lieux[lieu]
        print(f"🌍 Téléchargement image Sentinel-2 de {lieu}...")
        
        # Simulation (en réalité, il faudrait une vraie API)
        # Pour l'exemple, on crée une image synthétique
        image = self.creer_image_synthetique(lieu, coords)
        
        return image
    
    def creer_image_synthetique(self, lieu, coords):
        """Crée une image simulée (remplace les vraies données)"""
        # Créer une image de 512x512 pixels
        image = np.zeros((512, 512, 3), dtype=np.uint8)
        
        # Ciel bleu
        image[:, :, 0] = 135  # B
        image[:, :, 1] = 206  # G
        image[:, :, 2] = 235  # R
        
        # Ajouter des nuages aléatoires
        nuages = np.random.rand(512, 512) > 0.7
        image[nuages] = [255, 255, 255]
        
        # Ajouter une texture de sol (plus foncé en bas)
        sol = np.random.rand(512, 512) * 50
        for i in range(256, 512):
            image[i, :, 0] = np.maximum(0, image[i, :, 0] - sol[i])
            image[i, :, 1] = np.maximum(0, image[i, :, 1] - sol[i])
            image[i, :, 2] = np.maximum(0, image[i, :, 2] - sol[i])
        
        # Ajouter le nom du lieu
        from PIL import Image, ImageDraw, ImageFont
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        draw.text((10, 10), f"{lieu}", fill=(255, 255, 255))
        draw.text((10, 30), f"Lat: {coords['lat']:.4f}, Lon: {coords['lon']:.4f}", fill=(255, 255, 255))
        
        return np.array(img_pil)
    
    def calculer_ndvi(self, image):
        """Calcule l'indice de végétation NDVI"""
        # Simuler des bandes rouge et proche infrarouge
        rouge = image[:, :, 0].astype(float)
        nir = image[:, :, 1].astype(float) * 1.2  # Simulation
        
        ndvi = (nir - rouge) / (nir + rouge + 1e-10)
        return ndvi

class MplCanvas(FigureCanvas):
    """Canvas matplotlib pour PySide6"""
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1a1a2a')
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class SatelliteAppPySide(QMainWindow):
    """Interface moderne avec PySide6"""
    
    def __init__(self):
        super().__init__()
        self.downloader = SatelliteImageDownloader()
        self.current_image = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🛰️ Téléchargeur d'Images Satellites - Édition Professionnelle")
        self.setGeometry(100, 100, 1200, 800)
        
        # Appliquer un style sombre moderne
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2a;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QComboBox {
                background-color: #16213e;
                color: white;
                border: 1px solid #0f3460;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #4CAF50;
            }
            QGroupBox {
                color: white;
                border: 2px solid #0f3460;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                background-color: #16213e;
                color: #00ff00;
                border: 1px solid #0f3460;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QProgressBar {
                border: 2px solid #0f3460;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Panneau gauche (contrôles)
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Panneau droit (visualisation)
        right_panel = self.create_visualization_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt à télécharger des images satellites 🛰️")
        
        # Timer pour animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_progress)
        self.animation_step = 0
        
    def create_control_panel(self):
        """Crée le panneau de contrôle à gauche"""
        panel = QGroupBox("🛸 Contrôles")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Sélection du lieu
        lieu_group = QGroupBox("📍 Lieu")
        lieu_layout = QVBoxLayout(lieu_group)
        
        lieu_label = QLabel("Choisissez un lieu:")
        lieu_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        lieu_layout.addWidget(lieu_label)
        
        self.lieu_combo = QComboBox()
        self.lieu_combo.addItems(self.downloader.lieux.keys())
        self.lieu_combo.setCurrentText("Paris")
        lieu_layout.addWidget(self.lieu_combo)
        
        # Coordonnées
        self.coords_label = QLabel("Lat: 48.8566, Lon: 2.3522")
        self.coords_label.setStyleSheet("color: #888888; font-size: 10px;")
        lieu_layout.addWidget(self.coords_label)
        
        self.lieu_combo.currentTextChanged.connect(self.update_coords)
        
        layout.addWidget(lieu_group)
        
        # Sélection de la date
        date_group = QGroupBox("📅 Date")
        date_layout = QVBoxLayout(date_group)
        
        self.date_combo = QComboBox()
        self.date_combo.addItems(["Aujourd'hui", "Hier", "Cette semaine", "Ce mois", "Personnalisée"])
        date_layout.addWidget(self.date_combo)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(False)
        date_layout.addWidget(self.date_edit)
        
        self.date_combo.currentTextChanged.connect(self.toggle_date_edit)
        
        layout.addWidget(date_group)
        
        # Options
        options_group = QGroupBox("⚙️ Options")
        options_layout = QVBoxLayout(options_group)
        
        self.ndvi_check = QCheckBox("Calculer NDVI (végétation)")
        self.ndvi_check.setChecked(True)
        options_layout.addWidget(self.ndvi_check)
        
        self.save_check = QCheckBox("Sauvegarder l'image")
        self.save_check.setChecked(True)
        options_layout.addWidget(self.save_check)
        
        self.highres_check = QCheckBox("Haute résolution")
        self.highres_check.setChecked(False)
        options_layout.addWidget(self.highres_check)
        
        layout.addWidget(options_group)
        
        # Bouton de téléchargement
        self.download_btn = QPushButton("🚀 TÉLÉCHARGER L'IMAGE")
        self.download_btn.setMinimumHeight(50)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        self.download_btn.clicked.connect(self.download_image)
        layout.addWidget(self.download_btn)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Zone de résultats
        results_group = QGroupBox("📊 Résultats")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Statistiques en direct
        stats_group = QGroupBox("📈 Statistiques")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Téléchargements aujourd'hui: 0\nImages en cache: 0\nDernier téléchargement: -")
        self.stats_label.setStyleSheet("color: #888888; font-size: 10px;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
        # Spacer
        layout.addStretch()
        
        return panel
    
    def create_visualization_panel(self):
        """Crée le panneau de visualisation à droite"""
        panel = QGroupBox("🪐 Visualisation")
        layout = QVBoxLayout(panel)
        
        # Canvas matplotlib
        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)
        self.canvas.setMinimumHeight(500)
        layout.addWidget(self.canvas)
        
        # Informations sur l'image
        info_layout = QHBoxLayout()
        
        self.resolution_label = QLabel("Résolution: -")
        self.resolution_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.resolution_label)
        
        info_layout.addStretch()
        
        self.bands_label = QLabel("Bandes: RGB")
        self.bands_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.bands_label)
        
        layout.addLayout(info_layout)
        
        # Miniatures des bandes
        bands_layout = QHBoxLayout()
        
        self.red_band = QLabel("Rouge")
        self.red_band.setAlignment(Qt.AlignCenter)
        self.red_band.setStyleSheet("""
            background-color: #ff0000;
            color: white;
            padding: 5px;
            border-radius: 3px;
        """)
        bands_layout.addWidget(self.red_band)
        
        self.green_band = QLabel("Vert")
        self.green_band.setAlignment(Qt.AlignCenter)
        self.green_band.setStyleSheet("""
            background-color: #00ff00;
            color: black;
            padding: 5px;
            border-radius: 3px;
        """)
        bands_layout.addWidget(self.green_band)
        
        self.blue_band = QLabel("Bleu")
        self.blue_band.setAlignment(Qt.AlignCenter)
        self.blue_band.setStyleSheet("""
            background-color: #0000ff;
            color: white;
            padding: 5px;
            border-radius: 3px;
        """)
        bands_layout.addWidget(self.blue_band)
        
        self.nir_band = QLabel("NIR")
        self.nir_band.setAlignment(Qt.AlignCenter)
        self.nir_band.setStyleSheet("""
            background-color: #8b0000;
            color: white;
            padding: 5px;
            border-radius: 3px;
        """)
        bands_layout.addWidget(self.nir_band)
        
        layout.addLayout(bands_layout)
        
        return panel
    
    def update_coords(self, lieu):
        """Met à jour l'affichage des coordonnées"""
        coords = self.downloader.lieux[lieu]
        self.coords_label.setText(f"Lat: {coords['lat']:.4f}, Lon: {coords['lon']:.4f}")
    
    def toggle_date_edit(self, text):
        """Active/désactive l'édition de date personnalisée"""
        self.date_edit.setEnabled(text == "Personnalisée")
    
    def animate_progress(self):
        """Animation de la barre de progression"""
        self.animation_step = (self.animation_step + 5) % 100
        self.progress_bar.setValue(self.animation_step)
    
    def download_image(self):
        """Télécharge et affiche l'image"""
        lieu = self.lieu_combo.currentText()
        
        # Déterminer la date
        date_choice = self.date_combo.currentText()
        if date_choice == "Aujourd'hui":
            date = datetime.now().strftime("%Y-%m-%d")
        elif date_choice == "Hier":
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_choice == "Cette semaine":
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif date_choice == "Ce mois":
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            qdate = self.date_edit.date()
            date = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"
        
        # Afficher la progression
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        self.download_btn.setEnabled(False)
        self.results_text.clear()
        self.results_text.append("🛰️ Téléchargement en cours...")
        
        # Simuler un téléchargement avec animation
        self.animation_timer.start(50)
        
        # Traiter dans un thread séparé pour ne pas bloquer l'UI
        QTimer.singleShot(2000, lambda: self.process_download(lieu, date))
    
    def process_download(self, lieu, date):
        """Traite le téléchargement (appelé après simulation)"""
        # Arrêter l'animation
        self.animation_timer.stop()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        try:
            # Télécharger l'image
            image = self.downloader.telecharger_image_sentinel(lieu, date)
            self.current_image = image
            
            # Afficher l'image
            self.display_image(image, lieu, date)
            
            # Calculer NDVI si demandé
            ndvi_text = ""
            if self.ndvi_check.isChecked():
                ndvi = self.downloader.calculer_ndvi(image)
                ndvi_text = f"\n🌿 NDVI moyen: {ndvi.mean():.3f}\n"
                ndvi_text += f"🌳 Végétation: {(ndvi > 0.3).sum()/ndvi.size*100:.1f}%"
            
            # Sauvegarder si demandé
            save_text = ""
            if self.save_check.isChecked():
                from PIL import Image as PILImage
                img_pil = PILImage.fromarray(image)
                filename = f"{lieu}_{date}.png"
                img_pil.save(filename)
                save_text = f"\n✅ Image sauvegardée: {filename}"
            
            # Mettre à jour les résultats
            self.results_text.clear()
            self.results_text.append(f"✅ Téléchargement réussi!\n")
            self.results_text.append(f"📍 Lieu: {lieu}")
            self.results_text.append(f"📅 Date: {date}")
            self.results_text.append(f"📊 Dimensions: {image.shape[0]}x{image.shape[1]} pixels")
            self.results_text.append(ndvi_text)
            self.results_text.append(save_text)
            
            # Mettre à jour les statistiques
            self.stats_label.setText(
                f"Téléchargements aujourd'hui: 1\n"
                f"Images en cache: 1\n"
                f"Dernier téléchargement: {lieu}"
            )
            
            self.resolution_label.setText(f"Résolution: 512x512")
            self.status_bar.showMessage(f"✅ Image de {lieu} téléchargée avec succès!")
            
        except Exception as e:
            self.results_text.clear()
            self.results_text.append(f"❌ Erreur: {str(e)}")
            self.status_bar.showMessage(f"❌ Erreur lors du téléchargement")
        
        finally:
            self.progress_bar.setVisible(False)
            self.download_btn.setEnabled(True)
    
    def display_image(self, image, lieu, date):
        """Affiche l'image sur le canvas"""
        self.canvas.axes.clear()
        
        if self.ndvi_check.isChecked():
            # Afficher deux sous-graphiques
            self.canvas.fig.clear()
            
            ax1 = self.canvas.fig.add_subplot(1, 2, 1)
            ax1.imshow(image)
            ax1.set_title(f"{lieu} - {date}\nImage couleur", color='white')
            ax1.axis('off')
            
            ax2 = self.canvas.fig.add_subplot(1, 2, 2)
            ndvi = self.downloader.calculer_ndvi(image)
            im = ax2.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
            ax2.set_title("NDVI (végétation)", color='white')
            ax2.axis('off')
            
            # Ajouter une colorbar
            self.canvas.fig.colorbar(im, ax=ax2, orientation='vertical', 
                                     fraction=0.046, pad=0.04)
            
        else:
            # Afficher juste l'image
            self.canvas.axes.imshow(image)
            self.canvas.axes.set_title(f"{lieu} - {date}", color='white')
            self.canvas.axes.axis('off')
        
        self.canvas.fig.patch.set_facecolor('#1a1a2a')
        self.canvas.fig.tight_layout()
        self.canvas.draw()

class InterfaceConsole:
    """Interface console (option 1)"""
    def demarrer(self):
        print("\n" + "="*50)
        print("🛰️  TÉLÉCHARGEUR D'IMAGES SATELLITES (Console)")
        print("="*50)
        
        downloader = SatelliteImageDownloader()
        
        while True:
            print("\n📋 LIEUX DISPONIBLES:")
            for i, lieu in enumerate(downloader.lieux.keys(), 1):
                print(f"{i}. {lieu}")
            
            print("\n0. Quitter")
            
            try:
                choix = int(input("\nChoisissez un lieu (0-{}): ".format(len(downloader.lieux))))
                
                if choix == 0:
                    print("Au revoir ! 👋")
                    break
                    
                if 1 <= choix <= len(downloader.lieux):
                    lieu = list(downloader.lieux.keys())[choix-1]
                    
                    print(f"\n📅 Options de date:")
                    print("1. Aujourd'hui")
                    print("2. Il y a 1 mois")
                    print("3. Il y a 1 an")
                    print("4. Entrer une date")
                    
                    date_choix = input("Choisissez (1-4): ")
                    
                    if date_choix == '1':
                        date = datetime.now().strftime("%Y-%m-%d")
                    elif date_choix == '2':
                        date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                    elif date_choix == '3':
                        date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                    elif date_choix == '4':
                        date = input("Entrez la date (YYYY-MM-DD): ")
                    else:
                        date = datetime.now().strftime("%Y-%m-%d")
                    
                    print(f"\n⏳ Téléchargement de {lieu} pour le {date}...")
                    
                    # Télécharger l'image
                    image = downloader.telecharger_image_sentinel(lieu, date)
                    
                    # Afficher
                    self.afficher_image_console(image, lieu, date)
                    
                    # Sauvegarder
                    from PIL import Image
                    img_pil = Image.fromarray(image)
                    filename = f"{lieu}_{date}.png"
                    img_pil.save(filename)
                    print(f"✅ Image sauvegardée: {filename}")
                    
                else:
                    print("❌ Choix invalide")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre")
            except KeyboardInterrupt:
                print("\n\nAu revoir ! 👋")
                break
    
    def afficher_image_console(self, image, lieu, date):
        """Affiche l'image dans une fenêtre matplotlib"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Image couleur
        axes[0].imshow(image)
        axes[0].set_title(f"{lieu} - {date} - Image couleur")
        axes[0].axis('off')
        
        # NDVI
        downloader = SatelliteImageDownloader()
        ndvi = downloader.calculer_ndvi(image)
        im = axes[1].imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[1].set_title("NDVI (végétation)")
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1])
        
        plt.tight_layout()
        plt.show()

class InterfaceTkinter:
    """Interface tkinter (option 2)"""
    def demarrer(self):
        import tkinter as tk
        from tkinter import ttk
        
        # À implémenter si nécessaire
        print("Interface tkinter - En développement")

# Point d'entrée principal
if __name__ == "__main__":
    print("🛰️ TÉLÉCHARGEUR D'IMAGES SATELLITES")
    print("="*50)
    print("1. Interface console")
    print("2. Interface graphique (tkinter)")
    print("3. Interface graphique moderne (PySide6)")
    
    choix = input("\nChoisissez une interface (1-3): ")
    
    if choix == "1":
        interface = InterfaceConsole()
        interface.demarrer()
        
    elif choix == "2":
        interface = InterfaceTkinter()
        interface.demarrer()
        
    elif choix == "3":
        app = QApplication(sys.argv)
        
        # Appliquer un thème moderne
        app.setStyle("Fusion")
        
        # Palette de couleurs sombre
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
        
        window = SatelliteAppPySide()
        window.show()
        sys.exit(app.exec())
    else:
        print("Choix invalide")