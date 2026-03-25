import re

with open('spatial_gis_ultimate.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ajouter le style vector
if "'vector':" not in content:
    # Trouver la position de la dernière accolade
    pos = content.rfind('}')
    # Remonter pour trouver le début du dictionnaire STYLES
    styles_start = content.rfind('STYLES = {', 0, pos)
    if styles_start > 0:
        vector_style = '''

    'vector': {
        'name': 'Vecteur',
        'color': '#4CAF50',
        'edgecolor': '#2E7D32',
        'alpha': 0.5,
        'linewidth': 1.0,
        'min_scale': 0,
        'max_scale': float('inf')
    }'''
        content = content[:pos] + vector_style + content[pos:]
        print('✅ Style vector ajouté')

# 2. Corriger les boutons PluginManager
replacements = [
    ('btn_layout.addWidget(QPushButton("✅ Activer", self.activate_plugin))',
     'btn = QPushButton("✅ Activer"); btn.clicked.connect(self.activate_plugin); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("❌ Désactiver", self.deactivate_plugin))',
     'btn = QPushButton("❌ Désactiver"); btn.clicked.connect(self.deactivate_plugin); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("🗑️ Désinstaller", self.uninstall_plugin))',
     'btn = QPushButton("🗑️ Désinstaller"); btn.clicked.connect(self.uninstall_plugin); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("📥 Installer", self.install_plugin))',
     'btn = QPushButton("📥 Installer"); btn.clicked.connect(self.install_plugin); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("🔄 Actualiser", self.load_plugins))',
     'btn = QPushButton("🔄 Actualiser"); btn.clicked.connect(self.load_plugins); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("Fermer", self.accept))',
     'btn = QPushButton("Fermer"); btn.clicked.connect(self.accept); btn_layout.addWidget(btn)'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'✅ Corrigé: {old[:40]}...')

# 3. Corriger les boutons PythonConsole
replacements2 = [
    ('btn_layout.addWidget(QPushButton("▶️ Exécuter", self.execute))',
     'btn = QPushButton("▶️ Exécuter"); btn.clicked.connect(self.execute); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("🗑️ Effacer", self.clear))',
     'btn = QPushButton("🗑️ Effacer"); btn.clicked.connect(self.clear); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("📂 Charger", self.load_script))',
     'btn = QPushButton("📂 Charger"); btn.clicked.connect(self.load_script); btn_layout.addWidget(btn)'),
    ('btn_layout.addWidget(QPushButton("💾 Sauvegarder", self.save_script))',
     'btn = QPushButton("💾 Sauvegarder"); btn.clicked.connect(self.save_script); btn_layout.addWidget(btn)'),
]

for old, new in replacements2:
    if old in content:
        content = content.replace(old, new)
        print(f'✅ Corrigé: {old[:40]}...')

with open('spatial_gis_ultimate_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n✅ Fichier corrigé sauvegardé: spatial_gis_ultimate_fixed.py')
