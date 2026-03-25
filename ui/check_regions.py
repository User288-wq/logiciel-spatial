import geopandas as gpd

gdf = gpd.read_file(r'C:\Users\User\OneDrive\Desktop\logiciel_spatial\data\senegal\sen_admin1.shp')

print("=== INFORMATIONS ===")
print(f"Nombre de regions: {len(gdf)}")
print(f"Type de geometrie: {gdf.geometry.type.iloc[0]}")
print(f"Colonnes: {list(gdf.columns)}")
print("\nPremieres regions:")
for i in range(3):
    print(f"  {i}: {gdf.iloc[i]['adm1_name']}")
print("\nEtendue geographique:")
print(f"  X: {gdf.total_bounds[0]:.2f} a {gdf.total_bounds[2]:.2f}")
print(f"  Y: {gdf.total_bounds[1]:.2f} a {gdf.total_bounds[3]:.2f}")
