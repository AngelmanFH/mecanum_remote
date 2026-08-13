import struct
import sys
import threading
import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, \
    QStatusBar, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QMessageBox
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
import json

from client import MecanmControl
from ip_or_resolve import is_ip_address, resolve_hostname
from ssh_connection_widget import SshConnectionWidget

# for ssh to the raspberries
mecanum1 = "localhost"
mecanum1_user = "bernd"


class ConnectDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Connect")

        #self.last_ip = "luke.local"  # Default value
        self.last_ip = "luke.local" # "192.168.73.123"
        self.last_port = 54000  # Default value
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP Address")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port")

        form_layout = QFormLayout()
        form_layout.addRow("IP Address:", self.ip_input)
        form_layout.addRow("Port:", self.port_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.accepted.connect(self.save_input)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.load_input()

    def save_input(self):
        ip_address = self.ip_input.text()
        port = self.port_input.text()

        with open("last_connection.json", "w") as file:
            json.dump({"ip_address": ip_address, "port": port}, file)

    def load_input(self):
        try:
            with open("last_connection.json", "r") as file:
                data = json.load(file)
                self.ip_input.setText(data.get("ip_address", ""))
                self.port_input.setText(data.get("port", ""))
                print(f'data from file: ip_input: {data.get("ip_address", "")}, port: {data.get("port", "")}')
        except FileNotFoundError as e:
            print(f"Error: {e}")
            pass

    def get_ip_port(self):
        self.last_ip = self.ip_input.text()
        try:
            self.last_port = int(self.port_input.text())
        except ValueError:
            self.show_critical_dialog("Invalid port number, using default port 54000")
            self.last_port = 54000
        return self.last_ip, self.last_port

    def show_critical_dialog(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Conversion Error")
        msg_box.setText("An error occurred while converting the port number.")
        msg_box.setInformativeText(message)
        msg_box.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MECANUM GUI")

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.ssh_window = None


        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected")

        # Create menu bar
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Create "Connection" menu
        connection_menu = menu_bar.addMenu("Connection")

        # Create "Connect" action
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.show_connect_dialog)
        connection_menu.addAction(connect_action)

        # Create "Disconnect" action
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self._disconnect)
        connection_menu.addAction(disconnect_action)

        # Create "Connect" action
        connect_follower_action = QAction("Connect Follower", self)
        connect_follower_action.triggered.connect(self.show_follower_connect_dialog)
        connection_menu.addAction(connect_follower_action)

        # Create "Disconnect" action
        disconnect_follower_action = QAction("Disconnect Follower", self)
        disconnect_follower_action.triggered.connect(self.disconnect_follower)
        connection_menu.addAction(disconnect_follower_action)

        # Create "SSH Connection" action
        ssh_action = QAction("Open SSH Window", self)
        ssh_action.triggered.connect(self.open_ssh_window)
        connection_menu.addAction(ssh_action)

        self.socket = None

        self.client = MecanmControl(self.socket)
        layout.addWidget(self.client)

    @Slot()
    def show_connect_dialog(self):
        def show_error_message(hostname):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Host '{hostname}' could not be resolved.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        dialog = ConnectDialog(self)
        if dialog.exec():
            host_or_ip_address, port = dialog.get_ip_port()
            if not is_ip_address(host_or_ip_address):
                ip_address = resolve_hostname(host_or_ip_address)
                if not ip_address:
                    show_error_message(host_or_ip_address)
                    return
                else:
                    host_or_ip_address = ip_address
            self._connect(host_or_ip_address, port)

    @Slot()
    def show_follower_connect_dialog(self):
        if self.client.connected:
            dialog = ConnectDialog()
            dialog.setWindowTitle("Connect Follower")
            dialog.ip_input.setText("anakin.local")  # Default value
            dialog.port_input.setText("53999")  # Default value
            if dialog.exec():
                ip_address, port = dialog.get_ip_port()

                self.connect_follower(ip_address, port)

    def _connect(self, ip_address, port):
        self.status_bar.showMessage(f"Connecting to {ip_address}:{port}...")

        # Create a socket and connect to the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((ip_address, port))
            # self.socket.setblocking(False)
            self.status_bar.showMessage(f"Connected to {ip_address} at port {port}")
            self.client.client_socket = self.socket
            self.client.connected = True
            self.client.onConnect()

            # Start threads for receiving and sending data
            #receive_thread = threading.Thread(target=self.receive_data)
            #send_thread = threading.Thread(target=self.send_data)
            #receive_thread.start()
            #send_thread.start()
        except socket.error as e:
            self.status_bar.showMessage(f"Failed to connect: {e}")

    def connect_follower(self, ip_address, port):
        if self.client.connected:
            code = b'\x03'
            _port = struct.pack('!H', port)
            _ip_address = struct.pack(f'!{len(ip_address)}s', ip_address.encode())
            message = code + _port + _ip_address
            length = struct.pack('!I', len(message))
            self.socket.sendall(length + message)

    def _disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.client.client_socket = self.socket
            self.client.connected = False
            self.client.onDisconnect()
            self.status_bar.showMessage("Disconnected")

    def disconnect_follower(self):

        if self.client.connected:
            print("Disconnecting from follower")
            code = b'\x04'
            length = struct.pack('!I', len(code))
            message = length + code
            self.socket.sendall(message)

    def open_ssh_window(self):
        self.ssh_window = SshConnectionWidget(
            host=mecanum1,
            user=mecanum1_user,
            port=22,
        )
        self.ssh_window.show()

    # def receive_data(self):
    #     print("Started receiving data")
    #     while self.socket:
    #         try:
    #             data = self.socket.recv(1024)
    #             if not data:
    #                 break
    #             print(f"Received: {data.decode()}")
    #         except socket.error as e:
    #             print(f"Receive error: {e}")
    #             break
    #
    # def send_data(self):
    #     print("Started sending data")
    #     while self.socket:
    #         try:
    #             message = input("Enter message to send: ")
    #             self.socket.sendall(message.encode())
    #         except socket.error as e:
    #             print(f"Send error: {e}")
    #             break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
