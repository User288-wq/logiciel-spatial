# -*- coding: utf-8 -*-
"""
JOMAN GIS - Panneau de Propriétés de Couche complet
Comme dans QGIS avec tous les onglets
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class LayerPropertiesDialog(QDialog):
    """Dialogue des propriétés de couche complet comme dans QGIS"""
    
    def __init__(self, layer, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.setWindowTitle(f"Propriétés de la couche — {layer['name']}")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # ========== PANEL DE NAVIGATION GAUCHE ==========
        nav_list = QListWidget()
        nav_list.setMaximumWidth(200)
        nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: white;
                border: none;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        
        nav_items = [
            "📄 Information",
            "🔗 Source",
            "🎨 Symbologie",
            "🏷️ Étiquettes",
            "🎭 Masques",
            "🌍 Vue 3D",
            "📊 Diagrammes",
            "📋 Champs",
            "📝 Formulaire d'attributs",
            "🔗 Jointures",
            "💾 Stockage auxiliaire",
            "⚡ Actions",
            "👁️ Affichage",
            "🎨 Rendu",
            "⏱️ Temporel",
            "📊 Variables",
            "📋 Métadonnées",
            "🔗 Dépendances",
            "📖 Légende"
        ]
        
        for item in nav_items:
            nav_list.addItem(item)
        
        nav_list.setCurrentRow(3)  # Étiquettes sélectionné
        nav_list.currentRowChanged.connect(self.on_nav_changed)
        splitter.addWidget(nav_list)
        
        # ========== PANEL DE CONTENU DROIT ==========
        self.content_stack = QStackedWidget()
        
        # Créer tous les panneaux
        self.info_panel = self.create_info_panel()
        self.source_panel = self.create_source_panel()
        self.symbology_panel = self.create_symbology_panel()
        self.labels_panel = self.create_labels_panel()
        self.masks_panel = self.create_masks_panel()
        self.view3d_panel = self.create_view3d_panel()
        self.diagrams_panel = self.create_diagrams_panel()
        self.fields_panel = self.create_fields_panel()
        self.attribute_form_panel = self.create_attribute_form_panel()
        self.joins_panel = self.create_joins_panel()
        self.auxiliary_panel = self.create_auxiliary_panel()
        self.actions_panel = self.create_actions_panel()
        self.display_panel = self.create_display_panel()
        self.render_panel = self.create_render_panel()
        self.temporal_panel = self.create_temporal_panel()
        self.variables_panel = self.create_variables_panel()
        self.metadata_panel = self.create_metadata_panel()
        self.dependencies_panel = self.create_dependencies_panel()
        self.legend_panel = self.create_legend_panel()
        
        self.content_stack.addWidget(self.info_panel)
        self.content_stack.addWidget(self.source_panel)
        self.content_stack.addWidget(self.symbology_panel)
        self.content_stack.addWidget(self.labels_panel)
        self.content_stack.addWidget(self.masks_panel)
        self.content_stack.addWidget(self.view3d_panel)
        self.content_stack.addWidget(self.diagrams_panel)
        self.content_stack.addWidget(self.fields_panel)
        self.content_stack.addWidget(self.attribute_form_panel)
        self.content_stack.addWidget(self.joins_panel)
        self.content_stack.addWidget(self.auxiliary_panel)
        self.content_stack.addWidget(self.actions_panel)
        self.content_stack.addWidget(self.display_panel)
        self.content_stack.addWidget(self.render_panel)
        self.content_stack.addWidget(self.temporal_panel)
        self.content_stack.addWidget(self.variables_panel)
        self.content_stack.addWidget(self.metadata_panel)
        self.content_stack.addWidget(self.dependencies_panel)
        self.content_stack.addWidget(self.legend_panel)
        
        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 700])
        
        main_layout.addWidget(splitter)
        
        # ========== BOUTONS ==========
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_apply = QPushButton("Appliquer")
        btn_apply.clicked.connect(self.apply)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_apply)
        main_layout.addLayout(btn_layout)
    
    def on_nav_changed(self, index):
        self.content_stack.setCurrentIndex(index)
    
    # ==================== PANEL INFORMATION ====================
    def create_info_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Informations de base
        info_group = QGroupBox("Informations générales")
        info_layout = QGridLayout(info_group)
        
        gdf = self.layer['gdf']
        info_layout.addWidget(QLabel("Nom:"), 0, 0)
        info_layout.addWidget(QLabel(self.layer['name']), 0, 1)
        
        info_layout.addWidget(QLabel("Type:"), 1, 0)
        info_layout.addWidget(QLabel(self.layer.get('type', 'Inconnu')), 1, 1)
        
        info_layout.addWidget(QLabel("Entités:"), 2, 0)
        info_layout.addWidget(QLabel(str(len(gdf))), 2, 1)
        
        info_layout.addWidget(QLabel("Colonnes:"), 3, 0)
        info_layout.addWidget(QLabel(str(len(gdf.columns))), 3, 1)
        
        info_layout.addWidget(QLabel("Projection:"), 4, 0)
        info_layout.addWidget(QLabel(str(gdf.crs or 'WGS 84')), 4, 1)
        
        info_layout.addWidget(QLabel("Chemin:"), 5, 0)
        info_layout.addWidget(QLabel(self.layer.get('path', 'Mémoire')), 5, 1)
        
        layout.addWidget(info_group)
        
        # Statistiques
        stats_group = QGroupBox("Statistiques")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("Étendue X:"), 0, 0)
        stats_layout.addWidget(QLabel(f"[{gdf.total_bounds[0]:.4f}, {gdf.total_bounds[2]:.4f}]"), 0, 1)
        
        stats_layout.addWidget(QLabel("Étendue Y:"), 1, 0)
        stats_layout.addWidget(QLabel(f"[{gdf.total_bounds[1]:.4f}, {gdf.total_bounds[3]:.4f}]"), 1, 1)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return panel
    
    # ==================== PANEL SOURCE ====================
    def create_source_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        source_group = QGroupBox("Source des données")
        source_layout = QVBoxLayout(source_group)
        
        source_text = QTextEdit()
        source_text.setReadOnly(True)
        source_text.setText(f"Fichier: {self.layer.get('path', 'Mémoire')}\n"
                           f"Date: {self.layer.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n"
                           f"Type: {self.layer.get('type', 'Vector')}")
        source_layout.addWidget(source_text)
        
        layout.addWidget(source_group)
        layout.addStretch()
        
        return panel
    
    # ==================== PANEL SYMBOLOGIE ====================
    def create_symbology_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Valeur
        value_group = QGroupBox("Valeur")
        value_layout = QVBoxLayout(value_group)
        
        field_combo = QComboBox()
        for col in self.layer['gdf'].columns:
            if col != 'geometry':
                field_combo.addItem(col)
        value_layout.addWidget(field_combo)
        
        layout.addWidget(value_group)
        
        # Symbole
        symbol_group = QGroupBox("Symbole")
        symbol_layout = QVBoxLayout(symbol_group)
        
        color_btn = QPushButton("Couleur")
        color_btn.setStyleSheet(f"background-color: {self.layer.get('color', '#4CAF50')}")
        symbol_layout.addWidget(color_btn)
        
        layout.addWidget(symbol_group)
        
        # Classifier
        classify_group = QGroupBox("Classifier")
        classify_layout = QVBoxLayout(classify_group)
        classify_btn = QPushButton("Classifier")
        classify_layout.addWidget(classify_btn)
        layout.addWidget(classify_group)
        
        layout.addStretch()
        
        return panel
    
    # ==================== PANEL ÉTIQUETTES (COMPLET) ====================
    def create_labels_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # ========== SECTION VALEUR ==========
        value_group = QGroupBox("Valeur")
        value_layout = QVBoxLayout(value_group)
        
        value_layout.addWidget(QLabel("Champ d'étiquetage:"))
        self.label_field = QComboBox()
        for col in self.layer['gdf'].columns:
            if col != 'geometry':
                self.label_field.addItem(col)
        value_layout.addWidget(self.label_field)
        
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Échantillon de texte:"))
        sample_label = QLabel("Exemple de texte")
        sample_layout.addWidget(sample_label)
        value_layout.addLayout(sample_layout)
        
        layout.addWidget(value_group)
        
        # ========== SECTION TEXTE ==========
        text_group = QGroupBox("Texte")
        text_layout = QGridLayout(text_group)
        
        # Formatage
        text_layout.addWidget(QLabel("Formatage:"), 0, 0)
        font_combo = QComboBox()
        font_combo.addItems(["Sans-serif", "Serif", "Monospace"])
        text_layout.addWidget(font_combo, 0, 1)
        
        text_layout.addWidget(QLabel("Taille:"), 1, 0)
        size_spin = QSpinBox()
        size_spin.setRange(6, 36)
        size_spin.setValue(10)
        text_layout.addWidget(size_spin, 1, 1)
        
        text_layout.addWidget(QLabel("Couleur:"), 2, 0)
        color_btn = QPushButton()
        color_btn.setFixedSize(50, 25)
        color_btn.setStyleSheet("background-color: #333333;")
        text_layout.addWidget(color_btn, 2, 1)
        
        layout.addWidget(text_group)
        
        # ========== SECTION TAMPON ==========
        buffer_group = QGroupBox("Tampon")
        buffer_layout = QGridLayout(buffer_group)
        
        buffer_check = QCheckBox("Activer le tampon")
        buffer_layout.addWidget(buffer_check, 0, 0, 1, 2)
        
        buffer_layout.addWidget(QLabel("Taille:"), 1, 0)
        buffer_size = QDoubleSpinBox()
        buffer_size.setRange(0, 10)
        buffer_size.setValue(1)
        buffer_layout.addWidget(buffer_size, 1, 1)
        
        buffer_layout.addWidget(QLabel("Couleur:"), 2, 0)
        buffer_color = QPushButton()
        buffer_color.setFixedSize(50, 25)
        buffer_color.setStyleSheet("background-color: #FFFFFF;")
        buffer_layout.addWidget(buffer_color, 2, 1)
        
        layout.addWidget(buffer_group)
        
        # ========== SECTION ARRIÈRE-PLAN ==========
        bg_group = QGroupBox("Arrière-plan")
        bg_layout = QGridLayout(bg_group)
        
        bg_check = QCheckBox("Afficher un fond")
        bg_layout.addWidget(bg_check, 0, 0, 1, 2)
        
        bg_layout.addWidget(QLabel("Forme:"), 1, 0)
        shape_combo = QComboBox()
        shape_combo.addItems(["Rectangle", "Rond", "Carré", "Ellipse"])
        bg_layout.addWidget(shape_combo, 1, 1)
        
        bg_layout.addWidget(QLabel("Type de taille:"), 2, 0)
        size_type = QComboBox()
        size_type.addItems(["Tampon", "Fixé", "Proportionnel"])
        bg_layout.addWidget(size_type, 2, 1)
        
        bg_layout.addWidget(QLabel("Taille X:"), 3, 0)
        size_x = QDoubleSpinBox()
        size_x.setRange(0, 10)
        size_x.setValue(0)
        bg_layout.addWidget(size_x, 3, 1)
        
        bg_layout.addWidget(QLabel("Taille Y:"), 4, 0)
        size_y = QDoubleSpinBox()
        size_y.setRange(0, 10)
        size_y.setValue(0)
        bg_layout.addWidget(size_y, 4, 1)
        
        bg_layout.addWidget(QLabel("Décalage X:"), 5, 0)
        offset_x = QDoubleSpinBox()
        offset_x.setRange(-100, 100)
        offset_x.setValue(0)
        bg_layout.addWidget(offset_x, 5, 1)
        
        bg_layout.addWidget(QLabel("Décalage Y:"), 6, 0)
        offset_y = QDoubleSpinBox()
        offset_y.setRange(-100, 100)
        offset_y.setValue(0)
        bg_layout.addWidget(offset_y, 6, 1)
        
        bg_layout.addWidget(QLabel("Rayon X:"), 7, 0)
        radius_x = QDoubleSpinBox()
        radius_x.setRange(0, 10)
        radius_x.setValue(0)
        bg_layout.addWidget(radius_x, 7, 1)
        
        bg_layout.addWidget(QLabel("Rayon Y:"), 8, 0)
        radius_y = QDoubleSpinBox()
        radius_y.setRange(0, 10)
        radius_y.setValue(0)
        bg_layout.addWidget(radius_y, 8, 1)
        
        bg_layout.addWidget(QLabel("Opacité:"), 9, 0)
        bg_opacity = QSlider(Qt.Horizontal)
        bg_opacity.setRange(0, 100)
        bg_opacity.setValue(100)
        bg_layout.addWidget(bg_opacity, 9, 1)
        
        layout.addWidget(bg_group)
        
        # ========== SECTION OMBRE ==========
        shadow_group = QGroupBox("Ombre")
        shadow_layout = QGridLayout(shadow_group)
        
        shadow_check = QCheckBox("Activer l'ombre")
        shadow_layout.addWidget(shadow_check, 0, 0, 1, 2)
        
        shadow_layout.addWidget(QLabel("Décalage X:"), 1, 0)
        shadow_offset_x = QDoubleSpinBox()
        shadow_offset_x.setRange(-20, 20)
        shadow_layout.addWidget(shadow_offset_x, 1, 1)
        
        shadow_layout.addWidget(QLabel("Décalage Y:"), 2, 0)
        shadow_offset_y = QDoubleSpinBox()
        shadow_offset_y.setRange(-20, 20)
        shadow_layout.addWidget(shadow_offset_y, 2, 1)
        
        shadow_layout.addWidget(QLabel("Flou:"), 3, 0)
        shadow_blur = QDoubleSpinBox()
        shadow_blur.setRange(0, 10)
        shadow_layout.addWidget(shadow_blur, 3, 1)
        
        shadow_layout.addWidget(QLabel("Opacité:"), 4, 0)
        shadow_opacity = QSlider(Qt.Horizontal)
        shadow_opacity.setRange(0, 100)
        shadow_opacity.setValue(50)
        shadow_layout.addWidget(shadow_opacity, 4, 1)
        
        layout.addWidget(shadow_group)
        
        # ========== SECTION CONNECTEURS ==========
        connectors_group = QGroupBox("Connecteurs")
        connectors_layout = QVBoxLayout(connectors_group)
        
        connectors_check = QCheckBox("Afficher les connecteurs")
        connectors_layout.addWidget(connectors_check)
        
        connectors_layout.addWidget(QLabel("Style:"))
        connector_style = QComboBox()
        connector_style.addItems(["Ligne", "Flèche", "Pointillé"])
        connectors_layout.addWidget(connector_style)
        
        layout.addWidget(connectors_group)
        
        # ========== SECTION POSITION ==========
        position_group = QGroupBox("Position")
        position_layout = QGridLayout(position_group)
        
        position_layout.addWidget(QLabel("Placement:"), 0, 0)
        placement_combo = QComboBox()
        placement_combo.addItems(["Auto", "Centre", "Haut", "Bas", "Gauche", "Droite", "Haut-gauche", "Haut-droite", "Bas-gauche", "Bas-droite"])
        position_layout.addWidget(placement_combo, 0, 1)
        
        position_layout.addWidget(QLabel("Décalage X:"), 1, 0)
        pos_offset_x = QDoubleSpinBox()
        pos_offset_x.setRange(-100, 100)
        position_layout.addWidget(pos_offset_x, 1, 1)
        
        position_layout.addWidget(QLabel("Décalage Y:"), 2, 0)
        pos_offset_y = QDoubleSpinBox()
        pos_offset_y.setRange(-100, 100)
        position_layout.addWidget(pos_offset_y, 2, 1)
        
        position_layout.addWidget(QLabel("Rotation:"), 3, 0)
        rotation_spin = QDoubleSpinBox()
        rotation_spin.setRange(-180, 180)
        rotation_spin.setValue(0)
        position_layout.addWidget(rotation_spin, 3, 1)
        
        sync_check = QCheckBox("Synchroniser avec l'intitulé")
        position_layout.addWidget(sync_check, 4, 0, 1, 2)
        
        layout.addWidget(position_group)
        
        # ========== SECTION RENDU ==========
        render_group = QGroupBox("Rendu")
        render_layout = QVBoxLayout(render_group)
        
        scale_check = QCheckBox("Afficher selon l'échelle")
        render_layout.addWidget(scale_check)
        
        render_layout.addWidget(QLabel("Échelle min:"))
        scale_min = QSpinBox()
        scale_min.setRange(0, 1000000)
        render_layout.addWidget(scale_min)
        
        render_layout.addWidget(QLabel("Échelle max:"))
        scale_max = QSpinBox()
        scale_max.setRange(0, 1000000)
        scale_max.setValue(1000000)
        render_layout.addWidget(scale_max)
        
        layout.addWidget(render_group)
        
        layout.addStretch()
        
        return panel
    
    # ==================== AUTRES PANELS ====================
    def create_masks_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Masques - Fonctionnalité à venir"))
        return panel
    
    def create_view3d_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Vue 3D - Fonctionnalité à venir"))
        return panel
    
    def create_diagrams_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Diagrammes - Fonctionnalité à venir"))
        return panel
    
    def create_fields_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        fields_group = QGroupBox("Champs")
        fields_layout = QVBoxLayout(fields_group)
        
        fields_table = QTableWidget()
        fields_table.setColumnCount(3)
        fields_table.setHorizontalHeaderLabels(["Nom", "Type", "Alias"])
        fields_table.setRowCount(len(self.layer['gdf'].columns) - 1)
        
        row = 0
        for col in self.layer['gdf'].columns:
            if col != 'geometry':
                fields_table.setItem(row, 0, QTableWidgetItem(col))
                fields_table.setItem(row, 1, QTableWidgetItem(str(self.layer['gdf'][col].dtype)))
                row += 1
        
        fields_layout.addWidget(fields_table)
        layout.addWidget(fields_group)
        
        return panel
    
    def create_attribute_form_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Formulaire d'attributs - Fonctionnalité à venir"))
        return panel
    
    def create_joins_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Jointures - Fonctionnalité à venir"))
        return panel
    
    def create_auxiliary_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Stockage auxiliaire - Fonctionnalité à venir"))
        return panel
    
    def create_actions_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Actions - Fonctionnalité à venir"))
        return panel
    
    def create_display_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Affichage - Fonctionnalité à venir"))
        return panel
    
    def create_render_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Rendu - Fonctionnalité à venir"))
        return panel
    
    def create_temporal_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Temporel - Fonctionnalité à venir"))
        return panel
    
    def create_variables_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Variables - Fonctionnalité à venir"))
        return panel
    
    def create_metadata_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        metadata_text = QTextEdit()
        metadata_text.setReadOnly(True)
        metadata_text.setText(f"""
Nom: {self.layer['name']}
Type: {self.layer.get('type', 'Inconnu')}
Créé: {self.layer.get('created', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
Fichier: {self.layer.get('path', 'Mémoire')}
        """)
        layout.addWidget(metadata_text)
        
        return panel
    
    def create_dependencies_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Dépendances - Fonctionnalité à venir"))
        return panel
    
    def create_legend_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Légende - Fonctionnalité à venir"))
        return panel
    
    def apply(self):
        """Appliquer les changements"""
        self.accept()

# Pour éviter l'erreur datetime
from datetime import datetime
