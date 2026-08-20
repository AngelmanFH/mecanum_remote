import sys
import socket
import threading
import struct
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit

class TcpClient(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.client_socket = None
        self.receive_thread = None

    def init_ui(self):
        self.setWindowTitle('TCP Client')

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Widgets
        self.ip_label = QLabel('IP Address:')
        self.ip_input = QLineEdit('10.0.0.254')
        self.port_label = QLabel('Port:')
        self.port_input = QLineEdit('54000')
        self.connect_button = QPushButton('Connect')
        self.disconnect_button = QPushButton('Disconnect')
        self.message_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.received_messages = QTextEdit()
        self.received_messages.setReadOnly(True)

        # Add widgets to layouts
        form_layout.addWidget(self.ip_label)
        form_layout.addWidget(self.ip_input)
        form_layout.addWidget(self.port_label)
        form_layout.addWidget(self.port_input)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel('Message:'))
        main_layout.addWidget(self.message_input)
        main_layout.addWidget(self.send_button)
        main_layout.addWidget(QLabel('Received Messages:'))
        main_layout.addWidget(self.received_messages)

        # Set main layout
        self.setLayout(main_layout)

        # Connect signals and slots
        self.connect_button.clicked.connect(self.connect_to_server)
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.send_button.clicked.connect(self.send_message)

    def connect_to_server(self):
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((ip, port))
            self.received_messages.append(f"Connected to {ip}:{port}")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            self.received_messages.append(f"Failed to connect: {e}")

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.received_messages.append("Disconnected from server")

    def send_message(self):
        if self.client_socket:
            message = self.message_input.text()
            if message:
                try:
                    # Send message length first
                    message_length = struct.pack('!I', len(message))
                    self.client_socket.sendall(message_length + message.encode())
                    self.message_input.clear()
                except Exception as e:
                    self.received_messages.append(f"Failed to send message: {e}")

    def receive_messages(self):
        while self.client_socket:
            try:
                # First, receive the length of the message (4 bytes, network byte order)
                length_data = self.client_socket.recv(4)
                if not length_data:
                    break
                message_length = struct.unpack('!I', length_data)[0]

                # Now, receive the actual message based on the received length
                message_data = self.client_socket.recv(message_length)
                if not message_data:
                    break
                message = message_data.decode()
                self.received_messages.append(f"Received: {message}")
            except Exception as e:
                self.received_messages.append(f"Error receiving message: {e}")
                break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = TcpClient()
    client.show()
    sys.exit(app.exec())
