# -*- coding: utf-8 -*-
"""Module de découpage administratif - Régions, Départements, Communes"""

import os
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class AdministrativeDivisions:
    """Gestionnaire de découpage administratif"""
    
    LEVELS = {
        1: {'name': 'Région', 'code': 'REG', 'color': '#4CAF50', 'alpha': 0.3},
        2: {'name': 'Département', 'code': 'DEP', 'color': '#FFA500', 'alpha': 0.4},
        3: {'name': 'Arrondissement', 'code': 'ARR', 'color': '#2196F3', 'alpha': 0.5},
        4: {'name': 'Commune', 'code': 'COM', 'color': '#FFC107', 'alpha': 0.6}
    }
    
    def __init__(self):
        self.data = {}
    
    def load_from_file(self, filepath, level=1, name_column=None, code_column=None):
        try:
            gdf = gpd.read_file(filepath)
            gdf.attrs['admin_level'] = level
            gdf.attrs['admin_name'] = self.LEVELS[level]['name']
            
            if name_column and name_column in gdf.columns:
                gdf['admin_name'] = gdf[name_column]
            else:
                for col in ['name', 'NAME', 'NOM', 'admin_name']:
                    if col in gdf.columns:
                        gdf['admin_name'] = gdf[col]
                        break
                if 'admin_name' not in gdf.columns:
                    gdf['admin_name'] = f"Entité_{gdf.index}"
            
            if code_column and code_column in gdf.columns:
                gdf['admin_code'] = gdf[code_column]
            else:
                for col in ['code', 'CODE', 'id', 'admin_code']:
                    if col in gdf.columns:
                        gdf['admin_code'] = gdf[col]
                        break
                if 'admin_code' not in gdf.columns:
                    gdf['admin_code'] = gdf.index.astype(str)
            
            self.data[level] = gdf
            return gdf
        except Exception as e:
            print(f"Erreur: {e}")
            return None
    
    def get_level(self, level):
        return self.data.get(level)
    
    def get_all_levels(self):
        return self.data
    
    def find_location(self, lat, lon):
        point = Point(lon, lat)
        result = {}
        for level, gdf in sorted(self.data.items()):
            for idx, row in gdf.iterrows():
                if row.geometry.contains(point):
                    result[level] = {
                        'name': row.get('admin_name', f'Niveau {level}'),
                        'code': row.get('admin_code', ''),
                        'geometry': row.geometry
                    }
                    break
        return result
    
    def get_hierarchy(self, lat, lon):
        locations = self.find_location(lat, lon)
        return [{'level': l, 'name': locations[l]['name'], 'code': locations[l]['code']} 
                for l in sorted(locations.keys())]

class AdministrativeWidget(QWidget):
    location_selected = Signal(dict)
    
    def __init__(self, admin_manager, parent=None):
        super().__init__(parent)
        self.admin = admin_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🏛️ DÉCOUPAGE ADMINISTRATIF")
        title.setStyleSheet("font-weight: bold; color: #4CAF50; padding: 5px;")
        layout.addWidget(title)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Hiérarchie administrative")
        self.tree.setStyleSheet("""
            QTreeWidget { background-color: #16213e; color: white; border: none; }
            QTreeWidget::item { padding: 4px; }
            QTreeWidget::item:hover { background-color: #0f3460; }
        """)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
        
        self.info_label = QLabel("Sélectionnez une entité")
        self.info_label.setStyleSheet("background: #0f3460; padding: 5px; border-radius: 3px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
    
    def load_level(self, level):
        gdf = self.admin.get_level(level)
        if gdf is None:
            return
        
        level_name = self.admin.LEVELS[level]['name']
        root = QTreeWidgetItem(self.tree)
        root.setText(0, f"📁 {level_name}")
        
        for idx, row in gdf.iterrows():
            item = QTreeWidgetItem(root)
            name = row.get('admin_name', f"Entité {idx}")
            item.setText(0, f"📍 {name}")
            item.setData(0, Qt.UserRole, {
                'level': level,
                'name': name,
                'code': row.get('admin_code', ''),
                'geometry': row.geometry
            })
        
        self.tree.expandAll()
    
    def load_all_levels(self):
        self.tree.clear()
        for level in sorted(self.admin.get_all_levels().keys()):
            self.load_level(level)
    
    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if data and 'name' in data:
            self.info_label.setText(f"📍 {data['name']}\n🏷️ Code: {data.get('code', 'N/A')}")
            self.location_selected.emit(data)
