# -*- coding: utf-8 -*-
"""
Sémiologie graphique JOMAN GIS
Styles, symboles, couleurs, étiquettes - Comme dans QGIS
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MPLPolygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, to_rgba, to_hex
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# ============================================================================
# PALETTES DE COULEURS PROFESSIONNELLES
# ============================================================================

class JomanColorPalettes:
    """Palettes de couleurs professionnelles pour cartographie"""
    
    # Palettes qualitatives (catégories distinctes)
    QUALITATIVE = {
        'Default': ['#4CAF50', '#FF5722', '#2196F3', '#FFC107', '#9C27B0', '#FF4081', '#00BCD4', '#CDDC39'],
        'Pastel': ['#A8E6CF', '#FFD3B5', '#FFAAA5', '#FF8B94', '#C7CEE6', '#B5EAD7', '#FFDAC1', '#E2F0CB'],
        'Vibrant': ['#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', '#448AFF', '#40C4FF', '#18FFFF'],
        'Earth': ['#8D6E63', '#795548', '#A1887F', '#BCAAA4', '#D7CCC8', '#F5F5F5', '#EFEBE9', '#E0E0E0'],
        'Ocean': ['#01579B', '#0288D1', '#03A9F4', '#4FC3F7', '#81D4FA', '#B3E5FC', '#E1F5FE', '#F0F8FF'],
        'Forest': ['#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7'],
        'Sunset': ['#FF6D00', '#FF8F00', '#FFA000', '#FFB300', '#FFC107', '#FFCA28', '#FFD54F', '#FFE082'],
        'Metro': ['#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#009688', '#4CAF50', '#FF9800'],
    }
    
    # Palettes séquentielles (dégradés)
    SEQUENTIAL = {
        'Blues': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5', '#084594'],
        'Greens': ['#F7FCF5', '#E5F5E0', '#C7E9C0', '#A1D99B', '#74C476', '#41AB5D', '#238B45', '#005A32'],
        'Reds': ['#FFF5F0', '#FEE0D2', '#FCBBA1', '#FC9272', '#FB6A4A', '#EF3B2C', '#CB181D', '#99000D'],
        'Oranges': ['#FFF5EB', '#FEE6CE', '#FDD0A2', '#FDAE6B', '#FD8D3C', '#F16913', '#D94801', '#8C2D04'],
        'Purples': ['#FCFBFD', '#EFEDF5', '#DADAEB', '#BCBDDC', '#9E9AC8', '#807DBA', '#6A51A3', '#4A148C'],
        'Greys': ['#FFFFFF', '#F0F0F0', '#D9D9D9', '#BDBDBD', '#969696', '#737373', '#525252', '#252525'],
    }
    
    # Palettes divergentes (pour différences)
    DIVERGING = {
        'RdYlGn': ['#D73027', '#F46D43', '#FDAE61', '#FEE08B', '#FFFFBF', '#D9EF8B', '#A6D96A', '#66BD63', '#1A9850'],
        'RdBu': ['#B2182B', '#EF8A62', '#FDDBC7', '#F7F7F7', '#D1E5F0', '#67A9CF', '#2166AC'],
        'Spectral': ['#9E0142', '#D53E4F', '#F46D43', '#FDAE61', '#FEE08B', '#FFFFBF', '#E6F598', '#ABDDA4', '#66C2A5', '#3288BD', '#5E4FA2'],
        'BrBG': ['#543005', '#8C510A', '#BF812D', '#DFC27D', '#F6E8C3', '#F5F5F5', '#C7EAE5', '#80CDC1', '#35978F', '#01665E', '#003C30'],
    }
    
    # Palettes thématiques
    THEMATIC = {
        'Population': ['#FEF0D9', '#FDD49E', '#FDBB84', '#FC8D59', '#EF6548', '#D7301F', '#B30000', '#7F0000'],
        'Altitude': ['#2C7FB8', '#4A9FCA', '#6DBFDC', '#8FDFEE', '#B1FFE5', '#D9FFC9', '#FFFFA3', '#FFD966', '#FF9933', '#FF3300'],
        'Temperature': ['#313695', '#4575B4', '#74ADD1', '#ABD9E9', '#E0F3F8', '#FFFFBF', '#FEE090', '#FDAE61', '#F46D43', '#D73027', '#A50026'],
        'Precipitation': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5', '#08519C', '#08306B'],
    }
    
    @classmethod
    def get_palette(cls, name):
        if name in cls.QUALITATIVE:
            return cls.QUALITATIVE[name]
        elif name in cls.SEQUENTIAL:
            return cls.SEQUENTIAL[name]
        elif name in cls.DIVERGING:
            return cls.DIVERGING[name]
        elif name in cls.THEMATIC:
            return cls.THEMATIC[name]
        return cls.QUALITATIVE['Default']
    
    @classmethod
    def get_all_palettes(cls):
        result = []
        for name in cls.QUALITATIVE.keys():
            result.append(('Qualitative', name))
        for name in cls.SEQUENTIAL.keys():
            result.append(('Sequential', name))
        for name in cls.DIVERGING.keys():
            result.append(('Diverging', name))
        for name in cls.THEMATIC.keys():
            result.append(('Thematic', name))
        return result

# ============================================================================
# SYMBOLOGIE POUR POINTS, LIGNES, POLYGONES
# ============================================================================

class JomanSymbol:
    """Classe de base pour les symboles"""
    
    def __init__(self):
        self.color = '#4CAF50'
        self.opacity = 1.0
        self.size = 1.0
    
    def to_dict(self):
        return {'color': self.color, 'opacity': self.opacity, 'size': self.size}

class JomanPointSymbol(JomanSymbol):
    """Symbole pour les points"""
    
    SYMBOLS = ['o', 's', '^', 'v', 'D', 'p', '*', 'h', '+', 'x', '|', '_', '1', '2', '3', '4']
    SYMBOL_NAMES = ['Cercle', 'Carré', 'Triangle haut', 'Triangle bas', 'Losange', 'Pentagone', 'Étoile', 'Hexagone', 'Croix', 'X', 'Ligne verticale', 'Ligne horizontale']
    
    def __init__(self):
        super().__init__()
        self.marker = 'o'
        self.marker_size = 8
        self.edge_color = '#FFFFFF'
        self.edge_width = 0.5
    
    def to_dict(self):
        d = super().to_dict()
        d.update({'marker': self.marker, 'marker_size': self.marker_size, 'edge_color': self.edge_color, 'edge_width': self.edge_width})
        return d

class JomanLineSymbol(JomanSymbol):
    """Symbole pour les lignes"""
    
    LINE_STYLES = ['-', '--', '-.', ':']
    LINE_STYLE_NAMES = ['Plein', 'Tiret', 'Tiret-point', 'Pointillé']
    
    def __init__(self):
        super().__init__()
        self.line_style = '-'
        self.line_width = 1.5
    
    def to_dict(self):
        d = super().to_dict()
        d.update({'line_style': self.line_style, 'line_width': self.line_width})
        return d

class JomanPolygonSymbol(JomanSymbol):
    """Symbole pour les polygones"""
    
    HATCH_STYLES = ['', '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*']
    HATCH_NAMES = ['Aucun', 'Diagonal /', 'Diagonal \\', 'Vertical', 'Horizontal', 'Croix +', 'Croix x', 'Cercle', 'Grand cercle', 'Point', 'Étoile']
    
    def __init__(self):
        super().__init__()
        self.edge_color = '#2E7D32'
        self.edge_width = 1.0
        self.hatch = ''
    
    def to_dict(self):
        d = super().to_dict()
        d.update({'edge_color': self.edge_color, 'edge_width': self.edge_width, 'hatch': self.hatch})
        return d

# ============================================================================
# STYLES D'ÉTIQUETTES
# ============================================================================

class JomanLabelStyle:
    """Style d'étiquettes comme dans QGIS"""
    
    FONTS = ['sans-serif', 'serif', 'monospace', 'cursive', 'fantasy']
    FONT_SIZES = [6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36]
    FONT_WEIGHTS = ['normal', 'bold', 'light', 'heavy']
    PLACEMENTS = ['Auto', 'Point', 'Ligne', 'Polygone', 'Centroïde']
    
    def __init__(self):
        self.field = None
        self.font_family = 'sans-serif'
        self.font_size = 10
        self.font_weight = 'normal'
        self.font_color = '#333333'
        self.buffer = True
        self.buffer_color = '#FFFFFF'
        self.buffer_size = 1
        self.background = False
        self.background_color = '#FFFFFF'
        self.background_opacity = 0.7
        self.placement = 'Auto'
        self.offset_x = 0
        self.offset_y = 0
        self.rotation = 0
        self.bold = False
        self.italic = False
    
    def to_dict(self):
        return {
            'field': self.field,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_weight': self.font_weight,
            'font_color': self.font_color,
            'buffer': self.buffer,
            'buffer_color': self.buffer_color,
            'buffer_size': self.buffer_size,
            'background': self.background,
            'background_color': self.background_color,
            'background_opacity': self.background_opacity,
            'placement': self.placement,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'rotation': self.rotation,
            'bold': self.bold,
            'italic': self.italic
        }

