from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
                               QLabel, QLineEdit, QComboBox, QPushButton, QFrame, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QFontMetrics

def signed_int_decorator(func):
    def wrapper(value, base=10):
        num = func(value, base)
        if base == 16 and num >= 2**31:
            num -= 2**32
        return num
    return wrapper

@signed_int_decorator
def signed_int(value, base=10):
    return int(value, base)

class SdoReadWrite(QWidget):
    send_sdo_read_req = Signal(int, int, int, int)
    send_sdo_write_req = Signal(int, int, int, str, int)
    def __init__(self):
        super().__init__()
        self.lineedits = []
        self.names = ["MotNr", "Index", "SubIndex", "DataType", "Value"]
        self.placeholders = ["1..4", " E.g. '0x6041'", "E.g. '0x00'", "", "only when writing!"]
        self.d_types = ["u8", "i8", "u16", "i16", "u32", "i32"]

        # Create the main frame with a border
        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Box)
        main_frame.setLineWidth(1)
        # Create the main vertical layout
        main_layout = QVBoxLayout(main_frame)

        # Create the title label
        title_label = QLabel("SDO r/w")
        title_font = QFont()
        title_font.setPointSize(16)  # Set font size
        title_font.setBold(True)  # Set font to bold
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # Center-align the title

        # Add the title label to the main layout
        main_layout.addWidget(title_label)

        # Define a fixed width for the input fields
        input_field_width = 200

        # Create and add the QLineEdit widgets with labels
        for i in range(0, 5):
            # Create a horizontal layout for each label and line edit pair
            h_layout = QHBoxLayout()

            # Create the label
            label = QLabel(self.names[i])
            label.setAlignment(Qt.AlignRight)  # Right-align the label

            if i == 3:
                # Create a QComboBox for the 4th item
                widget = QComboBox()
                widget.addItems(self.d_types)
                self.typechoice = widget
            else:
                # Create a QLineEdit for other items
                widget = QTextEdit()
                widget.setPlaceholderText(self.placeholders[i])
                font_metrics = QFontMetrics(widget.font())
                single_line_height = font_metrics.lineSpacing()
                widget.setFixedHeight(single_line_height + 10)  # Adding some padding
                self.lineedits.append(widget)


            # Set the fixed width for the input fields
            widget.setFixedWidth(input_field_width)
            # widget.setMinimumWidth(input_field_width)

            # Add the label and widget to the horizontal layout
            h_layout.addWidget(label)
            h_layout.addWidget(widget)

            # Add the horizontal layout to the main vertical layout
            main_layout.addLayout(h_layout)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Create the Read and Write buttons
        read_button = QPushButton("Read")
        write_button = QPushButton("Write")

        # Connect the Read button to the sdo reading machine
        read_button.clicked.connect(self.read_sdo)

        # Connect the Write button to the sdo writing machine
        write_button.clicked.connect(self.write_sdo)

        # Add the buttons to the button layout
        button_layout.addWidget(read_button)
        button_layout.addWidget(write_button)

        # Add the button layout to the main vertical layout
        main_layout.addLayout(button_layout)

        # Set the main layout for the widget
        self.setLayout(QVBoxLayout())  # Set a new QVBoxLayout for the main widget
        self.layout().addWidget(main_frame)  # Add the main_frame to this layout

    @Slot(str)
    def update_read_data(self, valstring):
        self.lineedits[-1].setText(valstring)  # [-1] = the last one

    @Slot()
    def read_sdo(self):
        try:
            node, idx, subidx = self.read_address()
        except(TypeError): # when read_address() returns None because of erroneous input
            return
        dtypenum, dtype = self.read_datatype()
        reply = QMessageBox.question(self, "Proceed?", f"Read this data from CAN-bus?\nMotNr: {node}\nIndex: "
                                                       f"{idx}\nSubIndex: {subidx}\nType: {dtype} ({dtypenum})",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.send_sdo_read_req.emit(node, idx, subidx, dtypenum)

    @Slot()
    def write_sdo(self):
        try:
            node, idx, subidx = self.read_address()
        except(TypeError): # when read_address() returns None because of erroneous input
            return
        dtypenum, dtype = self.read_datatype()
        value = self.lineedits[-1].toPlainText()
        try:
            if value.startswith("0x"):
                # Convert the text to an integer assuming it's in hex format
                value = signed_int(value, 16)
            else:
                # Convert the text to an integer assuming it's in decimal format
                value = signed_int(value)
        except ValueError:
            # Show an error message if the text is not a valid hex number
            QMessageBox.critical(self, "Invalid Input", f"'{value}' in field '{self.names[-1]}' "
                                                        f"is not a valid number.")
            return

        reply = QMessageBox.question(self, "Proceed?",
                                      f"Write this data to CAN-bus?\nMotNr: {node}\nIndex: {idx}\n"
                                      f"SubIndex: {subidx}\nType: {dtype} ({dtypenum})"
                                      f"\nValue: {value}",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.send_sdo_write_req.emit(node, idx, subidx, dtype, value)
    def read_datatype(self):
        dtype = self.typechoice.currentIndex()
        dtypename = self.typechoice.currentText()
        return dtype, dtypename

    def read_address(self):
        addrdata = []
        for index, line_edit in enumerate(self.lineedits):
            text = line_edit.toPlainText()
            # omit the last one (value)
            if index == len(self.lineedits) - 1:
                break
            try:
                if text.startswith("0x"):
                    # Convert the text to an integer assuming it's in hex format
                    value = int(text, 16)
                else:
                    # Convert the text to an integer assuming it's in decimal format
                    value = int(text)
                addrdata.append(value)
                # print(f"value: {text} -> Integer: {value}\nLine Edit #: {index} ")
            except ValueError:
                # Show an error message if the text is not a valid hex number
                QMessageBox.critical(self, "Invalid Input", f"'{text}' in field '{self.names[index]}' "
                                                            f"is not a valid number.")
                return None
        return addrdata


if __name__ == "__main__":
    app = QApplication([])

    widget = SdoReadWrite()
    widget.show()

    app.exec()