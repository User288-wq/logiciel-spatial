# -*- coding: utf-8 -*-
"""
Dialogues avancés JOMAN GIS
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class JomanAboutDialog(QDialog):
    """Dialogue À propos stylisé"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos de JOMAN GIS")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Logo
        logo = QLabel("🏆")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Titre
        title = QLabel("JOMAN GIS")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("Version 5.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Description
        desc = QLabel("Logiciel de Cartographie Professionnel")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Infos
        info = QTextEdit()
        info.setReadOnly(True)
        info.setHtml("""
        <h3>Fonctionnalités</h3>
        <ul>
            <li>🗺️ Formats: SHP, GeoJSON, KML, KMZ, CSV</li>
            <li>🔍 Zoom/Pan/Vue d'ensemble</li>
            <li>📍 Sélection par clic</li>
            <li>📏 Mesure de distance</li>
            <li>⚙️ Buffer, Centroïdes, Enveloppe convexe</li>
            <li>🌍 200+ projections</li>
            <li>🎨 Thèmes personnalisables</li>
        </ul>
        <p>© 2026 - JOMAN TEAM</p>
        """)
        layout.addWidget(info)
        
        # Bouton
        btn_ok = QPushButton("Fermer")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

class JomanExportDialog(QDialog):
    """Dialogue d'export avancé"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exporter - JOMAN GIS")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Format
        layout.addWidget(QLabel("Format d'export:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "PDF", "SVG"])
        layout.addWidget(self.format_combo)
        
        # Résolution
        layout.addWidget(QLabel("Résolution (DPI):"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(300)
        layout.addWidget(self.dpi_spin)
        
        # Qualité
        layout.addWidget(QLabel("Qualité:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(90)
        layout.addWidget(self.quality_slider)
        
        # Options
        self.include_scalebar = QCheckBox("Inclure la barre d'échelle")
        self.include_scalebar.setChecked(True)
        layout.addWidget(self.include_scalebar)
        
        self.include_north_arrow = QCheckBox("Inclure la flèche nord")
        self.include_north_arrow.setChecked(True)
        layout.addWidget(self.include_north_arrow)
        
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_export = QPushButton("Exporter")
        btn_export.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_export)
        layout.addLayout(btn_layout)
    
    def get_options(self):
        return {
            'format': self.format_combo.currentText(),
            'dpi': self.dpi_spin.value(),
            'quality': self.quality_slider.value(),
            'include_scalebar': self.include_scalebar.isChecked(),
            'include_north_arrow': self.include_north_arrow.isChecked()
        }

class JomanLayerPropertiesDialog(QDialog):
    """Dialogue des propriétés de couche"""
    
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.setWindowTitle(f"Propriétés - {layer['name']}")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Général
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.addWidget(QLabel(f"Nom: {self.layer['name']}"))
        general_layout.addWidget(QLabel(f"Type: {self.layer['type']}"))
        general_layout.addWidget(QLabel(f"Entités: {len(self.layer['gdf'])}"))
        general_layout.addWidget(QLabel(f"Colonnes: {len(self.layer['gdf'].columns)}"))
        tabs.addTab(general_tab, "Général")
        
        # Style
        style_tab = QWidget()
        style_layout = QVBoxLayout(style_tab)
        style_layout.addWidget(QLabel("Couleur:"))
        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet(f"background-color: {self.layer.get('color', '#4CAF50')}")
        style_layout.addWidget(self.color_btn)
        
        style_layout.addWidget(QLabel("Opacité:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.layer.get('opacity', 70)))
        style_layout.addWidget(self.opacity_slider)
        tabs.addTab(style_tab, "Style")
        
        layout.addWidget(tabs)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Appliquer")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
