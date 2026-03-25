import geopandas as gpd
import matplotlib.pyplot as plt
import os

# Créer un petit fichier de test
from shapely.geometry import Polygon

data = {
    'geometry': [Polygon([(-17.5, 14.5), (-17.5, 14.9), (-17.0, 14.9), (-17.0, 14.5), (-17.5, 14.5)])],
    'name': ['Dakar']
}
gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')

# Sauvegarder
os.makedirs('data/senegal', exist_ok=True)
gdf.to_file('data/senegal/test_auto.geojson', driver='GeoJSON')

print("✅ Fichier de test créé")
print(f"Étendue: {gdf.total_bounds}")

# Afficher directement
fig, ax = plt.subplots(figsize=(8, 6))
gdf.plot(ax=ax, color='green', edgecolor='black')
ax.set_title("Test - Région de Dakar")
plt.show()