# -*- coding: utf-8 -*-
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from shapely.geometry import Point

class MapCanvas(FigureCanvas):
    selection_changed = Signal(object)
    coordinates_changed = Signal(float, float)
    
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 8), facecolor='#f5f5f5')
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#e8f4f8')
        self.ax.grid(True, alpha=0.3, color='#666666', linestyle='--')
        self.ax.tick_params(colors='#333333')
        
        self.current_gdf = None
        self.current_name = ""
        self.selected_index = None
        self.measure_points = []
        self.measure_mode = False
        self.scale = 0
        self.pan_start = None
        self.panning = False
        
        # Barre d'échelle et flèche nord
        self.scalebar_visible = True
        self.north_arrow_visible = True
        
        self.cid_press = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_click = self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.draw()
    
    def draw_layer(self, gdf, name, color='#4CAF50', edgecolor='#2E7D32', alpha=0.7):
        self.current_gdf = gdf
        self.current_name = name
        
        self.ax.clear()
        self.ax.set_facecolor('#e8f4f8')
        self.ax.grid(True, alpha=0.3, color='#666666', linestyle='--')
        
        if gdf is not None and len(gdf) > 0:
            geom_type = gdf.geometry.type.iloc[0]
            if 'Point' in geom_type:
                gdf.plot(ax=self.ax, color=color, markersize=10, alpha=alpha, edgecolor='white')
            elif 'Line' in geom_type:
                gdf.plot(ax=self.ax, color=color, linewidth=1.5, alpha=alpha)
            else:
                gdf.plot(ax=self.ax, color=color, edgecolor=edgecolor, linewidth=0.8, alpha=alpha)
            
            if self.selected_index is not None and self.selected_index < len(gdf):
                selected = gdf.iloc[[self.selected_index]]
                selected.plot(ax=self.ax, color='#FFD700', edgecolor='#FF8C00', linewidth=2, alpha=0.9)
            
            bounds = gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            
            width_deg = (bounds[2] - bounds[0])
            width_km = width_deg * 111
            self.scale = width_km * 100000
            self.ax.set_title(f"{name} - {len(gdf)} entités", color='#333333', fontsize=12)
        
        self.draw_measure()
        self.add_scalebar()
        self.add_north_arrow()
        self.ax.tick_params(colors='#333333')
        self.draw()
    
    def add_scalebar(self):
        """Ajoute une barre d'échelle comme dans QGIS"""
        if not self.scalebar_visible or self.current_gdf is None:
            return
        
        # Calculer la longueur de la barre d'échelle (en km)
        xlim = self.ax.get_xlim()
        width_deg = xlim[1] - xlim[0]
        width_km = width_deg * 111
        
        # Choisir une longueur de barre appropriée
        if width_km > 1000:
            bar_length_km = 500
            bar_text = f"{int(bar_length_km)} km"
        elif width_km > 100:
            bar_length_km = 50
            bar_text = f"{int(bar_length_km)} km"
        elif width_km > 10:
            bar_length_km = 5
            bar_text = f"{int(bar_length_km)} km"
        else:
            bar_length_km = 1
            bar_text = f"{int(bar_length_km)} km"
        
        # Convertir en degrés
        bar_length_deg = bar_length_km / 111
        
        # Position de la barre (en bas à gauche)
        x_pos = xlim[0] + (xlim[1] - xlim[0]) * 0.05
        y_pos = self.ax.get_ylim()[0] + (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.05
        
        # Dessiner la barre d'échelle
        self.ax.plot([x_pos, x_pos + bar_length_deg], [y_pos, y_pos], 'k-', linewidth=3)
        self.ax.plot([x_pos, x_pos], [y_pos - (self.ax.get_ylim()[1] * 0.005), y_pos + (self.ax.get_ylim()[1] * 0.005)], 'k-', linewidth=1)
        self.ax.plot([x_pos + bar_length_deg, x_pos + bar_length_deg], 
                    [y_pos - (self.ax.get_ylim()[1] * 0.005), y_pos + (self.ax.get_ylim()[1] * 0.005)], 'k-', linewidth=1)
        
        # Ajouter le texte
        self.ax.text(x_pos + bar_length_deg/2, y_pos - (self.ax.get_ylim()[1] * 0.015), bar_text, 
                    ha='center', va='top', fontsize=8, color='black',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
    
    def add_north_arrow(self):
        """Ajoute une flèche nord comme dans QGIS"""
        if not self.north_arrow_visible:
            return
        
        # Position de la flèche (en haut à droite)
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_pos = xlim[1] - (xlim[1] - xlim[0]) * 0.08
        y_pos = ylim[1] - (ylim[1] - ylim[0]) * 0.08
        arrow_length = (ylim[1] - ylim[0]) * 0.05
        
        # Dessiner la flèche nord
        self.ax.annotate('N', xy=(x_pos, y_pos + arrow_length), xytext=(x_pos, y_pos),
                        arrowprops=dict(arrowstyle='->', color='black', lw=2),
                        ha='center', va='center', fontsize=12, fontweight='bold')
    
    def draw_measure(self):
        if len(self.measure_points) > 1:
            x = [p[0] for p in self.measure_points]
            y = [p[1] for p in self.measure_points]
            self.ax.plot(x, y, '#FF69B4', linewidth=2, alpha=0.8)
            total = 0
            for i in range(len(self.measure_points)-1):
                total += math.sqrt((x[i+1]-x[i])**2 + (y[i+1]-y[i])**2) * 111
            self.ax.text(x[-1], y[-1], f"{total:.2f} km", fontsize=9, color='#FF1493',
                        bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
    
    def on_press(self, event):
        if event.button == 2 and event.xdata and event.ydata:  # Molette du milieu
            self.pan_start = (event.xdata, event.ydata)
            self.panning = True
    
    def on_release(self, event):
        self.panning = False
        self.pan_start = None
    
    def on_motion(self, event):
        if self.panning and event.xdata and event.ydata and self.pan_start:
            dx = event.xdata - self.pan_start[0]
            dy = event.ydata - self.pan_start[1]
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            self.pan_start = (event.xdata, event.ydata)
            self.draw()
            self.add_scalebar()
            self.add_north_arrow()
            self.draw()
    
    def on_click(self, event):
        if event.inaxes is None:
            return
        x, y = event.xdata, event.ydata
        self.coordinates_changed.emit(x, y)
        
        if self.measure_mode:
            self.measure_points.append((x, y))
            self.draw()
            self.add_scalebar()
            self.add_north_arrow()
            return
        
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            point = Point(x, y)
            for idx, row in self.current_gdf.iterrows():
                if row.geometry and row.geometry.contains(point):
                    self.selected_index = idx
                    self.draw()
                    self.add_scalebar()
                    self.add_north_arrow()
                    self.selection_changed.emit(row)
                    return
            self.selected_index = None
            self.draw()
            self.add_scalebar()
            self.add_north_arrow()
            self.selection_changed.emit(None)
    
    def toggle_measure(self):
        self.measure_mode = not self.measure_mode
        if not self.measure_mode:
            self.measure_points = []
            self.draw()
            self.add_scalebar()
            self.add_north_arrow()
        return self.measure_mode
    
    def toggle_scalebar(self):
        self.scalebar_visible = not self.scalebar_visible
        self.draw()
        if self.scalebar_visible:
            self.add_scalebar()
        self.add_north_arrow()
        self.draw()
    
    def toggle_north_arrow(self):
        self.north_arrow_visible = not self.north_arrow_visible
        self.draw()
        self.add_scalebar()
        if self.north_arrow_visible:
            self.add_north_arrow()
        self.draw()
    
    def clear(self):
        self.current_gdf = None
        self.selected_index = None
        self.ax.clear()
        self.ax.set_facecolor('#e8f4f8')
        self.ax.text(0.5, 0.5, "Aucune donnée", transform=self.ax.transAxes, ha='center', color='#666666', fontsize=14)
        self.draw()
    
    def zoom_in(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        dx = (xlim[1] - xlim[0]) * 0.2
        dy = (ylim[1] - ylim[0]) * 0.2
        self.ax.set_xlim(cx - dx, cx + dx)
        self.ax.set_ylim(cy - dy, cy + dy)
        self.draw()
        self.add_scalebar()
        self.add_north_arrow()
        self.draw()
    
    def zoom_out(self):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        dx = (xlim[1] - xlim[0]) * 0.3
        dy = (ylim[1] - ylim[0]) * 0.3
        self.ax.set_xlim(cx - dx, cx + dx)
        self.ax.set_ylim(cy - dy, cy + dy)
        self.draw()
        self.add_scalebar()
        self.add_north_arrow()
        self.draw()
    
    def zoom_all(self):
        if self.current_gdf is not None and len(self.current_gdf) > 0:
            bounds = self.current_gdf.total_bounds
            margin_x = (bounds[2] - bounds[0]) * 0.05
            margin_y = (bounds[3] - bounds[1]) * 0.05
            self.ax.set_xlim(bounds[0] - margin_x, bounds[2] + margin_x)
            self.ax.set_ylim(bounds[1] - margin_y, bounds[3] + margin_y)
            self.draw()
            self.add_scalebar()
            self.add_north_arrow()
            self.draw()
    
    def export(self, filename):
        self.add_scalebar()
        self.add_north_arrow()
        self.figure.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f5f5f5')
    
    def get_scale(self):
        return self.scale
