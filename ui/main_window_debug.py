def setup_ui(self):
    print("   setup_ui début")
    central = QWidget()
    self.setCentralWidget(central)
    print("   central créé")
    layout = QHBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    print("   layout créé")
    
    # Panneau gauche
    left_panel = QWidget()
    left_panel.setMaximumWidth(450)
    left_layout = QVBoxLayout(left_panel)
    print("   left_panel créé")
    
    info_label = QLabel("💡 Glissez-déposez vos fichiers ici\n📁 Formats: .shp, .geojson, .kml, .kmz, .csv...")
    info_label.setStyleSheet("background-color: #16213e; color: #ffaa00; padding: 8px; border-radius: 5px;")
    left_layout.addWidget(info_label)
    print("   info_label ajouté")
    
    # Création du LayerTreeWidget
    print("   avant LayerTreeWidget")
    self.layer_tree = LayerTreeWidget(self)
    print("   après LayerTreeWidget")
    self.layer_tree.layer_visibility_changed.connect(self.on_layer_visibility_changed)
    self.layer_tree.layer_selected.connect(self.on_layer_selected)
    left_layout.addWidget(QLabel("🗂️ Couches"))
    left_layout.addWidget(self.layer_tree)
    print("   layer_tree ajouté")
    
    btn_layout = QHBoxLayout()
    self.btn_add = QPushButton("➕ Ajouter")
    self.btn_add.clicked.connect(self.import_file)
    self.btn_remove = QPushButton("➖ Supprimer")
    self.btn_remove.clicked.connect(self.remove_selected_layer)
    btn_layout.addWidget(self.btn_add)
    btn_layout.addWidget(self.btn_remove)
    left_layout.addLayout(btn_layout)
    print("   boutons ajoutés")
    
    self.attr_group = QGroupBox("📋 Attributs de l'entité sélectionnée")
    attr_layout = QVBoxLayout(self.attr_group)
    self.attr_text = QTextEdit()
    self.attr_text.setReadOnly(True)
    self.attr_text.setStyleSheet("background-color: #16213e; color: #ffaa00; font-family: 'Courier New'; font-size: 11px;")
    self.attr_text.setMaximumHeight(200)
    attr_layout.addWidget(self.attr_text)
    left_layout.addWidget(self.attr_group)
    print("   attr_group ajouté")
    
    self.properties = PropertiesWidget()
    left_layout.addWidget(QLabel("📋 Propriétés de la couche"))
    left_layout.addWidget(self.properties)
    print("   properties ajouté")
    
    layout.addWidget(left_panel)
    print("   left_panel ajouté")
    
    # Zone centrale
    center_panel = QWidget()
    center_layout = QVBoxLayout(center_panel)
    print("   center_panel créé")
    
    print("   avant create_map_widget")
    self.map_widget = self.create_map_widget()
    print("   après create_map_widget")
    center_layout.addWidget(self.map_widget)
    print("   map_widget ajouté")
    layout.addWidget(center_panel, 1)
    print("   center_panel ajouté")
    
    # Panneau droit
    right_panel = QWidget()
    right_panel.setMaximumWidth(250)
    right_layout = QVBoxLayout(right_panel)
    print("   right_panel créé")
    
    legend_title = QLabel("📖 LÉGENDE")
    legend_title.setStyleSheet("font-weight: bold; color: #4CAF50; font-size: 12px;")
    right_layout.addWidget(legend_title)
    print("   legend_title ajouté")
    
    legend_items = [
        ('🟩', 'Régions', '#4CAF50'),
        ('🟧', 'Départements', '#FFA500'),
        ('📍', 'Points', '#FF4444'),
        ('📏', 'Lignes', '#FFA500'),
        ('🔲', 'Polygones', '#4CAF50'),
        ('🟨', 'Sélectionné', '#FFFF00'),
    ]
    
    for icon, name, color in legend_items:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(QLabel(icon))
        layout.addWidget(QLabel(name))
        layout.addStretch()
        right_layout.addWidget(widget)
    print("   legend_items ajoutés")
    
    right_layout.addStretch()
    layout.addWidget(right_panel)
    print("   right_panel ajouté")
    print("   setup_ui fin")