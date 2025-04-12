from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMenu, QLineEdit


class RightClickMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint #| Qt.Popup
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.hovered.connect(self.on_hovered)
        self.triggered.connect(self.on_action_triggered)

        self.screen_width = QApplication.primaryScreen().size().width()
        self.last_selected_action = None
        self.left_top_radius = 0
        self.right_top_radius = 0
        self.left_bottom_radius = 0
        self.right_bottom_radius = 0
        self.width = int(self.screen_width * 0.06)
        self.outline_width = (
            self.screen_width // 1000 if self.screen_width // 1000 > 0 else 1
        )
        self.radius = self.outline_width * 6
        self.outline_color = "#9A9A9A"
        self.bg_color = "#EFEFEF"
        self.selected_color = "#90C8F6"
        self.setStyle()

    def on_hovered(self, action):
        actions = self.actions()

        self.left_top_radius = 0
        self.right_top_radius = 0
        self.left_bottom_radius = 0
        self.right_bottom_radius = 0

        if action == actions[0]:
            self.left_top_radius = self.radius - int(self.outline_width * 1.5)
            self.right_top_radius = self.radius - int(self.outline_width * 1.5)

        if action == actions[-1]:
            self.left_bottom_radius = self.radius - int(self.outline_width * 1.5)
            self.right_bottom_radius = self.radius - int(self.outline_width * 1.5)

        if action != self.last_selected_action:
            self.setStyle()
            self.last_selected_action = action

    def setStyle(self):
        self.setStyleSheet(f"""
                           RightClickMenu {{
                           background-color: {self.bg_color};
                           border-radius: {self.radius}px;
                           border: {self.outline_width}px solid {self.outline_color};
                           width: {self.width}px;
                           }}
                           RightClickMenu::item {{
                           padding: {self.outline_width * 2}px 0px;
                           width: {self.width - self.outline_width * 2}px;
                           }}
                           RightClickMenu::item:selected {{
                           padding: {self.outline_width * 2}px 0px;
                           width: {self.width - self.outline_width * 2}px;
                           background-color: {self.selected_color};
                           border-top-left-radius: {self.left_top_radius}px;
                           border-top-right-radius: {self.right_top_radius}px;
                           border-bottom-left-radius: {self.left_bottom_radius}px;
                           border-bottom-right-radius: {self.right_bottom_radius}px;
                           }}
                           """)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        QApplication.instance().installEventFilter(self)

    def hideEvent(self, event):
        super().hideEvent(event)
        QApplication.instance().removeEventFilter(self)

    def on_action_triggered(self, action):
        self.close()


class reNameLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen_width = QApplication.primaryScreen().size().width()
        self.outline_width = (
            self.screen_width // 1000 if self.screen_width // 1000 > 0 else 1
        )
        self.setStyleSheet(
            f"""QLineEdit {{border: {self.outline_width}px solid #0059BA; }}"""
        )
        self.textChanged.connect(self.adjustSize)

    def adjustSize(self):
        metrics = self.fontMetrics()
        text_width = metrics.boundingRect(self.text()).width() + self.size().height()
        self.setFixedWidth(text_width)
