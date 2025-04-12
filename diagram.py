from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor
from PyQt5.QtWidgets import QWidget, QApplication


class EllipseSectorRing:
    def __init__(self, rect, start_angle, span_angle, color):
        self.rect = rect
        self.start_angle = start_angle
        self.span_angle = span_angle
        self.color = color

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        pen = QPen(QColor(240, 240, 240, 255), 2, Qt.SolidLine)
        painter.setPen(pen)
        path = QPainterPath()
        path.moveTo(self.rect.center())
        path.arcTo(self.rect, self.start_angle, self.span_angle)
        path.closeSubpath()

        painter.drawPath(path)


class Diagram(QWidget):
    def __init__(self):
        super().__init__()
        self.track_num = 4
        self.lst = []
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        self.colorTag = ""

    def setParameters(self):
        try:
            self.rotation_angle = 0
            self.width = self.size().width()
            self.height = self.size().height()
            self.spaceing = int(self.height / 5)
            if self.width > 0:
                self.platter_width = int(self.width * 0.9)
                if self.platter_width > self.screen_width * 0.24:
                    self.platter_width = int(self.screen_width * 0.24)
            self.platter_height = int(self.height * 0.3)
            if self.platter_height > self.screen_height * 0.14:
                self.platter_height = int(self.screen_height * 0.14)
            else:
                self.rotation_angle = int(
                    45 - 45 * self.platter_height / (self.screen_height * 0.14)
                )
            self.track_width = int(self.platter_width / (self.track_num * 2) * 0.7)
            self.track_height = int(
                self.track_width * self.platter_height / self.platter_width
            )
        except Exception:
            pass

    def prepareEllipses(self):
        for i in range(128):
            if self.colorTag[i] == "ŀ":
                color = QColor(100, 100, 100, 255)
            elif self.colorTag[i] == "□":
                color = QColor(85, 85, 255, 255)
            else:
                color = QColor(237, 125, 49, 255)

            self.lst.append(
                EllipseSectorRing(
                    QRectF(
                        int(
                            self.width / 2
                            - self.platter_width / 2
                            + self.track_width * (i % 32 // 8) * (1 + i % 32 // 8 / 10)
                        ),
                        int(
                            self.track_height * (i % 32 // 8) * (1 + i % 32 // 8 / 10)
                            + self.spaceing * ((127 - i) // 32 + 1)
                            - self.platter_height / 2
                        ),
                        self.platter_width
                        - self.track_width * 2 * (i % 32 // 8) * (1 + i % 32 // 8 / 10),
                        self.platter_height
                        - self.track_height
                        * 2
                        * (i % 32 // 8)
                        * (1 + i % 32 // 8 / 10),
                    ),
                    -(45 * (i % 8) + 10 + self.rotation_angle),
                    -45,
                    color,
                )
            )

    def paintEvent(self, event):
        self.lst.clear()
        self.setParameters()
        self.prepareEllipses()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制所有椭圆形扇环
        for ring in self.lst:
            ring.draw(painter)
