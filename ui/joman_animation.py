# -*- coding: utf-8 -*-
"""
Console Python intégrée - Comme dans QGIS
"""

import sys
import code
import threading
from io import StringIO

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class JomanConsole(QWidget):
    """Console Python interactive comme dans QGIS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_interpreter()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        self.btn_clear = QPushButton("🗑️ Effacer")
        self.btn_clear.clicked.connect(self.clear_console)
        self.btn_run = QPushButton("▶️ Exécuter")
        self.btn_run.clicked.connect(self.run_selection)
        self.btn_help = QPushButton("❓ Aide")
        self.btn_help.clicked.connect(self.show_help)
        toolbar.addWidget(self.btn_clear)
        toolbar.addWidget(self.btn_run)
        toolbar.addWidget(self.btn_help)
        toolbar.addStretch()
        self.lbl_status = QLabel("Prêt")
        toolbar.addWidget(self.lbl_status)
        layout.addLayout(toolbar)
        
        # Zone de sortie
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.output_area, 1)
        
        # Zone de saisie
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(">>>"))
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Entrez une commande Python...")
        self.input_line.returnPressed.connect(self.execute_command)
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 5px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
        """)
        input_layout.addWidget(self.input_line)
        layout.addLayout(input_layout)
        
        self.history = []
        self.history_index = -1
        
        # Raccourcis
        self.input_line.installEventFilter(self)
    
    def setup_interpreter(self):
        """Configure l'interpréteur Python"""
        self.interpreter = code.InteractiveInterpreter(locals())
        
        # Ajouter des variables utiles
        self.interpreter.locals['app'] = self.window()
        self.interpreter.locals['map'] = self.window().map_canvas if hasattr(self.window(), 'map_canvas') else None
        self.interpreter.locals['layers'] = self.window().layers if hasattr(self.window(), 'layers') else []
        self.interpreter.locals['current_layer'] = self.window().current_layer if hasattr(self.window(), 'current_layer') else None
        
        self.write_output("JOMAN GIS Console Python v1.0")
        self.write_output("=" * 40)
        self.write_output("Variables disponibles:")
        self.write_output("  app    - Instance de JOMAN GIS")
        self.write_output("  map    - Canvas cartographique")
        self.write_output("  layers - Liste des couches")
        self.write_output("  current_layer - Couche actuelle")
        self.write_output("")
    
    def write_output(self, text):
        """Écrit du texte dans la console"""
        self.output_area.append(text)
        self.output_area.ensureCursorVisible()
    
    def execute_command(self):
        """Exécute la commande saisie"""
        command = self.input_line.text()
        if not command:
            return
        
        # Ajouter à l'historique
        self.history.append(command)
        self.history_index = len(self.history)
        
        # Afficher la commande
        self.write_output(f">>> {command}")
        
        # Rediriger stdout
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        try:
            # Exécuter la commande
            self.interpreter.runsource(command)
            
            # Récupérer la sortie
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            
            if output:
                self.write_output(output.rstrip())
            if error:
                self.write_output(f"Erreur: {error.rstrip()}")
                self.lbl_status.setText("❌ Erreur")
            else:
                self.lbl_status.setText("✅ Exécuté")
                
        except Exception as e:
            self.write_output(f"Erreur: {e}")
            self.lbl_status.setText("❌ Erreur")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        self.input_line.clear()
        QTimer.singleShot(1000, lambda: self.lbl_status.setText("Prêt"))
    
    def run_selection(self):
        """Exécute la sélection de texte"""
        cursor = self.output_area.textCursor()
        if cursor.hasSelection():
            command = cursor.selectedText()
            self.input_line.setText(command)
            self.execute_command()
    
    def clear_console(self):
        """Efface la console"""
        self.output_area.clear()
        self.write_output("Console effacée")
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
JOMAN GIS Console Python - Aide

Commandes utiles:
  help()               - Affiche l'aide Python
  dir(app)             - Liste les attributs de l'application
  len(layers)          - Nombre de couches
  current_layer.name   - Nom de la couche actuelle
  
Variables:
  app    - Instance principale
  map    - Canvas cartographique
  layers - Liste des couches
  current_layer - Couche actuelle

Exemples:
  # Charger une couche
  app.load_file_from_path('mon_fichier.shp')
  
  # Zoom sur la couche
  map.zoom_all()
  
  # Exporter la carte
  map.export('carte.png')
