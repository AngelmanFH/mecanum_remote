import sys
from pathlib import Path
key_path = Path.home() / ".ssh" / "id_ed25519"

from PySide6.QtCore import QProcess, QTimer, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SshConnectionWidget(QWidget):
    server_ready = Signal()
    output_received = Signal(str)

    def __init__(self, host="example.com", user=None, port=22, parent=None):
        super().__init__(parent)

        self.host = host
        self.user = user
        self.port = port
        self._stdout_buffer = ""
        self._stderr_buffer = ""

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.started.connect(self.on_started)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_error)

        self.setWindowTitle("SSH Connection")

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "QTextEdit { background-color: #111; color: #ddd; font-family: Menlo; }"
        )

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type command and press Enter")
        self.input_line.returnPressed.connect(self.send_input)

        self.connect_button = QPushButton("Connect to Pi")
        self.connect_button.clicked.connect(self.connect_ssh)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_ssh)
        self.disconnect_button.setEnabled(False)

        self.run_test_script_button = QPushButton("Start Mecanum-App on Pi")
        self.run_test_script_button.clicked.connect(self.run_test_script)
        self.run_test_script_button.setEnabled(False)

        self.ctrl_c_button = QPushButton("Quit Mecanum-App (Ctrl+C)")
        self.ctrl_c_button.clicked.connect(self.send_ctrl_c)
        self.ctrl_c_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        button_layout.addWidget(self.run_test_script_button)
        button_layout.addWidget(self.ctrl_c_button)

        layout = QVBoxLayout()
        layout.addWidget(self.output)
        layout.addWidget(self.input_line)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.resize(800, 500)

    def build_target(self):
        if self.user:
            return f"{self.user}@{self.host}"
        return self.host

    @Slot()
    def connect_ssh(self):
        if self.process.state() != QProcess.NotRunning:
            return

        target = self.build_target()

        args = [
            "-tt",
            "-o",
            "IdentitiesOnly=yes",
            "-i",
            key_path,
            "-p",
            str(self.port),
            target,
        ]

        self.output.append(f"$ ssh {' '.join(args)}")
        self.process.start("ssh", args)

    @Slot()
    def disconnect_ssh(self):
        if self.process.state() != QProcess.NotRunning:
            self.output.append("\nDisconnect requested.")
            self.process.write(b"exit\n")
            QTimer.singleShot(3000, self.terminate_if_still_running)

    def terminate_if_still_running(self):
        if self.process.state() != QProcess.NotRunning:
            self.output.append("SSH did not exit after sending 'exit'. Terminating process.")
            self.process.terminate()
            QTimer.singleShot(3000, self.kill_if_still_running)

    def kill_if_still_running(self):
        if self.process.state() != QProcess.NotRunning:
            self.output.append("SSH did not terminate. Killing process.")
            self.process.kill()

    @Slot()
    def send_ctrl_c(self):
        if self.process.state() == QProcess.NotRunning:
            self.output.append("Not connected.")
            return

        self.output.append("^C")
        self.process.write(b"\x03")

    @Slot()
    def run_test_script(self):
        self.run_remote_command("./start_mecanum.sh")

    def run_remote_command(self, command):
        if self.process.state() == QProcess.NotRunning:
            self.output.append("Not connected.")
            return

        self.output.append(f"> {command}")
        self.process.write((command + "\n").encode("utf-8"))

    @Slot()
    def send_input(self):
        text = self.input_line.text()
        self.input_line.clear()

        if self.process.state() == QProcess.NotRunning:
            self.output.append("Not connected.")
            return

        self.output.append(f"> {text}")
        self.process.write((text + "\n").encode("utf-8"))

    @Slot()
    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.output.moveCursor(QTextCursor.End)
        self.output.insertPlainText(data)
        self.output.moveCursor(QTextCursor.End)
        self.output_received.emit(data)

        self._stdout_buffer = (self._stdout_buffer + data)[-4096:]
        if "CanopenApp object created" in self._stdout_buffer:
            self._stdout_buffer = ""
            self.server_ready.emit()

    @Slot()
    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.output.moveCursor(QTextCursor.End)
        self.output.insertPlainText(data)
        self.output.moveCursor(QTextCursor.End)
        self.output_received.emit(data)

        self._stderr_buffer = (self._stderr_buffer + data)[-4096:]
        if "CanopenApp object created" in self._stderr_buffer:
            self._stderr_buffer = ""
            self.server_ready.emit()

    @Slot()
    def on_started(self):
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.run_test_script_button.setEnabled(True)
        self.ctrl_c_button.setEnabled(True)
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self.output.append("SSH process started.")

    @Slot(int, QProcess.ExitStatus)
    def on_finished(self, exit_code, exit_status):
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.run_test_script_button.setEnabled(False)
        self.ctrl_c_button.setEnabled(False)
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self.output.append(f"\nSSH process finished with exit code {exit_code}.")

    @Slot(QProcess.ProcessError)
    def on_error(self, error):
        QMessageBox.critical(self, "SSH Error", f"SSH process error: {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = SshConnectionWidget(
        host="localhost",
        user="bernd",
        port=22,
    )
    widget.show()

    sys.exit(app.exec())