# ============================================================================
# WIDGET DE SÉLECTION DE SYMBOLOGIE
# ============================================================================

class JomanSymbologyWidget(QWidget):
    """Widget de sélection de symbologie"""
    
    symbology_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_type = 'Polygon'
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Type de géométrie
        layout.addWidget(QLabel("Type de géométrie:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Point', 'Ligne', 'Polygone'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        
        # Palette de couleurs
        layout.addWidget(QLabel("Palette:"))
        self.palette_combo = QComboBox()
        for cat, name in JomanColorPalettes.get_all_palettes():
            self.palette_combo.addItem(f"{cat}: {name}", name)
        self.palette_combo.currentIndexChanged.connect(self.on_palette_changed)
        layout.addWidget(self.palette_combo)
        
        # Couleur personnalisée
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setStyleSheet("background-color: #4CAF50; border: 1px solid white;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Opacité
        layout.addWidget(QLabel("Opacité:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        self.opacity_slider.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.opacity_slider)
        
        # Taille/épaisseur
        layout.addWidget(QLabel("Taille/Épaisseur:"))
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.5, 20)
        self.size_spin.setValue(5)
        self.size_spin.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.size_spin)
        
        # Symboles spécifiques au type
        self.symbol_stack = QStackedWidget()
        
        # Point symbols
        point_widget = QWidget()
        point_layout = QVBoxLayout(point_widget)
        point_layout.addWidget(QLabel("Symbole:"))
        self.symbol_combo = QComboBox()
        for i, sym in enumerate(JomanPointSymbol.SYMBOLS):
            self.symbol_combo.addItem(JomanPointSymbol.SYMBOL_NAMES[i], sym)
        self.symbol_combo.currentIndexChanged.connect(self.on_style_changed)
        point_layout.addWidget(self.symbol_combo)
        self.symbol_stack.addWidget(point_widget)
        
        # Line styles
        line_widget = QWidget()
        line_layout = QVBoxLayout(line_widget)
        line_layout.addWidget(QLabel("Style de ligne:"))
        self.line_style_combo = QComboBox()
        for i, style in enumerate(JomanLineSymbol.LINE_STYLES):
            self.line_style_combo.addItem(JomanLineSymbol.LINE_STYLE_NAMES[i], style)
        self.line_style_combo.currentIndexChanged.connect(self.on_style_changed)
        line_layout.addWidget(self.line_style_combo)
        self.symbol_stack.addWidget(line_widget)
        
        # Polygon hatches
        polygon_widget = QWidget()
        polygon_layout = QVBoxLayout(polygon_widget)
        polygon_layout.addWidget(QLabel("Hachure:"))
        self.hatch_combo = QComboBox()
        for i, hatch in enumerate(JomanPolygonSymbol.HATCH_STYLES):
            self.hatch_combo.addItem(JomanPolygonSymbol.HATCH_NAMES[i], hatch)
        self.hatch_combo.currentIndexChanged.connect(self.on_style_changed)
        polygon_layout.addWidget(self.hatch_combo)
        self.symbol_stack.addWidget(polygon_widget)
        
        layout.addWidget(self.symbol_stack)
        
        # Aperçu
        layout.addWidget(QLabel("Aperçu:"))
        self.preview = QLabel()
        self.preview.setFixedSize(100, 50)
        self.preview.setStyleSheet("background-color: #2d2d2d; border: 1px solid #4CAF50;")
        self.preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview)
        
        layout.addStretch()
        
        self.update_preview()
    
    def on_type_changed(self, type_name):
        self.current_type = type_name
        if type_name == 'Point':
            self.symbol_stack.setCurrentIndex(0)
        elif type_name == 'Ligne':
            self.symbol_stack.setCurrentIndex(1)
        else:
            self.symbol_stack.setCurrentIndex(2)
        self.update_preview()
    
    def on_palette_changed(self):
        palette_name = self.palette_combo.currentData()
        colors = JomanColorPalettes.get_palette(palette_name)
        self.color_btn.setStyleSheet(f"background-color: {colors[0]}; border: 1px solid white;")
        self.on_style_changed()
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white;")
            self.on_style_changed()
    
    def on_style_changed(self):
        self.update_preview()
        self.emit_style()
    
    def update_preview(self):
        """Met à jour l'aperçu du symbole"""
        color = self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0]
        opacity = self.opacity_slider.value() / 100
        size = self.size_spin.value()
        
        preview_text = ""
        if self.current_type == 'Point':
            sym = self.symbol_combo.currentData()
            preview_text = f"● {sym}"
        elif self.current_type == 'Ligne':
            style = self.line_style_combo.currentData()
            preview_text = f"── {style}"
        else:
            hatch = self.hatch_combo.currentData()
            preview_text = f"█ {hatch or 'Solid'}"
        
        self.preview.setText(f"{preview_text}\n{color}\n{opacity*100:.0f}%")
    
    def emit_style(self):
        """Émet le style actuel"""
        color = self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0]
        opacity = self.opacity_slider.value() / 100
        size = self.size_spin.value()
        
        style = {
            'type': self.current_type,
            'color': color,
            'opacity': opacity,
            'size': size
        }
        
        if self.current_type == 'Point':
            style['marker'] = self.symbol_combo.currentData()
            style['marker_size'] = size
        elif self.current_type == 'Ligne':
            style['line_style'] = self.line_style_combo.currentData()
            style['line_width'] = size
        else:
            style['hatch'] = self.hatch_combo.currentData()
            style['edge_width'] = size
        
        self.symbology_changed.emit(style)

