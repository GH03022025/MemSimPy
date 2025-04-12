import sys
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal


class Editor(QPlainTextEdit):
    cmd_signal = pyqtSignal(str, str, list, list)

    def __init__(self):
        super().__init__()
        self.fcb_pos = []
        self.blocks = []
        self.initUI()

    def initUI(self):
        self.cmd_line_height = int(QApplication.primaryScreen().size().height() * 0.025)
        # 命令输入框
        self.cmd_line = QLineEdit(self)
        self.cmd_line.setPlaceholderText(">>>")
        self.cmd_line.hide()

        # 连接命令输入框的回车事件
        self.cmd_line.returnPressed.connect(self.handle_command)

        # 初始模式为NORMAL_MODE
        self.mode = "NORMAL_MODE"
        self.update_mode()

        # 设置QSS样式
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(12, 12, 12, 1);
                color: rgba(216, 216, 216, 1);
                font-size: 12pt;
                font-family: 'Cascadia Mono';
                border: none;
            }
            QLineEdit {
                background-color: rgba(40, 40, 40, 1);
                color: rgba(180, 180, 180, 1);
                font-size: 12pt;
                font-family: 'Cascadia Mono';
                border: none;
            }
        """)

    def update_mode(self):
        if self.mode == "NORMAL_MODE":
            self.setReadOnly(True)
            self.cmd_line.hide()
        elif self.mode == "INSERT_MODE":
            self.setReadOnly(False)
            self.cmd_line.hide()
        elif self.mode == "COMMAND_MODE":
            self.setReadOnly(True)
            self.cmd_line.show()

    def keyPressEvent(self, event):
        if self.mode == "NORMAL_MODE":
            if event.key() == Qt.Key_I:
                self.mode = "INSERT_MODE"
                self.update_mode()
                return
            elif event.key() == Qt.Key_Colon:
                self.cmd_line.show()
                self.cmd_line.setFocus()
            elif event.key() == Qt.Key_Escape:
                pass  # 已经在NORMAL_MODE，无需处理
        elif self.mode == "INSERT_MODE":
            if event.key() == Qt.Key_Escape:
                self.mode = "NORMAL_MODE"
                self.update_mode()
        elif self.mode == "COMMAND_MODE":
            if event.key() == Qt.Key_Escape:
                self.cmd_line.clear()
                self.cmd_line.hide()
                self.mode = "NORMAL_MODE"
                self.update_mode()
            elif event.key() == Qt.Key_Return:
                self.handle_command()
            else:
                self.cmd_line.setText(self.cmd_line.text() + event.text())
        super().keyPressEvent(event)

    def handle_command(self):
        # 获取输入的命令
        cmd = self.cmd_line.text()
        # 打印编辑器中的文本
        content = self.toPlainText().replace("\n", "↵")
        print("content:", content)

        if cmd == "w":
            self.cmd_signal.emit("w", content, self.fcb_pos, self.blocks)
        elif cmd == "q":
            self.clear()
            self.cmd_line.clear()
            self.cmd_signal.emit("q", "", [], [])
        elif cmd == "wq":
            self.clear()
            self.cmd_line.clear()
            self.cmd_signal.emit("wq", content, self.fcb_pos, self.blocks)

        # 清空命令输入框并隐藏
        self.cmd_line.clear()
        self.cmd_line.hide()
        # 返回普通模式
        self.mode = "NORMAL_MODE"
        self.update_mode()
        # 将焦点返回到文本编辑器
        self.setFocus()

    def resizeEvent(self, event):
        # 调整命令输入框的位置和大小
        self.cmd_line.setGeometry(
            0, self.height() - self.cmd_line_height, self.width(), self.cmd_line_height
        )
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(len("\n"))
    editor = Editor()
    editor.show()
    sys.exit(app.exec_())

