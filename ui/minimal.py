import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

print("=== DÉMARRAGE ===")

app = QApplication(sys.argv)
print("App créée")

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Minimal")
        self.setGeometry(100, 100, 600, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        label = QLabel(" INTERFACE FONCTIONNE !")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: green; background-color: #16213e; padding: 20px;")
        layout.addWidget(label)
        
        print("Fenêtre initialisée")

print("Création de la fenêtre...")
window = MinimalWindow()
window.show()
print("Fenêtre affichée")

print("Entrée dans la boucle...")
sys.exit(app.exec())
print("Fin")