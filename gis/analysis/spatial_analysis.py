# -*- coding: utf-8 -*-
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from scipy.spatial import KDTree, cKDTree
from scipy.spatial.distance import cdist

class SpatialAnalysisTools:
    """TOUS les outils d'analyse spatiale QGIS"""
    
    @staticmethod
    def nearest_neighbor(gdf1, gdf2, k=1, max_distance=None):
        points1 = np.array([(p.x, p.y) for p in gdf1.geometry.centroid])
        points2 = np.array([(p.x, p.y) for p in gdf2.geometry.centroid])
        tree = KDTree(points2)
        if max_distance:
            distances, indices = tree.query(points1, k=k, distance_upper_bound=max_distance)
        else:
            distances, indices = tree.query(points1, k=k)
        return distances, indices
    
    @staticmethod
    def distance_matrix(gdf1, gdf2):
        points1 = np.array([(p.x, p.y) for p in gdf1.geometry.centroid])
        points2 = np.array([(p.x, p.y) for p in gdf2.geometry.centroid])
        return cdist(points1, points2)
    
    @staticmethod
    def count_points_in_polygon(points_gdf, polygons_gdf):
        result = polygons_gdf.copy()
        result['point_count'] = 0
        for idx, polygon in polygons_gdf.iterrows():
            count = points_gdf[points_gdf.geometry.within(polygon.geometry)].shape[0]
            result.at[idx, 'point_count'] = count
        return result
    
    @staticmethod
    def heatmap(points_gdf, cell_size=0.01, radius=0.05, kernel='gaussian'):
        bounds = points_gdf.total_bounds
        xmin, ymin, xmax, ymax = bounds
        x_cells = int((xmax - xmin) / cell_size)
        y_cells = int((ymax - ymin) / cell_size)
        heatmap_data = []
        for i in range(x_cells):
            for j in range(y_cells):
                x = xmin + i * cell_size + cell_size/2
                y = ymin + j * cell_size + cell_size/2
                point = Point(x, y)
                count = points_gdf[points_gdf.geometry.distance(point) <= radius].shape[0]
                if count > 0:
                    heatmap_data.append({'x': x, 'y': y, 'intensity': count, 'geometry': point})
        return gpd.GeoDataFrame(heatmap_data, crs=points_gdf.crs)
    
    @staticmethod
    def interpolate_points(points_gdf, field, method='idw', grid_size=50):
        """Interpolation IDW des points"""
        from scipy.interpolate import RBFInterpolator
        points = np.array([(p.x, p.y) for p in points_gdf.geometry])
        values = points_gdf[field].values
        
        bounds = points_gdf.total_bounds
        x = np.linspace(bounds[0], bounds[2], grid_size)
        y = np.linspace(bounds[1], bounds[3], grid_size)
        xx, yy = np.meshgrid(x, y)
        grid_points = np.c_[xx.ravel(), yy.ravel()]
        
        rbf = RBFInterpolator(points, values, kernel='thin_plate_spline')
        zz = rbf(grid_points).reshape(grid_size, grid_size)
        
        return xx, yy, zz
    
    @staticmethod
    def create_grid(bounds, n_rows, n_cols):
        xmin, ymin, xmax, ymax = bounds
        dx = (xmax - xmin) / n_cols
        dy = (ymax - ymin) / n_rows
        polygons = []
        for i in range(n_rows):
            for j in range(n_cols):
                x1 = xmin + j * dx
                y1 = ymin + i * dy
                poly = Polygon([(x1, y1), (x1+dx, y1), (x1+dx, y1+dy), (x1, y1+dy)])
                polygons.append(poly)
        return gpd.GeoDataFrame({'id': range(len(polygons)), 'row': i, 'col': j}, geometry=polygons, crs='EPSG:4326')
    
    @staticmethod
    def voronoi(points_gdf, bounds=None):
        from scipy.spatial import Voronoi
        points = np.array([(p.x, p.y) for p in points_gdf.geometry])
        vor = Voronoi(points)
        from shapely.geometry import Polygon
        polygons = []
        for i, region in enumerate(vor.regions):
            if region and -1 not in region:
                polygon = Polygon([vor.vertices[i] for i in region])
                if polygon.is_valid and polygon.area > 0:
                    polygons.append(polygon)
        return gpd.GeoDataFrame(geometry=polygons, crs=points_gdf.crs)
    
    @staticmethod
    def delaunay(points_gdf):
        from scipy.spatial import Delaunay
        points = np.array([(p.x, p.y) for p in points_gdf.geometry])
        tri = Delaunay(points)
        from shapely.geometry import Polygon
        triangles = []
        for simplex in tri.simplices:
            triangle = Polygon([points[simplex[0]], points[simplex[1]], points[simplex[2]]])
            triangles.append(triangle)
        return gpd.GeoDataFrame(geometry=triangles, crs=points_gdf.crs)
