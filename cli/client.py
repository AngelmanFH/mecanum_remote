#!/usr/bin/python3

import struct
import sys
import socket
import threading
import time
import select

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QMessageBox, QHBoxLayout, QSizePolicy, QSpacerItem
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, Slot
from joystick_flexsize import DraggableCircleWidget
from go_stop import StopButton, GoButton
from statuswords import StatusLabels

# from sdo_req import SdoReadWrite

srv_addr = '192.168.43.32'
# srv_addr = '10.0.0.14'
def_hosts = ['10.0.0.254', '127.0.0.1', '192.168.43.32', '10.0.0.14', ]

HOSTNAME = 'anakin.home'


class MecanmControl(QWidget):
    def __init__(self, client_socket):
        super().__init__()

        self.client_socket = client_socket

        self.setWindowTitle("MECANUM GUI")
        self.setGeometry(100, 100, 1200, 540)

        layout = QVBoxLayout()

        self.label = QLabel('Feedback Text')
        self.label.setStyleSheet("font-size: 14px; color: red;")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # self.joy = DraggableCircleWidget(lambda x, y: print(f"x: {x}, y:{y}"))
        self.joy = DraggableCircleWidget()
        layout.addWidget(self.joy)
        self.joy.positionChanged.connect(self.send_position_tcp)

        # self.text_field = QLineEdit()
        # self.text_field.textChanged.connect(self.on_text_changed)
        # layout.addWidget(self.text_field)

        # self.combo_box = QComboBox()
        # self.combo_box.addItems(['Option 1', 'Option 2', 'Option 3'])
        # self.combo_box.currentTextChanged.connect(self.on_combobox_changed)
        # layout.addWidget(self.combo_box)

        self.quitme = QPushButton("QUIT")
        self.quitme.clicked.connect(QApplication.quit)
        self.quitme.setStyleSheet("font-size: 24px; color: orange;")
        layout.addWidget(self.quitme)

        # self.sdo_comm = SdoReadWrite()
        # self.sdo_comm.send_sdo_read_req.connect(self.send_sdo_upload)
        # motor status
        self.motor_status = StatusLabels()
        self.motor_status.groupbox.setTitle('Leader')
        self.motor_status.title_label.setText('Leader')
        self.motor_status_follower = StatusLabels()
        self.motor_status_follower.groupbox.setTitle('Follower')
        self.motor_status_follower.title_label.setText('Follower')

        sdo_lay = QVBoxLayout()
        sdo_lay.addWidget(self.motor_status)
        sdo_lay.addStretch()
        # sdo_lay.addWidget(self.sdo_comm)
        sdo_lay.addWidget(self.motor_status_follower)
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        sdo_lay.addSpacerItem(spacer)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addStretch(0)
        main_layout.addLayout(sdo_lay)

        vlayout2 = QVBoxLayout()

        self.setLayout(main_layout)

        # Hintergrundbild laden
        import os

        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.background_pixmap = QPixmap(os.path.join(script_dir, "mecanum_gui.png"))

        # stop und go buttons
        self.go = GoButton(50, parent=self)
        self.stop = StopButton(50, parent=self)
        self.go.clicked.connect(self.send_motctrl)
        self.stop.clicked.connect(self.send_motctrl)

        vlayout2.addWidget(self.go)
        vlayout2.addWidget(self.stop)
        vlayout2.addStretch(0)

        self.go_f = GoButton(50, parent=self)
        self.stop_f = StopButton(50, parent=self)
        self.go_f.clicked.connect(self.send_motctrl_f)
        self.stop_f.clicked.connect(self.send_motctrl_f)

        vlayout2.addWidget(self.go_f)
        vlayout2.addWidget(self.stop_f)

        main_layout.addLayout(vlayout2)

        # Start a thread to listen for messages from the server
        self.listening_thread = None
        # self.listening_thread.start()

        # Set up a timer to send keep-alive messages every 500 milliseconds
        self.keep_alive_timer = QTimer(self)
        self.keep_alive_timer.timeout.connect(self.send_keep_alive)
        self.keep_alive_timer.start(500)

        self.connected = False

    def onConnect(self):
        if self.client_socket:
            # Join old threads if they exist
            if self.listening_thread and self.listening_thread.is_alive():
                self.listening_thread.join()
            self.listening_thread = threading.Thread(target=self.listen_for_messages)  # , daemon=True)
            self.listening_thread.start()

    def onDisconnect(self):
        self.connected = False
        # Join old threads if they exist
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join()
            self.listening_thread = None

    def paintEvent(self, event):
        painter = QPainter(self)
        target_rect = self.rect()
        source_rect = self.background_pixmap.rect()

        # Berechne das Seitenverhältnis
        try:
            target_aspect_ratio = target_rect.width() / target_rect.height()
        except ZeroDivisionError:
            target_aspect_ratio = 1
        try:
            source_aspect_ratio = source_rect.width() / source_rect.height()
        except ZeroDivisionError:
            source_aspect_ratio = 1

        if target_aspect_ratio > source_aspect_ratio:
            # Ziel ist breiter als Quelle
            new_height = target_rect.height()
            new_width = int(new_height * source_aspect_ratio)
        else:
            # Ziel ist höher als Quelle
            new_width = target_rect.width()
            new_height = int(new_width / source_aspect_ratio)

        scaled_pixmap = self.background_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio,
                                                      Qt.SmoothTransformation)
        x_offset = (target_rect.width() - new_width) // 2
        y_offset = (target_rect.height() - new_height) // 2

        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

    @staticmethod
    def pack_string(string: str) -> bytes:
        # this is the payload
        encoded_text = string.encode('utf-8')
        # this is prepended to the payload, so the receiver knows how many subsequent bytes to read exactly
        length = len(encoded_text)
        # all is sent in one go -- receiver will split the operation into two parts
        return struct.pack('!I', length) + encoded_text

    def send_keep_alive(self):
        if self.client_socket:
            code = 0x00  # code for keep_alive
            payload_text = "KEEP_ALIVE".encode('utf-8')
            payload = struct.pack('!B', code) + payload_text
            length = len(payload)
            data = struct.pack('!I', length) + payload
            try:
                self.client_socket.sendall(data)
            except socket.error as e:
                # raise e
                self.update_label(f"Connection lost: {e}")
                self.keep_alive_timer.stop()
                self.connected = False

    def listen_for_messages(self):
        try:
            while self.connected:
                # print("Listening for messages...")
                ready_to_read, ready_to_write, in_error = select.select([self.client_socket], [], [], 0.1)
                if not ready_to_read:
                    continue  # No data ready to be read yet, go check again
                try:
                    raw_length = self.client_socket.recv(4)
                except AttributeError:  # when connection is closed while select waits,
                    # the socket will be consequently None
                    continue
                except socket.error as e:
                    self.update_label(f"Connection lost: {e}")
                    self.connected = False
                    break
                length = struct.unpack('!I', raw_length)[0]
                message = self.client_socket.recv(length)
                if message:
                    self.handle_incoming_message(message)
        except (socket.error, ConnectionResetError) as e:
            self.update_label(f"Connection lost: {e}")
            self.connected = False

    def handle_incoming_message(self, message):
        command = struct.unpack('!B', message[0:1])[0]  # Unpack the first byte
        rest_payload = message[1:]  # Get the rest of the payload
        if command == 100:
            self.handle_motor_status(rest_payload)
        elif command == 101:
            self.handle_follower_motor_status(rest_payload)
        elif command == 150:
            self.handle_general_message(rest_payload)
        else:
            print(f"Received message: {message}")
            self.update_label(message)

    def handle_general_message(self, payload):
        self.update_label(payload.decode())

    def handle_motor_status(self, payload):
        node_id, _type, value = struct.unpack('!BBh', payload)
        # print(f"node_id: {int(node_id)}, _type: {int(_type)}, value: {value}")
        if _type == 0:  # Statusword
            self.motor_status.update_statusword.emit(value, node_id)
        elif _type == 1:  # Modes of operation display
            self.update_label(f"Motor (leader) {node_id}: Modes of operation display: {int(value)}")

    def handle_follower_motor_status(self, payload):
        node_id, _type, value = struct.unpack('!BBh', payload)
        # print(f"node_id: {int(node_id)}, _type: {int(_type)}, value: {value}")
        if _type == 0:  # Statusword
            self.motor_status_follower.update_statusword.emit(value, node_id)
        elif _type == 1:  # Modes of operation display
            self.update_label(f"Motor (follower) {node_id}: Modes of operation display: {int(value)}")

    def update_label(self, text):
        self.label.setText(text)

    @Slot(float, float)
    def send_position_tcp(self, x, y):
        if not self.connected:
            return
        # Prepare the data
        prefix = b'\x01'  # message signature for joystick position
        data = struct.pack('!Bff', prefix[0], x, y)

        # Calculate the length of the message
        message_length = len(data)

        # Encode the length of the message
        length_prefix = struct.pack('!I', message_length)

        # Combine the length prefix and the actual data
        message = length_prefix + data

        # Send the data
        try:
            self.client_socket.sendall(message)
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")

    @Slot(str)
    def send_motctrl(self, whattodo):
        if not self.connected:
            return
        if whattodo == "on":
            on = True
        elif whattodo == 'off':
            on = False
        else:
            print("Illegal motctrl value")
            exit(1)
        prefix = b'\x02'  # message signature for motctrl
        payload = struct.pack('!B?', prefix[0], on)
        length = struct.pack('!I', len(payload))
        try:
            self.client_socket.sendall(length + payload)
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")

    @Slot(str)
    def send_motctrl_f(self, whattodo):
        if not self.connected:
            return
        if whattodo == "on":
            on = True
        elif whattodo == 'off':
            on = False
        else:
            print("Illegal motctrl value")
            exit(1)
        prefix = b'\x05'  # message signature for motctrl_follower
        payload = struct.pack('!B?', prefix[0], on)
        length = struct.pack('!I', len(payload))
        try:
            self.client_socket.sendall(length + payload)
        except socket.error as e:
            self.update_label(f"Connection lost: {e}")


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
        sock.settimeout(1)  # Set a timeout for the connection attempt
        try:
            # Attempt to connect to the IP address
            sock.connect((ip, port))
            print(f"Successfully connected to {hostname} ({ip}) on port {port}")
            return sock  # Return the connected socket

        except socket.error as e:
            print(f"Failed to connect to {ip}: {e}")
            sock.close()

        # finally:
        # sock.close()

    print(f"Could not connect to any IP addresses for {hostname}")
    return None


def main():
    # hostname = 'anakin'
    # ip_address = socket.gethostbyname(hostname)
    # print("IP Address:", ip_address)
    hostname = HOSTNAME
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
        gui = MecanmControl(client_socket)
        gui.show()
        app.exec()

        client_socket.close()
        return 0
    else:
        print(f"Could not connect to host {hostname}")
        return -1


if __name__ == '__main__':
    # main()
    sys.exit(main())
