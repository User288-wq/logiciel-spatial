import tkinter as tk
from tkinter import ttk
import math
import random

class SystemeSolaire:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Système Solaire - Simulation Spatiale")
        self.root.geometry("900x700")
        
        # Couleurs pour les planètes
        self.couleurs = {
            "Soleil": "#ffdd00",
            "Mercure": "#a5a5a5",
            "Vénus": "#ffb347",
            "Terre": "#4a90e2",
            "Mars": "#e27a4a",
            "Jupiter": "#d98c4a",
            "Saturne": "#e0b060",
            "Uranus": "#7ec8e0",
            "Neptune": "#4a6ee0"
        }
        
        # Données des planètes (distances en millions de km, diamètres en km)
        self.planetes = [
            {"nom": "Mercure", "distance": 57.9, "diametre": 4879, "couleur": "#a5a5a5", "vitesse": 47.87},
            {"nom": "Vénus", "distance": 108.2, "diametre": 12104, "couleur": "#ffb347", "vitesse": 35.02},
            {"nom": "Terre", "distance": 149.6, "diametre": 12742, "couleur": "#4a90e2", "vitesse": 29.78},
            {"nom": "Mars", "distance": 227.9, "diametre": 6779, "couleur": "#e27a4a", "vitesse": 24.07},
            {"nom": "Jupiter", "distance": 778.5, "diametre": 139820, "couleur": "#d98c4a", "vitesse": 13.07},
            {"nom": "Saturne", "distance": 1433.5, "diametre": 116460, "couleur": "#e0b060", "vitesse": 9.69},
            {"nom": "Uranus", "distance": 2872.5, "diametre": 50724, "couleur": "#7ec8e0", "vitesse": 6.81},
            {"nom": "Neptune", "distance": 4495.1, "diametre": 49244, "couleur": "#4a6ee0", "vitesse": 5.43}
        ]
        
        # Position actuelle des planètes (angle en radians)
        self.positions = {p["nom"]: random.uniform(0, 2*math.pi) for p in self.planetes}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Zone de contrôle (gauche)
        control_frame = ttk.LabelFrame(main_frame, text="🛸 Contrôles", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Sélecteur de planète
        ttk.Label(control_frame, text="Planète de départ:").pack(anchor=tk.W, pady=2)
        self.depart_var = tk.StringVar(value="Terre")
        depart_combo = ttk.Combobox(control_frame, textvariable=self.depart_var, 
                                    values=[p["nom"] for p in self.planetes], 
                                    state="readonly", width=15)
        depart_combo.pack(anchor=tk.W, pady=2)
        
        ttk.Label(control_frame, text="Planète d'arrivée:").pack(anchor=tk.W, pady=2)
        self.arrivee_var = tk.StringVar(value="Mars")
        arrivee_combo = ttk.Combobox(control_frame, textvariable=self.arrivee_var,
                                     values=[p["nom"] for p in self.planetes],
                                     state="readonly", width=15)
        arrivee_combo.pack(anchor=tk.W, pady=2)
        
        ttk.Label(control_frame, text="Vitesse (km/s):").pack(anchor=tk.W, pady=(10,2))
        self.vitesse_var = tk.DoubleVar(value=50000)
        vitesse_scale = ttk.Scale(control_frame, from_=10000, to=200000, 
                                  orient=tk.HORIZONTAL, variable=self.vitesse_var,
                                  length=150)
        vitesse_scale.pack(anchor=tk.W, pady=2)
        self.vitesse_label = ttk.Label(control_frame, text="50 000 km/s")
        self.vitesse_label.pack(anchor=tk.W)
        vitesse_scale.configure(command=self.maj_vitesse_label)
        
        # Boutons
        ttk.Button(control_frame, text="🚀 Calculer distance", 
                  command=self.calculer_distance).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="⏱️ Calculer temps de voyage", 
                  command=self.calculer_temps).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="🔄 Simuler orbites", 
                  command=self.simuler_orbites).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="📊 Comparer planètes", 
                  command=self.comparer_planetes).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="ℹ️ Info système", 
                  command=self.afficher_infos).pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="🌌 Position actuelle", 
                  command=self.afficher_positions).pack(fill=tk.X, pady=5)
        
        # Résultats
        result_frame = ttk.LabelFrame(control_frame, text="📋 Résultats", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=15, width=30, 
                                    font=("Consolas", 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", 
                                   command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Zone de visualisation (droite)
        visu_frame = ttk.LabelFrame(main_frame, text="🪐 Visualisation", padding="10")
        visu_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(visu_frame, bg="#0a0a2a", width=500, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Barre d'état
        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Info initiale
        self.afficher_infos()
        self.dessiner_systeme()
        
    def maj_vitesse_label(self, value):
        """Met à jour le label de vitesse"""
        self.vitesse_label.config(text=f"{int(float(value)):,} km/s".replace(",", " "))
    
    def trouver_planete(self, nom):
        """Trouve les données d'une planète par son nom"""
        for p in self.planetes:
            if p["nom"] == nom:
                return p
        return None
    
    def calculer_distance(self):
        """Calcule la distance entre deux planètes"""
        depart = self.depart_var.get()
        arrivee = self.arrivee_var.get()
        
        p1 = self.trouver_planete(depart)
        p2 = self.trouver_planete(arrivee)
        
        if p1 and p2:
            # Calcul de la distance selon leurs positions actuelles
            angle1 = self.positions[depart]
            angle2 = self.positions[arrivee]
            
            # Coordonnées (en millions de km)
            x1 = p1["distance"] * math.cos(angle1)
            y1 = p1["distance"] * math.sin(angle1)
            x2 = p2["distance"] * math.cos(angle2)
            y2 = p2["distance"] * math.sin(angle2)
            
            # Distance
            distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # Distance minimale (quand alignées du même côté)
            dist_min = abs(p2["distance"] - p1["distance"])
            
            # Distance maximale (quand opposées)
            dist_max = p1["distance"] + p2["distance"]
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"🌍 DISTANCE {depart} → {arrivee}\n")
            self.result_text.insert(tk.END, "="*30 + "\n\n")
            self.result_text.insert(tk.END, f"Distance actuelle : {distance:.2f} M km\n")
            self.result_text.insert(tk.END, f"({distance*1000000:.0f} km)\n\n")
            self.result_text.insert(tk.END, f"Distance minimale : {dist_min:.2f} M km\n")
            self.result_text.insert(tk.END, f"Distance maximale : {dist_max:.2f} M km\n\n")
            
            # Proportion de la distance Terre-Lune
            distance_tl = 0.384  # millions de km
            rapport = distance / distance_tl
            self.result_text.insert(tk.END, f"Soit {rapport:.1f} × distance Terre-Lune\n")
            
            self.status_bar.config(text=f"Distance calculée: {distance:.2f} M km")
    
    def calculer_temps(self):
        """Calcule le temps de voyage à une vitesse donnée"""
        depart = self.depart_var.get()
        arrivee = self.arrivee_var.get()
        vitesse = self.vitesse_var.get()  # km/s
        
        p1 = self.trouver_planete(depart)
        p2 = self.trouver_planete(arrivee)
        
        if p1 and p2:
            # Distance actuelle en km
            angle1 = self.positions[depart]
            angle2 = self.positions[arrivee]
            
            x1 = p1["distance"] * math.cos(angle1) * 1e6
            y1 = p1["distance"] * math.sin(angle1) * 1e6
            x2 = p2["distance"] * math.cos(angle2) * 1e6
            y2 = p2["distance"] * math.sin(angle2) * 1e6
            
            distance_km = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # Temps en secondes
            temps_s = distance_km / vitesse
            
            # Conversion
            jours = temps_s / (24 * 3600)
            annees = jours / 365.25
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"⏱️ TEMPS DE VOYAGE\n")
            self.result_text.insert(tk.END, "="*30 + "\n\n")
            self.result_text.insert(tk.END, f"Distance: {distance_km/1e6:.2f} M km\n")
            self.result_text.insert(tk.END, f"Vitesse: {vitesse:,.0f} km/s\n\n".replace(",", " "))
            self.result_text.insert(tk.END, f"Temps: {temps_s:.1f} secondes\n")
            
            if jours < 1:
                heures = jours * 24
                self.result_text.insert(tk.END, f"Soit {heures:.1f} heures\n")
            elif jours < 30:
                self.result_text.insert(tk.END, f"Soit {jours:.1f} jours\n")
            elif jours < 365:
                mois = jours / 30.44
                self.result_text.insert(tk.END, f"Soit {mois:.1f} mois\n")
            else:
                self.result_text.insert(tk.END, f"Soit {annees:.2f} années\n")
            
            self.status_bar.config(text=f"Temps calculé: {jours:.1f} jours")
    
    def simuler_orbites(self):
        """Simule le mouvement des planètes"""
        # Avancer les positions
        for p in self.planetes:
            # Plus la planète est proche, plus elle tourne vite
            vitesse_angulaire = 0.01 / math.sqrt(p["distance"])
            self.positions[p["nom"]] += vitesse_angulaire
            
        self.dessiner_systeme()
        self.status_bar.config(text="🔄 Orbites simulées")
        
        # Programmer la prochaine simulation
        self.root.after(100, self.simuler_orbites)
    
    def dessiner_systeme(self):
        """Dessine le système solaire sur le canvas"""
        self.canvas.delete("all")
        
        # Centre du canvas
        cx, cy = 250, 250
        
        # Dessiner le Soleil
        self.canvas.create_oval(cx-15, cy-15, cx+15, cy+15, 
                                fill="#ffdd00", outline="orange", width=2)
        self.canvas.create_text(cx, cy-25, text="☀️ Soleil", fill="white")
        
        # Échelle: 1 pixel = 10 millions de km
        echelle = 0.4  # Ajusté pour que tout tienne
        
        # Dessiner les orbites
        for p in self.planetes:
            rayon = p["distance"] * echelle
            if rayon < 200:  # Ne pas dessiner les orbites trop grandes
                self.canvas.create_oval(cx-rayon, cy-rayon, cx+rayon, cy+rayon,
                                       outline="#333366", dash=(2,2))
        
        # Dessiner les planètes
        for p in self.planetes:
            rayon = p["distance"] * echelle
            if rayon < 200:  # Ne dessiner que les planètes visibles
                angle = self.positions[p["nom"]]
                x = cx + rayon * math.cos(angle)
                y = cy + rayon * math.sin(angle)
                
                # Taille relative
                taille = max(3, min(8, p["diametre"] / 15000))
                
                # Dessiner la planète
                self.canvas.create_oval(x-taille, y-taille, x+taille, y+taille,
                                       fill=p["couleur"], outline="white")
                
                # Nom de la planète
                if p["distance"] < 500:  # Ne nommer que les plus proches
                    self.canvas.create_text(x, y-15, text=p["nom"], 
                                           fill="white", font=("Arial", 8))
    
    def comparer_planetes(self):
        """Compare les caractéristiques des planètes"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "📊 COMPARAISON DES PLANÈTES\n")
        self.result_text.insert(tk.END, "="*40 + "\n\n")
        
        # Tableau
        self.result_text.insert(tk.END, f"{'Planète':<10} {'Distance':<12} {'Diamètre':<12} {'Vitesse':<12}\n")
        self.result_text.insert(tk.END, "-"*50 + "\n")
        
        for p in sorted(self.planetes, key=lambda x: x["distance"]):
            self.result_text.insert(tk.END, 
                f"{p['nom']:<10} {p['distance']:<12.1f} {p['diametre']:<12} {p['vitesse']:<12.2f}\n")
        
        # Planète la plus grande
        plus_grande = max(self.planetes, key=lambda x: x["diametre"])
        self.result_text.insert(tk.END, f"\n🏆 Plus grande: {plus_grande['nom']} "
                               f"({plus_grande['diametre']} km)")
    
    def afficher_infos(self):
        """Affiche les informations générales"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🌌 SYSTÈME SOLAIRE\n")
        self.result_text.insert(tk.END, "="*30 + "\n\n")
        self.result_text.insert(tk.END, "8 planètes reconnues\n")
        self.result_text.insert(tk.END, f"Mercure à {self.planetes[0]['distance']} M km\n")
        self.result_text.insert(tk.END, f"Neptune à {self.planetes[-1]['distance']} M km\n\n")
        
        # Distance Terre-Soleil (1 UA)
        self.result_text.insert(tk.END, "📏 1 UA (Terre-Soleil) = 149.6 M km\n\n")
        
        # Vitesse de la lumière
        self.result_text.insert(tk.END, "⚡ Vitesse de la lumière:\n")
        self.result_text.insert(tk.END, "  299 792 km/s\n")
        self.result_text.insert(tk.END, f"  Terre-Soleil: {149.6e6/299792:.1f} min\n")
        
        self.status_bar.config(text="Informations système affichées")
    
    def afficher_positions(self):
        """Affiche les positions actuelles des planètes"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "📍 POSITIONS ACTUELLES\n")
        self.result_text.insert(tk.END, "="*30 + "\n\n")
        
        for p in self.planetes:
            angle = self.positions[p["nom"]]
            degres = math.degrees(angle) % 360
            self.result_text.insert(tk.END, 
                f"{p['nom']:<8}: {degres:6.1f}° (rayon {p['distance']} M km)\n")

# Pour exécuter le programme
if __name__ == "__main__":
    root = tk.Tk()
    app = SystemeSolaire(root)
    root.mainloop()
