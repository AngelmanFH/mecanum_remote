from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QRadialGradient, QFont, QFontMetrics
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, Signal, Slot


class StopGoButton(QWidget):
    clicked = Signal()
    def __init__(self, radius=200):
        super().__init__()
        self.setFixedSize(radius * 2 + 2, radius * 2 + 2)
        self.circle_radius = radius
        self.circle_center = QPointF(self.width() / 2, self.height() / 2)
        self.square_margin = radius * 2 // 16
        self.square_size = radius * 2  - 2 * self.square_margin
        self.mousedown = False

        # defaults to stop-button
        self.colors_notclicked = [QColor(255, 50, 50), QColor(55, 0, 0)]
        self.colors_clicked = [QColor(255, 100, 100), QColor(125, 0, 0)]
        self.text = "STOP"

    def set_colors(self, notclicked: list, clicked: list):
        self.colors_notclicked = notclicked
        self.colors_clicked = clicked

    def set_text(self, text):
        self.text = text

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # update position and size
        self.circle_center = QPointF(self.width() / 2, self.height() / 2)
        self.circle_radius = (min(self.width(), self.height()) - 2) // 2
        # painter.drawRect(self.square_margin, self.square_margin, self.square_size, self.square_size)

        # Draw 3D red circle
        gradient = QRadialGradient(self.circle_center, self.circle_radius)
        if not self.mousedown:
            gradient.setColorAt(0, self.colors_notclicked[0])
            gradient.setColorAt(1, self.colors_notclicked[1])
        else:
            gradient.setColorAt(0, self.colors_clicked[0])
            gradient.setColorAt(1, self.colors_clicked[1])
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(self.circle_center, self.circle_radius, self.circle_radius)

        # Get the rectangle of the widget
        rect = self.rect()
        # Initial font size
        font_size = 1
        # Set font
        font = QFont("Arial",font_size, QFont.Bold)
        # text = "STOP"

        while True:
            font.setPointSize(font_size)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(self.text)
            text_height = fm.height()

            if text_width > self.circle_radius *4//3 or text_height > rect.height():
                break

            font_size += 1

        painter.setFont(font)
        painter.setPen(QPen(Qt.white, 1))



        # Draw centered text
        painter.drawText(rect, Qt.AlignCenter, self.text)

    def is_inside_circle(self, pos):
        distance = ((pos.x() - self.circle_center.x()) ** 2 + (pos.y() - self.circle_center.y()) ** 2) ** 0.5
        return distance <= self.circle_radius

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_inside_circle(event.position()):
            self.mousedown = True
            self.update()
            self.clicked.emit()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.is_inside_circle(event.position()):
            self.mousedown = False
            self.update()


class StopButton(StopGoButton):
    pass

class GoButton(StopGoButton):
    def __init__(self, radius=200):
        super().__init__(radius)
        # make a green GO-Button
        self.colors_notclicked = [QColor(50, 255, 50), QColor(0, 55, 0)]
        self.colors_clicked = [QColor(100, 255, 100), QColor(0, 125, 0)]
        self.text = "GO"

if __name__ == "__main__":

    @Slot()
    def clicked_slot():
        print("clicked!")

    app = QApplication([])
    widget = GoButton(100)
    widget.clicked.connect(clicked_slot)
    widget.show()
    app.exec()