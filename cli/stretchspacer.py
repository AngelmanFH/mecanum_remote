from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Add a button
        button1 = QPushButton("Button 1")
        layout.addWidget(button1)

        # Add a stretchable space
        layout.addStretch()

        # Add another button
        button2 = QPushButton("Button 2")
        layout.addWidget(button2)

        # Add a fixed spacer item
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(spacer)

        # Add a third button
        button3 = QPushButton("Button 3")
        layout.addWidget(button3)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])

    widget = MyWidget()
    widget.show()

    app.exec()