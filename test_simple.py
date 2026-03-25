import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

print("1. Démarrage")

app = QApplication(sys.argv)
print("2. App créée")

class MaFenetre(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST - Cliquez sur le bouton")
        self.setGeometry(200, 200, 500, 300)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.label = QLabel("En attente de clic...")
        self.label.setAlignment(Qt.AlignCenter)  # Correction ici
        layout.addWidget(self.label)
        
        btn = QPushButton("Cliquez-moi !")
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)
        
        print("3. Fenêtre créée")
    
    def on_click(self):
        self.label.setText(" BRAVO ! Ça fonctionne !")
        print("4. Bouton cliqué")

print("5. Création de la fenêtre...")
window = MaFenetre()
window.show()
print("6. Fenêtre affichée")

print("7. Entrée dans la boucle...")
sys.exit(app.exec())
print("8. Fin")