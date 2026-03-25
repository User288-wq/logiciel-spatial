# -*- coding: utf-8 -*-
"""
Module de sémiologie graphique pour la mise en page
Styles de couleurs, symboles, étiquettes comme dans QGIS
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, to_rgba
import numpy as np
import geopandas as gpd

class StyleManager:
    """Gestionnaire de styles pour la sémiologie"""
    
    # Palettes de couleurs pré-définies
    COLOR_PALETTES = {
        'Qualitative': {
            'Default': ['#4CAF50', '#FF5722', '#2196F3', '#FFC107', '#9C27B0', '#FF4081', '#00BCD4', '#CDDC39'],
            'Pastel': ['#A8E6CF', '#FFD3B5', '#FFAAA5', '#FF8B94', '#C7CEE6', '#B5EAD7', '#FFDAC1', '#E2F0CB'],
            'Vibrant': ['#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', '#448AFF', '#40C4FF', '#18FFFF'],
            'Earth': ['#8D6E63', '#795548', '#A1887F', '#BCAAA4', '#D7CCC8', '#F5F5F5', '#EFEBE9', '#E0E0E0'],
        },
        'Sequential': {
            'Blues': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5', '#084594'],
            'Greens': ['#F7FCF5', '#E5F5E0', '#C7E9C0', '#A1D99B', '#74C476', '#41AB5D', '#238B45', '#005A32'],
            'Reds': ['#FFF5F0', '#FEE0D2', '#FCBBA1', '#FC9272', '#FB6A4A', '#EF3B2C', '#CB181D', '#99000D'],
            'Purples': ['#FCFBFD', '#EFEDF5', '#DADAEB', '#BCBDDC', '#9E9AC8', '#807DBA', '#6A51A3', '#4A148C'],
        },
        'Diverging': {
            'RdYlGn': ['#D73027', '#F46D43', '#FDAE61', '#FEE08B', '#FFFFBF', '#D9EF8B', '#A6D96A', '#66BD63', '#1A9850'],
            'RdBu': ['#B2182B', '#EF8A62', '#FDDBC7', '#F7F7F7', '#D1E5F0', '#67A9CF', '#2166AC'],
            'Spectral': ['#9E0142', '#D53E4F', '#F46D43', '#FDAE61', '#FEE08B', '#FFFFBF', '#E6F598', '#ABDDA4', '#66C2A5', '#3288BD', '#5E4FA2'],
        }
    }
    
    # Symboles pour les points
    POINT_SYMBOLS = ['o', 's', '^', 'v', 'D', 'p', '*', 'h', '+', 'x', '|', '_']
    
    # Types de lignes
    LINE_STYLES = ['-', '--', '-.', ':', (0, (1, 1)), (0, (5, 5)), (0, (5, 1)), (0, (1, 5))]
    
    def __init__(self):
        self.current_style = {}
    
    def get_color(self, palette_name='Default', index=0):
        """Retourne une couleur d'une palette"""
        if palette_name in self.COLOR_PALETTES['Qualitative']:
            palette = self.COLOR_PALETTES['Qualitative'][palette_name]
            return palette[index % len(palette)]
        return '#4CAF50'
    
    def get_gradient(self, palette_name='Blues', n_colors=10):
        """Retourne un dégradé de couleurs"""
        if palette_name in self.COLOR_PALETTES['Sequential']:
            palette = self.COLOR_PALETTES['Sequential'][palette_name]
            return palette[:min(n_colors, len(palette))]
        return self.COLOR_PALETTES['Sequential']['Blues'][:n_colors]
    
    def create_style(self, layer_type, color=None, size=1, opacity=1.0, symbol='o', line_style='-'):
        """Crée un style pour une couche"""
        style = {
            'type': layer_type,
            'color': color or self.get_color('Default', 0),
            'size': size,
            'opacity': opacity,
            'symbol': symbol,
            'line_style': line_style,
            'alpha': opacity
        }
        
        if layer_type == 'Point':
            style.update({
                'marker': symbol,
                'markersize': size * 5,
                'edgecolor': 'white',
                'linewidth': 0.5
            })
        elif layer_type == 'LineString':
            style.update({
                'linestyle': line_style,
                'linewidth': size,
            })
        elif layer_type == 'Polygon':
            style.update({
                'edgecolor': 'white',
                'linewidth': 0.5,
            })
        
        return style
    
    def get_legend_patch(self, style, label):
        """Crée un patch pour la légende"""
        if style['type'] == 'Point':
            return mpatches.Patch(color=style['color'], label=label, alpha=style['alpha'])
        elif style['type'] == 'LineString':
            return mpatches.Patch(color=style['color'], label=label, alpha=style['alpha'])
        else:
            return mpatches.Patch(color=style['color'], label=label, alpha=style['alpha'])


class LabelStyle:
    """Gestionnaire de styles d'étiquettes"""
    
    FONTS = ['sans-serif', 'serif', 'monospace', 'cursive', 'fantasy']
    FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24]
    FONT_WEIGHTS = ['normal', 'bold', 'light', 'heavy']
    FONT_COLORS = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple']
    
    def __init__(self):
        self.default = {
            'font_family': 'sans-serif',
            'font_size': 10,
            'font_weight': 'normal',
            'font_color': 'black',
            'background_color': 'white',
            'background_alpha': 0.7,
            'halo': True,
            'halo_color': 'white',
            'halo_width': 1,
            'placement': 'auto',  # auto, point, line, polygon
            'offset_x': 0,
            'offset_y': 0,
            'rotation': 0,
            'bold': False,
            'italic': False
        }
    
    def get_style(self, **kwargs):
        """Retourne un style d'étiquette personnalisé"""
        style = self.default.copy()
        style.update(kwargs)
        return style
    
    def apply_to_text(self, text, ax, x, y, style):
        """Applique le style à un texte"""
        return ax.text(
            x, y, text,
            fontfamily=style['font_family'],
            fontsize=style['font_size'],
            fontweight=style['font_weight'],
            color=style['font_color'],
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor=style['background_color'],
                alpha=style['background_alpha']
            ) if style['background_color'] else None,
            rotation=style['rotation']
        )


class LayoutComposer:
    """Gestionnaire de mise en page (Print Composer comme QGIS)"""
    
    def __init__(self, figure, title="", scalebar=True, north_arrow=True, legend=True):
        self.figure = figure
        self.title = title
        self.show_scalebar = scalebar
        self.show_north_arrow = north_arrow
        self.show_legend = legend
        self.elements = []
    
    def add_title(self, text, fontsize=14, fontweight='bold', position='top'):
        """Ajoute un titre à la carte"""
        self.elements.append({
            'type': 'title',
            'text': text,
            'fontsize': fontsize,
            'fontweight': fontweight,
            'position': position
        })
    
    def add_scalebar(self, length_km=10, position='bottom-left'):
        """Ajoute une barre d'échelle"""
        self.elements.append({
            'type': 'scalebar',
            'length_km': length_km,
            'position': position
        })
    
    def add_north_arrow(self, position='top-right'):
        """Ajoute une flèche nord"""
        self.elements.append({
            'type': 'north_arrow',
            'position': position
        })
    
    def add_legend(self, items, position='bottom-right'):
        """Ajoute une légende"""
        self.elements.append({
            'type': 'legend',
            'items': items,
            'position': position
        })
    
    def add_grid(self, interval_deg=1, color='gray', alpha=0.5):
        """Ajoute une grille"""
        self.elements.append({
            'type': 'grid',
            'interval': interval_deg,
            'color': color,
            'alpha': alpha
        })
    
    def add_textbox(self, text, x, y, fontsize=10, bbox=True):
        """Ajoute une boîte de texte"""
        self.elements.append({
            'type': 'textbox',
            'text': text,
            'x': x,
            'y': y,
            'fontsize': fontsize,
            'bbox': bbox
        })
    
    def render(self, ax):
        """Applique tous les éléments de mise en page"""
        for element in self.elements:
            if element['type'] == 'title':
                if element['position'] == 'top':
                    ax.set_title(element['text'], fontsize=element['fontsize'], fontweight=element['fontweight'])
            
            elif element['type'] == 'grid':
                ax.grid(True, alpha=element['alpha'], color=element['color'], linestyle='--')
            
            elif element['type'] == 'textbox':
                bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8) if element['bbox'] else None
                ax.text(element['x'], element['y'], element['text'],
                       fontsize=element['fontsize'],
                       bbox=bbox_props,
                       transform=ax.transAxes)


# Widget de sélection de style
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QColorDialog, QPushButton, QSpinBox, QCheckBox
from PySide6.QtCore import Signal, Qt

class StyleSelectorWidget(QWidget):
    """Widget de sélection de style comme dans QGIS"""
    style_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Palette de couleurs
        layout.addWidget(QLabel("Palette:"))
        self.palette_combo = QComboBox()
        for name in StyleManager.COLOR_PALETTES['Qualitative'].keys():
            self.palette_combo.addItem(name)
        self.palette_combo.currentIndexChanged.connect(self.on_style_changed)
        layout.addWidget(self.palette_combo)
        
        # Couleur personnalisée
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur:"))
        self.color_btn = QPushButton("Choisir")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        
        # Opacité
        layout.addWidget(QLabel("Opacité:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        self.opacity_slider.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.opacity_slider)
        
        # Taille
        layout.addWidget(QLabel("Taille:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 20)
        self.size_spin.setValue(5)
        self.size_spin.valueChanged.connect(self.on_style_changed)
        layout.addWidget(self.size_spin)
        
        # Symbole (pour points)
        layout.addWidget(QLabel("Symbole:"))
        self.symbol_combo = QComboBox()
        for sym in StyleManager.POINT_SYMBOLS:
            self.symbol_combo.addItem(sym)
        self.symbol_combo.currentIndexChanged.connect(self.on_style_changed)
        layout.addWidget(self.symbol_combo)
        
        # Style de ligne
        layout.addWidget(QLabel("Style ligne:"))
        self.line_style_combo = QComboBox()
        for style in StyleManager.LINE_STYLES:
            if isinstance(style, str):
                self.line_style_combo.addItem(style)
        self.line_style_combo.currentIndexChanged.connect(self.on_style_changed)
        layout.addWidget(self.line_style_combo)
        
        layout.addStretch()
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.on_style_changed()
    
    def on_style_changed(self):
        style = {
            'palette': self.palette_combo.currentText(),
            'color': getattr(self, 'current_color', '#4CAF50'),
            'opacity': self.opacity_slider.value() / 100,
            'size': self.size_spin.value(),
            'symbol': self.symbol_combo.currentText(),
            'line_style': self.line_style_combo.currentText()
        }
        self.style_changed.emit(style)

style_manager = StyleManager()
label_style = LabelStyle()
