import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

print("1. Début")
app = QApplication(sys.argv)
print("2. App créée")
window = QMainWindow()
print("3. Fenêtre créée")
window.setWindowTitle("Test Simple")
window.setGeometry(100, 100, 400, 300)

label = QLabel(" Test réussi !\n\nSi vous voyez ce message, l'interface fonctionne.")
label.setAlignment(Qt.AlignCenter)  # Correction ici
window.setCentralWidget(label)

window.show()
print("4. Fenêtre affichée")
print("5. Entrée dans la boucle d'événements...")
sys.exit(app.exec())
print("6. Fin")