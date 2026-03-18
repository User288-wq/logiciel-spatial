import tkinter as tk
from tkinter import ttk
import math
import random

class SystemeSolaireAvance:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍🚀 Système Solaire Avancé - Avec Lunes et Satellites")
        self.root.geometry("1000x800")
        
        # Données des planètes (distance en M km, diamètre en km)
        self.planetes = [
            {"nom": "Mercure", "distance": 57.9, "diametre": 4879, "couleur": "#a5a5a5", "vitesse": 47.87, "lunes": 0},
            {"nom": "Vénus", "distance": 108.2, "diametre": 12104, "couleur": "#ffb347", "vitesse": 35.02, "lunes": 0},
            {"nom": "Terre", "distance": 149.6, "diametre": 12742, "couleur": "#4a90e2", "vitesse": 29.78, "lunes": 1},
            {"nom": "Mars", "distance": 227.9, "diametre": 6779, "couleur": "#e27a4a", "vitesse": 24.07, "lunes": 2},
            {"nom": "Jupiter", "distance": 778.5, "diametre": 139820, "couleur": "#d98c4a", "vitesse": 13.07, "lunes": 79},
            {"nom": "Saturne", "distance": 1433.5, "diametre": 116460, "couleur": "#e0b060", "vitesse": 9.69, "lunes": 82},
            {"nom": "Uranus", "distance": 2872.5, "diametre": 50724, "couleur": "#7ec8e0", "vitesse": 6.81, "lunes": 27},
            {"nom": "Neptune", "distance": 4495.1, "diametre": 49244, "couleur": "#4a6ee0", "vitesse": 5.43, "lunes": 14}
        ]
        
        # Lunes (distances en km de leur planète)
        self.lunes = {
            "Terre": [{"nom": "🌙 Lune", "distance": 384400, "couleur": "#cccccc", "periode": 27.3}],
            "Mars": [
                {"nom": "🔴 Phobos", "distance": 9376, "couleur": "#aa8866", "periode": 0.32},
                {"nom": "🟤 Déimos", "distance": 23463, "couleur": "#886644", "periode": 1.26}
            ],
            "Jupiter": [{"nom": "🌕 Io", "distance": 421800, "couleur": "#ffaa00", "periode": 1.77},
                       {"nom": "🌑 Europe", "distance": 671100, "couleur": "#88aaff", "periode": 3.55},
                       {"nom": "🌘 Ganymède", "distance": 1070400, "couleur": "#aabbcc", "periode": 7.15},
                       {"nom": "🌗 Callisto", "distance": 1882700, "couleur": "#ccbbaa", "periode": 16.69}]
        }
        
        # Satellites artificiels
        self.satellites = [
            {"nom": "🛰️ ISS", "planete": "Terre", "altitude": 408, "couleur": "#ffffff"},
            {"nom": "🛰️ Hubble", "planete": "Terre", "altitude": 540, "couleur": "#aaaaff"},
            {"nom": "🛰️ GPS", "planete": "Terre", "altitude": 20200, "couleur": "#88ff88"}
        ]
        
        # Positions
        self.positions = {p["nom"]: random.uniform(0, 2*math.pi) for p in self.planetes}
        self.positions_lunes = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Interface avec onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet 1 : Visualisation
        visu_tab = ttk.Frame(notebook)
        notebook.add(visu_tab, text="🪐 Visualisation")
        
        # Onglet 2 : Satellites
        satellite_tab = ttk.Frame(notebook)
        notebook.add(satellite_tab, text="📡 Satellites")
        
        # Onglet 3 : Missions
        mission_tab = ttk.Frame(notebook)
        notebook.add(mission_tab, text="🚀 Missions")
        
        self.creer_onglet_visualisation(visu_tab)
        self.creer_onglet_satellites(satellite_tab)
        self.creer_onglet_missions(mission_tab)
        
    def creer_onglet_visualisation(self, parent):
        # Panneau de contrôle
        control_frame = ttk.LabelFrame(parent, text="🛸 Contrôles", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Même interface que avant mais avec plus d'options
        ttk.Label(control_frame, text="Planète de départ:").pack()
        self.depart_var = tk.StringVar(value="Terre")
        ttk.Combobox(control_frame, textvariable=self.depart_var, 
                    values=[p["nom"] for p in self.planetes]).pack()
        
        ttk.Label(control_frame, text="Planète d'arrivée:").pack()
        self.arrivee_var = tk.StringVar(value="Mars")
        ttk.Combobox(control_frame, textvariable=self.arrivee_var,
                    values=[p["nom"] for p in self.planetes]).pack()
        
        # Boutons
        ttk.Button(control_frame, text="🚀 Calculer distance", 
                  command=self.calculer_distance).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="🌙 Afficher lunes", 
                  command=self.afficher_lunes).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="📊 Statistiques", 
                  command=self.afficher_stats).pack(fill=tk.X, pady=2)
        
        # Canvas
        self.canvas = tk.Canvas(parent, bg="#0a0a2a", width=600, height=600)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.dessiner_systeme()
        
    def creer_onglet_satellites(self, parent):
        for sat in self.satellites:
            frame = ttk.LabelFrame(parent, text=sat["nom"], padding="5")
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"Planète: {sat['planete']}").pack()
            ttk.Label(frame, text=f"Altitude: {sat['altitude']} km").pack()
            ttk.Label(frame, text=f"Vitesse: {self.calculer_vitesse_satellite(sat['altitude']):.1f} km/s").pack()
            
    def creer_onglet_missions(self, parent):
        missions = [
            {"nom": "Apollo 11", "date": "1969", "objectif": "Premier pas sur la Lune"},
            {"nom": "Voyager 1", "date": "1977", "objectif": "Exploration système solaire"},
            {"nom": "ISS", "date": "1998", "objectif": "Station spatiale internationale"},
            {"nom": "Perseverance", "date": "2020", "objectif": "Exploration Mars"},
            {"nom": "James Webb", "date": "2021", "objectif": "Télescope spatial"}
        ]
        
        for mission in missions:
            frame = ttk.LabelFrame(parent, text=mission["nom"], padding="5")
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"📅 {mission['date']} - {mission['objectif']}").pack()
    
    def calculer_vitesse_satellite(self, altitude):
        # Vitesse orbitale approximative
        import math
        rayon_terre = 6371  # km
        rayon_orbite = (rayon_terre + altitude) * 1000  # en m
        mu_terre = 3.986e14  # m³/s²
        vitesse = math.sqrt(mu_terre / rayon_orbite) / 1000  # km/s
        return vitesse
    
    def calculer_distance(self):
        # Calcul de distance entre planètes
        depart = self.depart_var.get()
        arrivee = self.arrivee_var.get()
        
        p1 = next(p for p in self.planetes if p["nom"] == depart)
        p2 = next(p for p in self.planetes if p["nom"] == arrivee)
        
        angle1 = self.positions[depart]
        angle2 = self.positions[arrivee]
        
        x1 = p1["distance"] * math.cos(angle1)
        y1 = p1["distance"] * math.sin(angle1)
        x2 = p2["distance"] * math.cos(angle2)
        y2 = p2["distance"] * math.sin(angle2)
        
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        # Afficher dans une popup
        from tkinter import messagebox
        messagebox.showinfo("Distance", 
            f"Distance {depart} → {arrivee}\n\n"
            f"📏 {distance:.2f} millions de km\n"
            f"= {distance*1e6:.0f} km\n\n"
            f"🚀 Temps à 50 000 km/s: {distance*1e6/50000/3600:.1f} heures")
    
    def afficher_lunes(self):
        planete = self.depart_var.get()
        if planete in self.lunes:
            lunes = self.lunes[planete]
            texte = f"🌙 Lunes de {planete}:\n\n"
            for lune in lunes:
                texte += f"• {lune['nom']}\n"
                texte += f"  Distance: {lune['distance']} km\n"
                texte += f"  Période: {lune['periode']} jours\n\n"
        else:
            texte = f"{planete} n'a pas de lune connue"
        
        from tkinter import messagebox
        messagebox.showinfo("Lunes", texte)
    
    def afficher_stats(self):
        texte = "📊 STATISTIQUES DU SYSTÈME SOLAIRE\n"
        texte += "="*40 + "\n\n"
        
        texte += f"Nombre de planètes: {len(self.planetes)}\n"
        texte += f"Nombre total de lunes: {sum(p['lunes'] for p in self.planetes)}\n"
        texte += f"Satellites artificiels: {len(self.satellites)}\n\n"
        
        texte += "📏 DISTANCES:\n"
        texte += f"• Terre-Soleil: {self.planetes[2]['distance']} M km\n"
        texte += f"• Terre-Lune: 0.384 M km\n"
        texte += f"• Système solaire: {self.planetes[-1]['distance']} M km\n\n"
        
        texte += "⏱️ VOYAGES:\n"
        texte += "• Terre-Mars: 3-6 mois (actuel)\n"
        texte += "• Terre-Jupiter: 2-3 ans\n"
        texte += "• Terre-Neptune: 12 ans\n"
        
        from tkinter import messagebox
        messagebox.showinfo("Statistiques", texte)
    
    def dessiner_systeme(self):
        self.canvas.delete("all")
        cx, cy = 300, 300
        
        # Soleil
        self.canvas.create_oval(cx-20, cy-20, cx+20, cy+20, fill="#ffdd00")
        self.canvas.create_text(cx, cy-30, text="☀️ SOLEIL", fill="white")
        
        # Échelle
        echelle = 0.3
        
        # Dessiner les planètes
        for p in self.planetes:
            rayon = p["distance"] * echelle
            if rayon < 250:
                # Orbite
                self.canvas.create_oval(cx-rayon, cy-rayon, cx+rayon, cy+rayon,
                                       outline="#333366", dash=(2,2))
                
                # Planète
                angle = self.positions[p["nom"]]
                x = cx + rayon * math.cos(angle)
                y = cy + rayon * math.sin(angle)
                
                taille = max(2, min(6, p["diametre"] / 20000))
                self.canvas.create_oval(x-taille, y-taille, x+taille, y+taille,
                                       fill=p["couleur"], outline="white")
                self.canvas.create_text(x, y-12, text=p["nom"], 
                                       fill="white", font=("Arial", 7))
        
        # Animation
        self.root.after(100, self.animer)
    
    def animer(self):
        for p in self.planetes:
            vitesse = 0.002 / math.sqrt(p["distance"])
            self.positions[p["nom"]] += vitesse
        self.dessiner_systeme()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemeSolaireAvance(root)
    root.mainloop()