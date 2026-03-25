import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

print("=== TEST INTERFACE MINIMALE ===")
print("1. Démarrage...")

app = QApplication(sys.argv)
print("2. QApplication créée")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST")
        self.setGeometry(200, 200, 500, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        label = QLabel(" INTERFACE FONCTIONNE !")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: green;")
        layout.addWidget(label)
        
        print("3. Fenêtre créée")

print("4. Création de la fenêtre...")
window = TestWindow()
window.show()
print("5. Fenêtre affichée")
print("6. Entrée dans la boucle...")

sys.exit(app.exec())
print("7. Fin")