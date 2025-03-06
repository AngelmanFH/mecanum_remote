import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PySide6.QtCore import Qt, Signal, Slot

class RotateWidget(QWidget):
    valueChanged = Signal(int)  # Define a custom signal

    def __init__(self):
        super().__init__()

        # Set up the layout
        layout = QVBoxLayout()

        # Create the title label
        self.title_label = QLabel("Rotate angular speed [mm/s]")
        layout.addWidget(self.title_label)

        # Create the slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-200)
        self.slider.setMaximum(200)
        self.slider.setValue(0)  # Default value
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(50)
        layout.addWidget(self.slider)

        # Connect the slider's valueChanged signal to the custom slot
        self.slider.valueChanged.connect(self.on_value_changed)

        # Create the reset button
        self.reset_button = QPushButton("Reset to Zero")
        self.reset_button.clicked.connect(self.reset_slider)
        layout.addWidget(self.reset_button)

        # Set the layout for the widget
        self.setLayout(layout)

    @Slot(int)
    def on_value_changed(self, value):
        # Emit the custom signal with the slider's value
        self.valueChanged.emit(value)
        print(f"Slider value: {value}")

    @Slot()
    def reset_slider(self):
        # Set the slider value to zero
        self.slider.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RotateWidget()
    widget.valueChanged.connect(lambda value: print(f"Custom signal emitted with value: {value}"))
    widget.show()
    sys.exit(app.exec())
