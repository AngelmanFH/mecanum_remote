from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt

class PopArtWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pop-Art GUI")
        self.setGeometry(100, 100, 800, 600)

        # Layout für Vordergrund-Widgets
        layout = QVBoxLayout()

        # Titel
        self.title_label = QLabel("Pop-Art GUI", self)
        self.title_label.setStyleSheet("font-size: 24px; color: white;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Textfeld
        self.text_field = QLineEdit(self)
        self.text_field.setPlaceholderText("Geben Sie etwas ein...")
        layout.addWidget(self.text_field)

        # Combobox
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(self.combo_box)

        # Layout auf das Hauptfenster anwenden
        self.setLayout(layout)

        # Hintergrundbild laden
        self.background_pixmap = QPixmap("pop_art_image.jpg")  # Pfad zum Pop-Art-Bild

    def paintEvent(self, event):
        painter = QPainter(self)
        target_rect = self.rect()
        source_rect = self.background_pixmap.rect()

        # Berechne das Seitenverhältnis
        target_aspect_ratio = target_rect.width() / target_rect.height()
        source_aspect_ratio = source_rect.width() / source_rect.height()

        if target_aspect_ratio > source_aspect_ratio:
            # Ziel ist breiter als Quelle
            new_height = target_rect.height()
            new_width = int(new_height * source_aspect_ratio)
        else:
            # Ziel ist höher als Quelle
            new_width = target_rect.width()
            new_height = int(new_width / source_aspect_ratio)

        scaled_pixmap = self.background_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x_offset = (target_rect.width() - new_width) // 2
        y_offset = (target_rect.height() - new_height) // 2

        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

if __name__ == "__main__":
    app = QApplication([])
    window = PopArtWindow()
    window.show()
    app.exec()
