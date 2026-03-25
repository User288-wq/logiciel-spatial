# -*- coding: utf-8 -*-
"""
Styles et thèmes JOMAN GIS - UI Avancée
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont, QLinearGradient, QBrush

class JomanTheme:
    """Gestionnaire de thèmes JOMAN GIS"""
    
    # Thème sombre (par défaut)
    DARK_THEME = {
        'name': 'Sombre JOMAN',
        'window': '#1a1a2a',
        'window_text': '#ffffff',
        'base': '#16213e',
        'alternate_base': '#0f3460',
        'text': '#ffffff',
        'button': '#4CAF50',
        'button_text': '#ffffff',
        'highlight': '#4CAF50',
        'highlight_text': '#ffffff',
        'border': '#333333',
        'grid': '#2d2d2d',
        'tooltip': '#2d2d2d',
        'tooltip_text': '#ffffff',
        'accent1': '#4CAF50',
        'accent2': '#FFA500',
        'accent3': '#2196F3',
        'accent4': '#9C27B0',
    }
    
    # Thème clair
    LIGHT_THEME = {
        'name': 'Clair JOMAN',
        'window': '#f5f5f5',
        'window_text': '#333333',
        'base': '#ffffff',
        'alternate_base': '#f8f9fa',
        'text': '#333333',
        'button': '#4CAF50',
        'button_text': '#ffffff',
        'highlight': '#4CAF50',
        'highlight_text': '#ffffff',
        'border': '#dee2e6',
        'grid': '#e9ecef',
        'tooltip': '#ffffff',
        'tooltip_text': '#333333',
        'accent1': '#4CAF50',
        'accent2': '#FFA500',
        'accent3': '#2196F3',
        'accent4': '#9C27B0',
    }
    
    # Thème bleu professionnel
    BLUE_THEME = {
        'name': 'Bleu JOMAN',
        'window': '#0a192f',
        'window_text': '#ffffff',
        'base': '#0a192f',
        'alternate_base': '#112240',
        'text': '#ffffff',
        'button': '#2196F3',
        'button_text': '#ffffff',
        'highlight': '#2196F3',
        'highlight_text': '#ffffff',
        'border': '#233554',
        'grid': '#112240',
        'tooltip': '#112240',
        'tooltip_text': '#ffffff',
        'accent1': '#2196F3',
        'accent2': '#64B5F6',
        'accent3': '#FFA500',
        'accent4': '#9C27B0',
    }
    
    # Thème vert nature
    GREEN_THEME = {
        'name': 'Vert JOMAN',
        'window': '#1b4d1b',
        'window_text': '#ffffff',
        'base': '#1b4d1b',
        'alternate_base': '#2e6b2e',
        'text': '#ffffff',
        'button': '#4CAF50',
        'button_text': '#ffffff',
        'highlight': '#4CAF50',
        'highlight_text': '#ffffff',
        'border': '#3d8f3d',
        'grid': '#2e6b2e',
        'tooltip': '#2e6b2e',
        'tooltip_text': '#ffffff',
        'accent1': '#4CAF50',
        'accent2': '#8BC34A',
        'accent3': '#FFC107',
        'accent4': '#FF9800',
    }
    
    THEMES = {
        'dark': DARK_THEME,
        'light': LIGHT_THEME,
        'blue': BLUE_THEME,
        'green': GREEN_THEME,
    }
    
    def __init__(self):
        self.current_theme = 'dark'
    
    def apply_theme(self, app, theme_name='dark'):
        """Applique un thème à l'application"""
        self.current_theme = theme_name
        theme = self.THEMES.get(theme_name, self.DARK_THEME)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme['window']))
        palette.setColor(QPalette.WindowText, QColor(theme['window_text']))
        palette.setColor(QPalette.Base, QColor(theme['base']))
        palette.setColor(QPalette.AlternateBase, QColor(theme['alternate_base']))
        palette.setColor(QPalette.Text, QColor(theme['text']))
        palette.setColor(QPalette.Button, QColor(theme['button']))
        palette.setColor(QPalette.ButtonText, QColor(theme['button_text']))
        palette.setColor(QPalette.Highlight, QColor(theme['highlight']))
        palette.setColor(QPalette.HighlightedText, QColor(theme['highlight_text']))
        palette.setColor(QPalette.ToolTipBase, QColor(theme['tooltip']))
        palette.setColor(QPalette.ToolTipText, QColor(theme['tooltip_text']))
        
        app.setPalette(palette)
        
        # StyleSheet avancé
        style = f"""
        QMainWindow {{
            background-color: {theme['window']};
        }}
        QMenuBar {{
            background-color: {theme['alternate_base']};
            color: {theme['window_text']};
            border-bottom: 1px solid {theme['border']};
        }}
        QMenuBar::item:selected {{
            background-color: {theme['highlight']};
            color: {theme['highlight_text']};
        }}
        QMenu {{
            background-color: {theme['alternate_base']};
            color: {theme['window_text']};
            border: 1px solid {theme['border']};
        }}
        QMenu::item:selected {{
            background-color: {theme['highlight']};
            color: {theme['highlight_text']};
        }}
        QToolBar {{
            background-color: {theme['alternate_base']};
            border: none;
            border-bottom: 1px solid {theme['border']};
            spacing: 5px;
            padding: 5px;
        }}
        QToolBar::separator {{
            width: 1px;
            background-color: {theme['border']};
            margin: 5px;
        }}
        QPushButton {{
            background-color: {theme['button']};
            color: {theme['button_text']};
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {theme['accent2']};
        }}
        QPushButton:pressed {{
            background-color: {theme['accent3']};
        }}
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {theme['base']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            outline: none;
        }}
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {theme['highlight']};
            color: {theme['highlight_text']};
        }}
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {theme['alternate_base']};
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {theme['border']};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {theme['accent1']};
        }}
        QTabWidget::pane {{
            border: 1px solid {theme['border']};
            background-color: {theme['base']};
        }}
        QTabBar::tab {{
            background-color: {theme['alternate_base']};
            color: {theme['text']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme['highlight']};
            color: {theme['highlight_text']};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {theme['button']};
        }}
        QScrollBar:vertical {{
            background-color: {theme['alternate_base']};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {theme['highlight']};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['accent2']};
        }}
        QStatusBar {{
            background-color: {theme['alternate_base']};
            color: {theme['text']};
            border-top: 1px solid {theme['border']};
        }}
        QDockWidget::title {{
            background-color: {theme['alternate_base']};
            padding: 5px;
            border-bottom: 1px solid {theme['border']};
        }}
        QProgressBar {{
            border: 1px solid {theme['border']};
            border-radius: 3px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {theme['highlight']};
            border-radius: 3px;
        }}
        """
        app.setStyleSheet(style)
    
    def get_theme_names(self):
        return list(self.THEMES.keys())
    
    def get_theme_colors(self):
        return self.THEMES[self.current_theme]

joman_theme = JomanTheme()
