#!/usr/bin/python3

import sys
import socket
import threading
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt

# srv_addr = '192.168.43.30'
srv_addr = '10.0.0.14'
def_hosts = ['10.0.0.14', '192.168.43.30']

class SimpleGUI(QWidget):
    def __init__(self, client_socket):
        super().__init__()

        self.client_socket = client_socket

        self.setWindowTitle("Pop-Art GUI")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel('This is a Title')
        self.label.setStyleSheet("font-size: 24px; color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.text_field = QLineEdit()
        self.text_field.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_field)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['Option 1', 'Option 2', 'Option 3'])
        self.combo_box.currentTextChanged.connect(self.on_combobox_changed)
        layout.addWidget(self.combo_box)

        self.quitme = QPushButton("QUIT")
        self.quitme.clicked.connect(QApplication.quit)
        self.quitme.setStyleSheet("font-size: 24px; color: orange;")
        layout.addWidget(self.quitme)

        self.setLayout(layout)

        # Hintergrundbild laden
        self.background_pixmap = QPixmap("pop_art_image.jpg")  # Pfad zum Pop-Art-Bild
        
        # Start a thread to listen for messages from the server
        self.listening_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listening_thread.start()
        
        # Set up a timer to send keep-alive messages every 500 milliseconds
        self.keep_alive_timer = QTimer(self)
        self.keep_alive_timer.timeout.connect(self.send_keep_alive)
        self.keep_alive_timer.start(500)

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


    def on_text_changed(self, text):
        try:
            self.client_socket.sendall(f"Text changed: {text}".encode('utf-8'))
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")

    def on_combobox_changed(self, text):
        try:
            self.client_socket.sendall(f"Combobox selection changed: {text}".encode('utf-8'))
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")
        
    def send_keep_alive(self):
        try:
            self.client_socket.sendall(b"KEEP_ALIVE")
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")
            self.keep_alive_timer.stop()
        
    def listen_for_messages(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.update_label(message)
        except (socket.error, ConnectionResetError) as e:
            self.update_label(f"Connection lost: {e}")
                
    def update_label(self, text):
        self.label.setText(text)

    def _quit(self):
        self.parent.quit()


def connect_to_host(hostname, port):
    try:
        # Get all IP addresses associated with the hostname
        host_info = socket.gethostbyname_ex(hostname)
        ip_addresses = host_info[2]
        print(ip_addresses)

    except socket.gaierror as e:
        print(f"Error resolving hostname {hostname}: {e}\nTrying default IP-Addresses...")
        ip_addresses = def_hosts

    for ip in ip_addresses:
        # try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attem               pt
        try:
            # Attempt to connect to the IP address
            sock.connect((ip, port))
            print(f"Successfully connected to {hostname} ({ip}) on port {port}")
            return sock  # Return the connected socket

        except socket.error as e:
            print(f"Failed to connect to {ip}: {e}")
            sock.close()

        #finally:
            #sock.close()

    print(f"Could not connect to any IP addresses for {hostname}")
    return None


def main():
    # hostname = 'anakin'
    # ip_address = socket.gethostbyname(hostname)
    # print("IP Address:", ip_address)
    hostname = 'anakin'
    port = 54000
    client_socket = connect_to_host(hostname, port)


    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     client_socket.connect((srv_addr, 54000))
    # except socket.error as e:
    #     print(f"Failed to connect: {e}")
    #     #return
        
    if client_socket:
        app = QApplication(sys.argv)
        gui = SimpleGUI(client_socket)
        gui.show()
        app.exec()

        client_socket.close()
        return 0
    else:
        print(f"Could not connect to host {hostname}")
        return -1

if __name__ == '__main__':
    main()
    # sys.exit(main())
