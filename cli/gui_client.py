import configparser
import os
import struct
import sys
# import threading
# import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, \
    QStatusBar, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QMessageBox
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction
from PySide6.QtNetwork import QAbstractSocket, QTcpSocket

from client import MecanmControl
from ip_or_resolve import is_ip_address, resolve_hostname
from ssh_connection_widget import SshConnectionWidget

# for ssh to the raspberries
mecanum1 = "anakin.local"
mecanum1_user = "pi"

mecanum2 = "luke.local"
mecanum2_user = "pi"

CONFIG_FILE = "config.ini"
HINT_START_SERVER = "start the server first (ssh-window)"


class ConnectDialog(QDialog):
    def __init__(self, parent=None, section="connection", default_ip="anakin.local", default_port=54000):
        super().__init__(parent)

        self.section = section
        self.default_ip = default_ip
        self.default_port = default_port

        self.setWindowTitle("Connect")

        self.last_ip = self.default_ip
        self.last_port = self.default_port
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP Address")

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port")

        form_layout = QFormLayout()
        form_layout.addRow("IP Address:", self.ip_input)
        form_layout.addRow("Port:", self.port_input)

        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
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

        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)

        if not config.has_section(self.section):
            config.add_section(self.section)

        config.set(self.section, "ip_address", ip_address)
        config.set(self.section, "port", str(port))

        with open(CONFIG_FILE, "w") as file:
            config.write(file)

    def load_input(self):
        config = configparser.ConfigParser()
        ip_address = self.default_ip
        port = str(self.default_port)

        if os.path.exists(CONFIG_FILE):
            try:
                config.read(CONFIG_FILE)
                if config.has_section(self.section):
                    ip_address = config.get(self.section, "ip_address", fallback=self.default_ip)
                    port = config.get(self.section, "port", fallback=str(self.default_port))
            except Exception as e:
                print(f"Error: {e}")

        self.ip_input.setText(ip_address)
        self.port_input.setText(str(port))
        print(f'data from file: ip_input: {ip_address}, port: {port}')

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
        msg_box.setIcon(QMessageBox.Icon.Critical)
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
        self.connect_action = QAction("Connect", self)
        self.connect_action.setEnabled(False)
        self.connect_action.setToolTip(HINT_START_SERVER)
        self.connect_action.setStatusTip(HINT_START_SERVER)
        self.connect_action.triggered.connect(self.show_connect_dialog)
        connection_menu.addAction(self.connect_action)

        # Create "Disconnect" action
        self.disconnect_action = QAction("Disconnect", self)
        self.disconnect_action.setEnabled(False)
        self.disconnect_action.setToolTip(HINT_START_SERVER)
        self.disconnect_action.setStatusTip(HINT_START_SERVER)
        self.disconnect_action.triggered.connect(self._disconnect)
        connection_menu.addAction(self.disconnect_action)

        # Create "Connect Follower" action
        self.connect_follower_action = QAction("Connect Follower", self)
        self.connect_follower_action.setEnabled(False)
        self.connect_follower_action.setToolTip(HINT_START_SERVER)
        self.connect_follower_action.setStatusTip(HINT_START_SERVER)
        self.connect_follower_action.triggered.connect(self.show_follower_connect_dialog)
        connection_menu.addAction(self.connect_follower_action)

        # Create "Disconnect Follower" action
        self.disconnect_follower_action = QAction("Disconnect Follower", self)
        self.disconnect_follower_action.setEnabled(False)
        self.disconnect_follower_action.setToolTip(HINT_START_SERVER)
        self.disconnect_follower_action.setStatusTip(HINT_START_SERVER)
        self.disconnect_follower_action.triggered.connect(self.disconnect_follower)
        connection_menu.addAction(self.disconnect_follower_action)


        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.on_socket_connected)
        self.socket.disconnected.connect(self.on_socket_disconnected)
        self.socket.errorOccurred.connect(self.on_socket_error)

        self.pending_ip_address = None
        self.pending_port = None
        self.primary_server_ready = False
        self.follower_server_ready = False
        self.follower_connected = False

        self.client = MecanmControl(self.socket)
        layout.addWidget(self.client)

        ssh_layout = QHBoxLayout()
        self.ssh_widget_1 = SshConnectionWidget(
            host=mecanum1,
            user=mecanum1_user,
            port=22,
        )
        self.ssh_widget_2 = SshConnectionWidget(
            host=mecanum2,
            user=mecanum2_user,
            port=22,
        )
        self.ssh_widget_1.server_ready.connect(self.on_server_ready_primary)
        self.ssh_widget_2.server_ready.connect(self.on_server_ready_follower)
        self.ssh_widget_1.process.finished.connect(self.on_ssh_1_finished)
        self.ssh_widget_2.process.finished.connect(self.on_ssh_2_finished)
        ssh_layout.addWidget(self.ssh_widget_1)
        ssh_layout.addWidget(self.ssh_widget_2)
        layout.addLayout(ssh_layout)

    @Slot()
    def on_server_ready_primary(self):
        self.primary_server_ready = True
        if not self.client.connected:
            self.connect_action.setEnabled(True)
            self.connect_action.setToolTip("")
            self.connect_action.setStatusTip("")
        self.status_bar.showMessage("Primary server ready on mecanum1 (anakin.local)")

    @Slot()
    def on_server_ready_follower(self):
        self.follower_server_ready = True
        if not self.follower_connected:
            self.connect_follower_action.setEnabled(True)
            self.connect_follower_action.setToolTip("")
            self.connect_follower_action.setStatusTip("")
        self.status_bar.showMessage("Follower server ready on mecanum2 (luke.local)")

    @Slot()
    def on_ssh_1_finished(self):
        self.primary_server_ready = False
        if not self.client.connected:
            self.connect_action.setEnabled(False)
            self.connect_action.setToolTip(HINT_START_SERVER)
            self.connect_action.setStatusTip(HINT_START_SERVER)

    @Slot()
    def on_ssh_2_finished(self):
        self.follower_server_ready = False
        if not self.follower_connected:
            self.connect_follower_action.setEnabled(False)
            self.connect_follower_action.setToolTip(HINT_START_SERVER)
            self.connect_follower_action.setStatusTip(HINT_START_SERVER)

    @Slot()
    def show_connect_dialog(self):
        def show_error_message(hostname):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Host '{hostname}' could not be resolved.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

        dialog = ConnectDialog(parent=self, section="connection", default_ip="anakin.local", default_port=54000)
        dialog.setWindowTitle("Connect")
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
            dialog = ConnectDialog(parent=self, section="follower", default_ip="luke.local", default_port=53999)
            dialog.setWindowTitle("Connect Follower")
            if dialog.exec():
                ip_address, port = dialog.get_ip_port()

                self.connect_follower(ip_address, port)

    # def _connect(self, ip_address, port):
    #     self.status_bar.showMessage(f"Connecting to {ip_address}:{port}...")
    #
    #     # Create a socket and connect to the server
    #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #
    #     try:
    #         self.socket.connect((ip_address, port))
    #         # self.socket.setblocking(False)
    #         self.status_bar.showMessage(f"Connected to {ip_address} at port {port}")
    #         self.client.client_socket = self.socket
    #         self.client.connected = True
    #         self.client.onConnect()
    #
    #         # Start threads for receiving and sending data
    #         #receive_thread = threading.Thread(target=self.receive_data)
    #         #send_thread = threading.Thread(target=self.send_data)
    #         #receive_thread.start()
    #         #send_thread.start()
    #     except socket.error as e:
    #         self.status_bar.showMessage(f"Failed to connect: {e}")

    def _connect(self, ip_address, port):
        self.pending_ip_address = ip_address
        self.pending_port = port

        self.status_bar.showMessage(f"Connecting to {ip_address}:{port}...")
        self.socket.connectToHost(ip_address, port)

    @Slot()
    def on_socket_connected(self):
        self.status_bar.showMessage(
            f"Connected to {self.pending_ip_address} at port {self.pending_port}"
        )
        self.connect_action.setEnabled(False)
        self.disconnect_action.setEnabled(True)
        self.disconnect_action.setToolTip("")
        self.disconnect_action.setStatusTip("")
        self.client.client_socket = self.socket
        self.client.connected = True
        self.client.onConnect()

    @Slot()
    def on_socket_disconnected(self):
        self.client.connected = False
        self.client.onDisconnect()
        self.follower_connected = False
        self.disconnect_action.setEnabled(False)
        self.disconnect_action.setToolTip(HINT_START_SERVER)
        self.disconnect_action.setStatusTip(HINT_START_SERVER)
        self.disconnect_follower_action.setEnabled(False)
        self.disconnect_follower_action.setToolTip(HINT_START_SERVER)
        self.disconnect_follower_action.setStatusTip(HINT_START_SERVER)
        if self.primary_server_ready:
            self.connect_action.setEnabled(True)
            self.connect_action.setToolTip("")
            self.connect_action.setStatusTip("")
        else:
            self.connect_action.setEnabled(False)
            self.connect_action.setToolTip(HINT_START_SERVER)
            self.connect_action.setStatusTip(HINT_START_SERVER)
        if self.follower_server_ready:
            self.connect_follower_action.setEnabled(True)
            self.connect_follower_action.setToolTip("")
            self.connect_follower_action.setStatusTip("")
        else:
            self.connect_follower_action.setEnabled(False)
            self.connect_follower_action.setToolTip(HINT_START_SERVER)
            self.connect_follower_action.setStatusTip(HINT_START_SERVER)
        self.status_bar.showMessage("Disconnected")

    @Slot(QAbstractSocket.SocketError)
    def on_socket_error(self, socket_error):
        self.status_bar.showMessage(f"Connection error: {self.socket.errorString()}")

    def connect_follower(self, ip_address, port):
        if self.client.connected:
            code = b'\x03'
            _port = struct.pack('!H', port)
            _ip_address = struct.pack(f'!{len(ip_address)}s', ip_address.encode())
            message = code + _port + _ip_address
            length = struct.pack('!I', len(message))
            # self.socket.sendall(length + message)
            self.socket.write(length + message)
            self.follower_connected = True
            self.connect_follower_action.setEnabled(False)
            self.disconnect_follower_action.setEnabled(True)
            self.disconnect_follower_action.setToolTip("")
            self.disconnect_follower_action.setStatusTip("")

    # def _disconnect(self):
    #     if self.socket:
    #         self.socket.close()
    #         self.socket = None
    #         self.client.client_socket = self.socket
    #         self.client.connected = False
    #         self.client.onDisconnect()
    #         self.status_bar.showMessage("Disconnected")

    def _disconnect(self):
        if self.socket.state() != QAbstractSocket.SocketState.UnconnectedState:
            self.socket.disconnectFromHost()
        else:
            self.status_bar.showMessage("Already disconnected")

    def disconnect_follower(self):

        if self.client.connected:
            print("Disconnecting from follower")
            code = b'\x04'
            length = struct.pack('!I', len(code))
            message = length + code
            # self.socket.sendall(message)
            self.socket.write(message)
            self.follower_connected = False
            self.disconnect_follower_action.setEnabled(False)
            self.disconnect_follower_action.setToolTip(HINT_START_SERVER)
            self.disconnect_follower_action.setStatusTip(HINT_START_SERVER)
            if self.follower_server_ready:
                self.connect_follower_action.setEnabled(True)
                self.connect_follower_action.setToolTip("")
                self.connect_follower_action.setStatusTip("")
            else:
                self.connect_follower_action.setEnabled(False)
                self.connect_follower_action.setToolTip(HINT_START_SERVER)
                self.connect_follower_action.setStatusTip(HINT_START_SERVER)


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
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
