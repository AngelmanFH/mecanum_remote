from PySide6.QtWidgets import QWidget, QApplication, QMessageBox, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
import sys

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quitter")
        self.setGeometry(200, 100,500, 200)

        layout = QVBoxLayout()

        self.label = QLabel('Quitter v0.1')
        self.label.setStyleSheet("font-size: 24px; color: red;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.quitme = QPushButton("QUIT")
        self.quitme.clicked.connect(QApplication.quit)
        self.quitme.setStyleSheet("font-size: 24px; color: orange;")
        layout.addWidget(self.quitme)

        self.setLayout(layout)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

app = QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec())