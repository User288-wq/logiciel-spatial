import geopandas as gpd

gdf = gpd.read_file(r'C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\senegal\sen_admin1.shp')

print("=== TEST DES NOMS ===")
for i in range(5):
    print(f"{i}: {gdf.iloc[i]['adm1_name']}")

print()
print("=== TEST DES CENTROIDES ===")
for i in range(3):
    centroid = gdf.iloc[i].geometry.centroid
    print(f"{i}: ({centroid.x:.4f}, {centroid.y:.4f})")

print()
print("=== LIMITES GLOBALES ===")
bounds = gdf.total_bounds
print(f"X: [{bounds[0]:.2f}, {bounds[2]:.2f}]")
print(f"Y: [{bounds[1]:.2f}, {bounds[3]:.2f}]")
