from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QApplication, QGroupBox, QVBoxLayout
from PySide6.QtCore import Signal, Slot
import sys

class RotateAtWidget(QWidget):
    send_values = Signal(int, int, int)

    def __init__(self):
        super().__init__()

        self.group_box = QGroupBox("Rotate Around a Center Point")
        self.form_layout = QFormLayout()

        self.x_input = QLineEdit(self)
        self.form_layout.addRow("X:", self.x_input)

        self.y_input = QLineEdit(self)
        self.form_layout.addRow("Y:", self.y_input)

        self.speed_input = QLineEdit(self)
        self.form_layout.addRow("Speed:", self.speed_input)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.form_layout.addWidget(self.send_button)

        self.group_box.setLayout(self.form_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.group_box)
        self.setLayout(self.main_layout)

        # Set background color to white
        self.setStyleSheet("background-color: white;")

    @Slot()
    def on_send_button_clicked(self):
        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            speed = int(self.speed_input.text())
            self.send_values.emit(x, y, speed)
        except ValueError:
            print("Please enter valid integer values.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RotateAtWidget()
    widget.send_values.connect(lambda x, y, speed: print(f"Values sent: x={x}, y={y}, speed={speed}"))
    widget.show()
    sys.exit(app.exec())