"""
        self.write_output(help_text)
    
    def eventFilter(self, obj, event):
        """Filtre les événements pour l'historique"""
        if obj == self.input_line and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.history[self.history_index])
                return True
            elif event.key() == Qt.Key_Down:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input_line.setText(self.history[self.history_index])
                else:
                    self.history_index = len(self.history)
                    self.input_line.clear()
                return True
        return super().eventFilter(obj, event)

# ============================================================================
# FICHIER: ui/joman_plugins.py - Gestionnaire de plugins
# ============================================================================
@'
# -*- coding: utf-8 -*-
"""
Gestionnaire de plugins - Comme dans QGIS
"""

import os
import importlib
import inspect
from pathlib import Path

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class JomanPlugin:
    """Classe de base pour les plugins JOMAN"""
    
    def __init__(self, iface):
        self.iface = iface
        self.name = "Plugin JOMAN"
        self.version = "1.0"
    
    def initGui(self):
        pass
    
    def unload(self):
        pass
    
    def run(self):
        pass

class JomanPluginManager(QWidget):
    """Gestionnaire de plugins comme dans QGIS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = {}
        self.plugin_dir = Path.home() / ".joman_gis" / "plugins"
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.setup_ui()
        self.load_plugins()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        btn_install = QPushButton("📦 Installer un plugin")
        btn_install.clicked.connect(self.install_plugin)
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_plugins)
        toolbar.addWidget(btn_install)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Liste des plugins
        self.plugin_list = QListWidget()
        self.plugin_list.itemClicked.connect(self.on_plugin_selected)
        self.plugin_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.plugin_list)
        
        # Informations du plugin
        self.info_group = QGroupBox("Informations du plugin")
        info_layout = QVBoxLayout(self.info_group)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        layout.addWidget(self.info_group)
        
        # Actions
        btn_layout = QHBoxLayout()
        self.btn_enable = QPushButton("Activer")
        self.btn_enable.clicked.connect(self.toggle_plugin)
        self.btn_uninstall = QPushButton("Désinstaller")
        self.btn_uninstall.clicked.connect(self.uninstall_plugin)
        btn_layout.addWidget(self.btn_enable)
        btn_layout.addWidget(self.btn_uninstall)
        layout.addLayout(btn_layout)
    
    def load_plugins(self):
        """Charge tous les plugins disponibles"""
        self.plugin_list.clear()
        self.plugins.clear()
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, JomanPlugin) and obj != JomanPlugin:
                        plugin = obj(self.parent())
                        self.plugins[plugin_file.stem] = {
                            'module': module,
                            'plugin': plugin,
                            'enabled': False
                        }
                        item = QListWidgetItem(f"📦 {plugin.name} v{plugin.version}")
                        item.setData(Qt.UserRole, plugin_file.stem)
                        self.plugin_list.addItem(item)
            except Exception as e:
                print(f"Erreur chargement plugin {plugin_file}: {e}")
    
    def install_plugin(self):
        """Installe un nouveau plugin"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Installer un plugin", "", "Python (*.py);;ZIP Archive (*.zip)"
        )
        if filename:
            import shutil
            dest = self.plugin_dir / os.path.basename(filename)
            shutil.copy(filename, dest)
            self.load_plugins()
            QMessageBox.information(self, "Plugin installé", f"Plugin {os.path.basename(filename)} installé avec succès.")
    
    def on_plugin_selected(self, item):
        """Affiche les informations du plugin sélectionné"""
        plugin_id = item.data(Qt.UserRole)
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]['plugin']
            info = f"""
📦 {plugin.name}
📌 Version: {plugin.version}
📁 ID: {plugin_id}
🔄 Statut: {"Activé" if self.plugins[plugin_id]['enabled'] else "Désactivé"}

Description: Plugin pour JOMAN GIS
Emplacement: {self.plugin_dir / plugin_id}.py
            """
            self.info_text.setText(info)
    
    def toggle_plugin(self):
        """Active/Désactive le plugin sélectionné"""
        item = self.plugin_list.currentItem()
        if item:
            plugin_id = item.data(Qt.UserRole)
            if plugin_id in self.plugins:
                plugin_data = self.plugins[plugin_id]
                if plugin_data['enabled']:
                    plugin_data['plugin'].unload()
                    plugin_data['enabled'] = False
                    QMessageBox.information(self, "Plugin désactivé", f"{plugin_data['plugin'].name} a été désactivé.")
                else:
                    plugin_data['plugin'].initGui()
                    plugin_data['enabled'] = True
                    QMessageBox.information(self, "Plugin activé", f"{plugin_data['plugin'].name} a été activé.")
                self.on_plugin_selected(item)
    
    def uninstall_plugin(self):
        """Désinstalle le plugin sélectionné"""
        item = self.plugin_list.currentItem()
        if item:
            plugin_id = item.data(Qt.UserRole)
            if plugin_id in self.plugins:
                reply = QMessageBox.question(self, "Confirmation", 
                    f"Voulez-vous vraiment désinstaller le plugin {plugin_id} ?",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    plugin_file = self.plugin_dir / f"{plugin_id}.py"
                    if plugin_file.exists():
                        os.remove(plugin_file)
                    del self.plugins[plugin_id]
                    self.load_plugins()
                    QMessageBox.information(self, "Plugin désinstallé", f"Plugin {plugin_id} désinstallé.")

# ============================================================================
# FICHIER: ui/joman_animation.py - Animations avancées
# ============================================================================
@'
# -*- coding: utf-8 -*-
"""
Animations avancées pour JOMAN GIS
"""

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class JomanAnimations:
    """Gestionnaire d'animations"""
    
    @staticmethod
    def fade_in(widget, duration=300):
        """Animation d'apparition"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        return animation
    
    @staticmethod
    def fade_out(widget, duration=300):
        """Animation de disparition"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.finished.connect(widget.hide)
        animation.start()
        return animation
    
    @staticmethod
    def slide_in(widget, direction="left", duration=300):
        """Animation de glissement"""
        geometry = widget.geometry()
        if direction == "left":
            start_x = -geometry.width()
            end_x = geometry.x()
        elif direction == "right":
            start_x = widget.parent().width()
            end_x = geometry.x()
        else:
            start_x = geometry.x()
            end_x = geometry.x()
        
        widget.show()
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(QRect(start_x, geometry.y(), geometry.width(), geometry.height()))
        animation.setEndValue(geometry)
        animation.start()
        return animation
    
    @staticmethod
    def pulse(widget, color=QColor(76, 175, 80), duration=1000):
        """Animation de pulsation"""
        original_style = widget.styleSheet()
        animation = QVariantAnimation()
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(100)
        animation.valueChanged.connect(lambda val: widget.setStyleSheet(
            f"background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {val/100});"
        ))
        animation.finished.connect(lambda: widget.setStyleSheet(original_style))
        animation.start()
        return animation
    
    @staticmethod
    def rotate(widget, duration=500):
        """Animation de rotation"""
        animation = QPropertyAnimation(widget, b"rotation")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(360)
        animation.start()
        return animation
    
    @staticmethod
    def shake(widget, duration=300):
        """Animation de secousse"""
        original_pos = widget.pos()
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setKeyValueAt(0, original_pos)
        animation.setKeyValueAt(0.2, original_pos + QPoint(10, 0))
        animation.setKeyValueAt(0.4, original_pos - QPoint(10, 0))
        animation.setKeyValueAt(0.6, original_pos + QPoint(5, 0))
        animation.setKeyValueAt(0.8, original_pos - QPoint(5, 0))
        animation.setKeyValueAt(1, original_pos)
        animation.start()
        return animation

class JomanNotification(QWidget):
    """Notification flottante comme dans QGIS"""
    
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setup_ui(message)
        self.duration = duration
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            JomanNotification {
                background-color: rgba(0, 0, 0, 0.8);
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
        """)
        
        # Positionner en bas à droite
        if parent:
            parent_rect = parent.geometry()
            self.move(parent_rect.right() - self.width() - 20, parent_rect.bottom() - self.height() - 20)
    
    def setup_ui(self, message):
        layout = QHBoxLayout(self)
        icon = QLabel("ℹ️")
        icon.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon)
        
        label = QLabel(message)
        layout.addWidget(label)
        
        self.setFixedSize(self.sizeHint())
    
    def show_notification(self):
        JomanAnimations.fade_in(self, 300)
        QTimer.singleShot(self.duration, lambda: JomanAnimations.fade_out(self, 300))
        self.show()
        return self
