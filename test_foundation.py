#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test de la fondation du logiciel de cartographie
"""

import sys
import os

# Ajouter le dossier courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🏛️ TEST DE LA FONDATION ARCHITECTURALE")
print("=" * 60)

try:
    print("\n📦 Importation des modules...")
    
    from core.engine.map_engine import MapEngine, MapLayer, VectorLayer, RasterLayer, MapExtent, LayerStyle, Projection, RenderMode
    print("✅ core.engine.map_engine chargé")
    
    from core.io.file_loader import FileLoader, ShapefileHandler, GeoJSONHandler, KMLHandler, CSVHandler
    print("✅ core.io.file_loader chargé")
    
    from core.analysis.spatial_analysis import SpatialAnalysis, DistanceResult, BufferResult
    print("✅ core.analysis.spatial_analysis chargé")
    
    from core.project.project_manager import ProjectManager, ProjectMetadata
    print(" core.project.project_manager chargé")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES MODULES SONT CHARGÉS AVEC SUCCÈS !")
    print("=" * 60)
    
    # Test simple du moteur
    print("\n🔧 Test du moteur cartographique...")
    engine = MapEngine()
    print(f" Moteur créé : {engine}")
    
    # Test du chargeur de fichiers
    print("\n📁 Test du chargeur de fichiers...")
    loader = FileLoader()
    extensions = loader.get_supported_extensions()
    print(f" Extensions supportées : {extensions}")
    
    # Test du gestionnaire de projet
    print("\n💾 Test du gestionnaire de projet...")
    pm = ProjectManager()
    project = pm.new_project("Test Fondation")
    print(f" Projet créé : {project.name}")
    
    print("\n" + "=" * 60)
    print("🏛️ FONDATION VALIDÉE - TOUT FONCTIONNE !")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERREUR : {e}")
    import traceback
    traceback.print_exc()

print("\nAppuyez sur Entrée pour fermer...")
input()