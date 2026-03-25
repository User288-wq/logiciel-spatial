# -*- coding: utf-8 -*-
"""
Widgets personnalisés JOMAN GIS
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class JomanSearchBar(QLineEdit):
    """Barre de recherche comme dans QGIS"""
    
    search_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("🔍 Rechercher un lieu, une couche...")
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border-radius: 20px;
                border: 1px solid #dee2e6;
                background-color: white;
            }
        """)
        self.returnPressed.connect(self.on_search)
    
    def on_search(self):
        self.search_requested.emit(self.text())

class JomanColorButton(QPushButton):
    """Bouton de sélection de couleur"""
    
    color_changed = Signal(QColor)
    
    def __init__(self, color=QColor(76, 175, 80), parent=None):
        super().__init__(parent)
        self.current_color = color
        self.update_style()
        self.clicked.connect(self.choose_color)
    
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px;
                min-width: 50px;
            }}
            QPushButton:hover {{
                border: 2px solid white;
            }}
        """)
    
    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Choisir une couleur JOMAN")
        if color.isValid():
            self.current_color = color
            self.update_style()
            self.color_changed.emit(color)
    
    def get_color(self):
        return self.current_color

class JomanProgressBar(QProgressBar):
    """Barre de progression animée"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #FFA500);
                border-radius: 5px;
            }
        """)
    
    def start_task(self, message="Chargement..."):
        self.setVisible(True)
        self.setValue(0)
        self.setFormat(message)
        self.show()
    
    def update_progress(self, value, message=None):
        self.setValue(value)
        if message:
            self.setFormat(message)
    
    def finish_task(self):
        self.setValue(100)
        QTimer.singleShot(500, self.hide)

class JomanInfoPanel(QWidget):
    """Panneau d'information flottant"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()
    
    def setup_ui(self):
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            JomanInfoPanel {
                background-color: #2d2d2d;
                border: 1px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.title_label)
        
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        layout.addWidget(self.content_label)
        
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
    
    def show_info(self, title, content, pos):
        self.title_label.setText(title)
        self.content_label.setText(content)
        self.move(pos)
        self.show()
        QTimer.singleShot(5000, self.hide)

class JomanChartWidget(QWidget):
    """Widget de graphiques statistiques"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils du graphique
        toolbar = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Histogramme", "Camembert", "Courbe", "Barres"])
        self.type_combo.currentTextChanged.connect(self.change_chart_type)
        toolbar.addWidget(QLabel("Type:"))
        toolbar.addWidget(self.type_combo)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Zone du graphique
        self.figure = Figure(figsize=(5, 3), facecolor='#f8f9fa')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def set_data(self, data, labels, title="Statistiques"):
        self.data = data
        self.labels = labels
        self.title = title
        self.draw_chart()
    
    def draw_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        chart_type = self.type_combo.currentText()
        
        if chart_type == "Histogramme":
            ax.bar(self.labels, self.data, color='#4CAF50')
        elif chart_type == "Camembert":
            ax.pie(self.data, labels=self.labels, autopct='%1.1f%%')
        elif chart_type == "Barres":
            ax.barh(self.labels, self.data, color='#FFA500')
        else:
            ax.plot(self.labels, self.data, marker='o', color='#2196F3', linewidth=2)
        
        ax.set_title(self.title)
        ax.set_facecolor('#f8f9fa')
        self.canvas.draw()
    
    def change_chart_type(self):
        self.draw_chart()

class JomanDockWidget(QDockWidget):
    """Dock widget amélioré avec animation"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.setStyleSheet("""
            QDockWidget::title {
                background-color: #2d2d2d;
                padding: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
    
    def animate_show(self):
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        self.show()
    
    def animate_hide(self):
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.finished.connect(self.hide)
        animation.start()
