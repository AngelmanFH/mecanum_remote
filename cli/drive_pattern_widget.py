from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout, QGroupBox
)

import sys

from action_timer import ActionTimerAngleDist


class DrivePatternWidget(QWidget):
    action_signal = Signal(int, int)
    def __init__(self):
        super().__init__()

        self.speed_list = []
        self.angle_list = []
        self.distance_list = []

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.speed_input = QLineEdit()
        self.angle_input = QLineEdit()
        self.distance_input = QLineEdit()

        form_layout.addRow("Speed:", self.speed_input)
        form_layout.addRow("Angle:", self.angle_input)
        form_layout.addRow("Distance:", self.distance_input)

        self.submit_button = QPushButton("Submit")
        self.clear_button = QPushButton("Clear")

        self.submit_button.clicked.connect(self.submit)
        self.clear_button.clicked.connect(self.clear)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.clear_button)

        self.text_edit = QTextEdit()

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.text_edit)

        self.final_submit_button = QPushButton("Final Submit")
        self.final_submit_button.clicked.connect(self.final_submit)
        layout.addWidget(self.final_submit_button)

        # Create a GroupBox
        self.groupbox = QGroupBox("ride a pattern")
        self.groupbox.setStyleSheet("QGroupBox {background-color: white;}")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.groupbox)

        self.groupbox.setLayout(layout)

        # self.setLayout(layout)

    def submit(self):
        speed = int(self.speed_input.text())
        angle = int(self.angle_input.text())
        distance = int(self.distance_input.text())

        self.speed_list.append(speed)
        self.angle_list.append(angle)
        self.distance_list.append(distance)

        self.text_edit.append(f"{speed}\t{angle}\t{distance}")

    def clear(self):
        self.text_edit.clear()
        self.speed_list.clear()
        self.angle_list.clear()
        self.distance_list.clear()

    def final_submit(self):
        def action(angle, speed):
            self.action_signal.emit(angle, speed)
            print(f"Action performed with angle: {angle} and speed: {speed}")

        action_timer = ActionTimerAngleDist(action, self.speed_list, self.angle_list, self.distance_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DrivePatternWidget()
    widget.action_signal.connect(lambda angle, dist: print(f"Signal emitted with angle: {angle} and speed: {dist}"))
    widget.show()
    sys.exit(app.exec())
