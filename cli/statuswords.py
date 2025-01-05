from PySide6.QtWidgets import QMainWindow, QGridLayout, QLabel, QWidget, QGroupBox, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics, QFont
from controlandstatus import status_dict, det_status
import random


class ColorChangingLabel(QLabel):
    updateColorAndText = Signal(str, str, str)

    def __init__(self, s_dict=status_dict, padding=10, font_size=26, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updateColorAndText.connect(self.change_color_and_text)

        # Set the font size
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

        self.padding = padding

        # Find the maximum length key in status_dict
        max_key = max(s_dict.keys(), key=len)

        # Calculate the width of this text with current font settings
        fm = QFontMetrics(self.font())
        max_pixels = fm.horizontalAdvance(max_key) + 2 * padding + 10  # Added twice the padding value, and some

        # Set that width as this QLabel's fixed width
        self.setFixedWidth(max_pixels)

        # Set text alignment to center
        self.setAlignment(Qt.AlignCenter)

    def change_color_and_text(self, color, text, tooltip):
        self.setStyleSheet(f"QLabel {{ background-color : {color}; padding: {self.padding}px;}}")
        self.setText(text)
        self.setToolTip(tooltip)


class StatusLabels(QWidget):
    update_statusword = Signal(int, int)  # value, motor#
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a GroupBox
        self.groupbox = QGroupBox("Title - changeme")
        self.groupbox.setStyleSheet("QGroupBox {background-color: white;}")

        # Don't forget to set the layout of the main widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.groupbox)

        # Use the GroupBox layout for your grid layout
        grid_layout = QGridLayout(self.groupbox)

        # Create and set the title label
        self.title_label = QLabel("Title")
        title_font = QFont("Arial", 20, QFont.Bold)
        self.title_label.setFont(title_font)
        grid_layout.addWidget(self.title_label, 0, 0, 1, 2)  # Span the label across all columns

        self.labels = [ColorChangingLabel() for _ in range(4)]



        for i, label in enumerate(self.labels):
            grid_layout.addWidget(label, (i // 2) + 1, i % 2)  # Start adding labels from the second row

        all_status_values = list(value['value'] for value in status_dict.values())
        for i in range(len(self.labels)):
            # get the first value at startup
            value = all_status_values[0]
            self.update_label_info(value, i)

        self.update_statusword.connect(self.update_label_info)

    def update_label_info(self, val, which_motor):
        name, info, color = det_status(val)
        which_label = which_motor - 1  # motors are indexed from 1 to 4, self.labels from 0 to 3
        self.labels[which_label].updateColorAndText.emit(color, name, info)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = StatusLabels()
    window.show()

    sys.exit(app.exec())