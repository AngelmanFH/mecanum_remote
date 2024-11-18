from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QRadialGradient
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, Signal, Slot


class DraggableCircleWidget(QWidget):
    positionChanged = Signal(float, float)  # Define a custom signal

    def __init__(self, size=400):
        super().__init__()
        self.setFixedSize(size, size)
        self.circle_radius = size // 10
        self.circle_center = QPointF(self.width() / 2, self.height() / 2)
        self.dragging = False
        self.drag_offset = QPointF(0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_towards_center)
        self.square_margin = size // 50
        self.square_size = size - 2 * self.square_margin

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw white square with black border
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(Qt.black, 3))
        painter.drawRect(self.square_margin, self.square_margin, self.square_size, self.square_size)

        # Draw 3D red circle
        gradient = QRadialGradient(self.circle_center, self.circle_radius)
        gradient.setColorAt(0, QColor(255, 100, 100))
        gradient.setColorAt(1, QColor(150, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(self.circle_center, self.circle_radius, self.circle_radius)

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_inside_circle(event.position()):
            self.dragging = True
            self.drag_offset = event.position() - self.circle_center
            self.timer.stop()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            new_center = event.position() - self.drag_offset
            # Ensure the circle stays within the bounds of the square
            new_center.setX(max(self.square_margin + self.circle_radius,
                                min(new_center.x(), self.square_margin + self.square_size - self.circle_radius)))
            new_center.setY(max(self.square_margin + self.circle_radius,
                                min(new_center.y(), self.square_margin + self.square_size - self.circle_radius)))
            self.circle_center = new_center
            self.update()
            self.report_position()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        self.timer.start(50)  # Start the timer to update every 50 ms

    def is_inside_circle(self, pos):
        distance = ((pos.x() - self.circle_center.x()) ** 2 + (pos.y() - self.circle_center.y()) ** 2) ** 0.5
        return distance <= self.circle_radius

    def move_towards_center(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        direction = center - self.circle_center
        distance = (direction.x() ** 2 + direction.y() ** 2) ** 0.5

        if distance < 1:
            self.circle_center = center
            self.timer.stop()
            self.report_position()  # Ensure the final position is reported
        else:
            step = direction * 0.5  # Adjust the speed of the movement here
            self.circle_center += step
            self.update()
            self.report_position()

    def report_position(self):
        # Convert the position to the specified coordinate system
        x = self.height() / 2 - self.circle_center.y()
        y = self.width() / 2 - self.circle_center.x()
        self.positionChanged.emit(x, y)





if __name__ == "__main__":
    def position_callback(x, y):
        print(f"Circle position: x={x}, y={y}")

    app = QApplication([])
    widget = DraggableCircleWidget(size=300)
    widget.show()
    app.exec()