# ============================================================================
# WIDGET D'ÉTIQUETTES
# ============================================================================

class JomanLabelWidget(QWidget):
    """Widget de configuration des étiquettes"""
    
    label_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Activer les étiquettes
        self.enable_check = QCheckBox("Activer les étiquettes")
        self.enable_check.toggled.connect(self.on_changed)
        layout.addWidget(self.enable_check)
        
        # Champ d'étiquetage
        layout.addWidget(QLabel("Champ:"))
        self.field_combo = QComboBox()
        self.field_combo.currentIndexChanged.connect(self.on_changed)
        layout.addWidget(self.field_combo)
        
        # Police
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Police:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(['Sans-serif', 'Serif', 'Monospace'])
        self.font_combo.currentIndexChanged.connect(self.on_changed)
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)
        
        # Taille
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Taille:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 36)
        self.size_spin.setValue(10)
        self.size_spin.valueChanged.connect(self.on_changed)
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)
        
        # Couleur
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setStyleSheet("background-color: #333333; border: 1px solid white;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        
        # Contour (buffer)
        self.buffer_check = QCheckBox("Contour du texte")
        self.buffer_check.toggled.connect(self.on_changed)
        layout.addWidget(self.buffer_check)
        
        # Placement
        layout.addWidget(QLabel("Placement:"))
        self.placement_combo = QComboBox()
        self.placement_combo.addItems(['Auto', 'Centre', 'Haut', 'Bas', 'Gauche', 'Droite'])
        self.placement_combo.currentIndexChanged.connect(self.on_changed)
        layout.addWidget(self.placement_combo)
        
        layout.addStretch()
    
    def set_fields(self, fields):
        self.field_combo.clear()
        self.field_combo.addItems(fields)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white;")
            self.on_changed()
    
    def on_changed(self):
        if not self.enable_check.isChecked():
            self.label_changed.emit({'enabled': False})
            return
        
        style = {
            'enabled': True,
            'field': self.field_combo.currentText(),
            'font': self.font_combo.currentText(),
            'size': self.size_spin.value(),
            'color': self.color_btn.styleSheet().split('background-color: ')[1].split(';')[0],
            'buffer': self.buffer_check.isChecked(),
            'placement': self.placement_combo.currentText()
        }
        self.label_changed.emit(style)

# ============================================================================
# COMPOSEUR DE MISE EN PAGE (COMME DANS QGIS)
# ============================================================================

class JomanLayoutComposer(QDialog):
    """Composeur de mise en page comme dans QGIS"""
    
    def __init__(self, map_canvas, parent=None):
        super().__init__(parent)
        self.map_canvas = map_canvas
        self.setWindowTitle("Composeur de mise en page - JOMAN GIS")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        btn_add_title = QPushButton("📝 Ajouter titre")
        btn_add_title.clicked.connect(self.add_title)
        btn_add_scalebar = QPushButton("📏 Ajouter échelle")
        btn_add_scalebar.clicked.connect(self.add_scalebar)
        btn_add_north = QPushButton("🧭 Ajouter nord")
        btn_add_north.clicked.connect(self.add_north_arrow)
        btn_add_legend = QPushButton("📖 Ajouter légende")
        btn_add_legend.clicked.connect(self.add_legend)
        btn_export = QPushButton("💾 Exporter")
        btn_export.clicked.connect(self.export_layout)
        toolbar.addWidget(btn_add_title)
        toolbar.addWidget(btn_add_scalebar)
        toolbar.addWidget(btn_add_north)
        toolbar.addWidget(btn_add_legend)
        toolbar.addStretch()
        toolbar.addWidget(btn_export)
        layout.addLayout(toolbar)
        
        # Zone de mise en page
        self.page_widget = QWidget()
        self.page_widget.setStyleSheet("background-color: white; border: 1px solid #dee2e6;")
        page_layout = QVBoxLayout(self.page_widget)
        
        # Canvas de la carte
        self.layout_canvas = FigureCanvas(self.map_canvas.figure)
        page_layout.addWidget(self.layout_canvas)
        
        layout.addWidget(self.page_widget)
        
        # Panneau de propriétés
        self.properties_panel = QGroupBox("Propriétés")
        props_layout = QVBoxLayout(self.properties_panel)
        self.props_text = QTextEdit()
        self.props_text.setMaximumHeight(150)
        props_layout.addWidget(self.props_text)
        layout.addWidget(self.properties_panel)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton("Appliquer")
        btn_apply.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_apply)
        layout.addLayout(btn_layout)
    
    def add_title(self):
        title, ok = QInputDialog.getText(self, "Ajouter un titre", "Titre de la carte:")
        if ok and title:
            self.map_canvas.ax.set_title(title, fontsize=14, fontweight='bold')
            self.map_canvas.draw()
            self.props_text.setText(f"Titre: {title}")
    
    def add_scalebar(self):
        self.map_canvas.add_scalebar()
        self.map_canvas.draw()
        self.props_text.setText("Barre d'échelle ajoutée")
    
    def add_north_arrow(self):
        self.map_canvas.add_north_arrow()
        self.map_canvas.draw()
        self.props_text.setText("Flèche nord ajoutée")
    
    def add_legend(self):
        # Récupérer les couches
        layers = []
        if hasattr(self.parent(), 'layers'):
            for layer in self.parent().layers:
                layers.append(f"{layer['type']}: {layer['name']}")
        legend_text = "Légende:\n" + "\n".join(layers)
        self.props_text.setText(legend_text)
    
    def export_layout(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exporter la mise en page", "", "PNG (*.png);;PDF (*.pdf)")
        if filename:
            self.map_canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "Export", f"Mise en page exportée vers {filename}")

# Instance globale
joman_color_palettes = JomanColorPalettes()
