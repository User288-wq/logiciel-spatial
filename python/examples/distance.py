import tkinter as tk
import math

def calculer_distance():
    # Exemple : Terre (0,0,0) et Lune
    x1, y1, z1 = 0, 0, 0
    x2, y2, z2 = 384000, 0, 0  # distance en km

    d = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    label_result.config(text=f"Distance: {d} km")

root = tk.Tk()
root.title("Simulation spatiale")

btn = tk.Button(root, text="Calcul Terre-Lune", command=calculer_distance)
btn.pack()

label_result = tk.Label(root, text="")
label_result.pack()

root.mainloop()