import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from queue import Queue


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.button = QPushButton("Add Message")
        self.button.clicked.connect(self.on_button_click)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.message_queue = Queue()
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Set the interval to 100 milliseconds
        self.timer.timeout.connect(self.process_messages)
        self.timer.start()
        self.count = 0

    def on_button_click(self):
        self.count += 1
        self.add_message(f"Message #{self.count}")

    def add_message(self, message):
        self.message_queue.put(message)

    def process_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            # Process the message
            print(f"Processing message: {message}")

app = QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec())