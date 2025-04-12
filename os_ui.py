import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QSplitter, QWidget, QVBoxLayout
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt

from terminal import Terminal
from diagram import Diagram
from directory import Directory
from cmd_checker import CmdFormatChecker
from disk import Disk
from editor import Editor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HBU > OS Course Design > 20222605061")
        self.init_width = int(QApplication.primaryScreen().size().width() * 0.6)
        self.init_height = int(self.init_width * 0.65)
        self.resize(self.init_width, self.init_height)
        self.initUI()

    def initUI(self):
        self.h_splitter = QSplitter(self)
        self.left_v_splitter = QSplitter(self)
        self.left_top_area = QWidget(self)
        self.left_bottom_area = QWidget(self)
        self.right_area = QWidget(self)
        self.left_top_layout = QVBoxLayout(self.left_top_area)
        self.left_bottom_layout = QVBoxLayout(self.left_bottom_area)
        self.right_layout = QVBoxLayout(self.right_area)

        self.left_v_splitter.setOrientation(Qt.Vertical)

        self.left_top_area.setObjectName("left_top_area")
        self.left_top_area.setStyleSheet(
            "QWidget#left_top_area { background-color: #AA4444; }"
        )
        self.left_bottom_area.setObjectName("left_bottom_area")
        self.left_bottom_area.setStyleSheet(
            "QWidget#left_bottom_area { background-color: #44AA44; }"
        )
        self.right_area.setObjectName("right_area")
        self.right_area.setStyleSheet(
            "QWidget#right_area { background-color: #4444AA; }"
        )

        color = self.palette().color(QPalette.Window).name()
        self.h_splitter.setObjectName("h_splitter")
        self.h_splitter.setStyleSheet(
            f"""QSplitter#h_splitter::handle {{ background: {color}; }}"""
        )
        self.left_v_splitter.setObjectName("left_v_splitter")
        self.left_v_splitter.setStyleSheet(
            f"""QSplitter#left_v_splitter::handle {{ background: {color}; }}"""
        )

        self.setCentralWidget(self.h_splitter)
        self.h_splitter.addWidget(self.left_v_splitter)
        self.left_v_splitter.addWidget(self.left_top_area)
        self.left_v_splitter.addWidget(self.left_bottom_area)
        self.h_splitter.addWidget(self.right_area)

        self.h_splitter.setSizes([300, 200])  # 初始大小可以根据需要设定
        self.left_v_splitter.setSizes([200, 300])  # 初始大小可以根据需要设定

        self.dir_win = Directory()
        self.left_top_layout.addWidget(self.dir_win)

        self.cmd_win = Terminal()
        self.left_bottom_layout.addWidget(self.cmd_win)

        self.editor_win = Editor()
        self.editor_win.hide()
        self.left_bottom_layout.addWidget(self.editor_win)

        self.diag_win = Diagram()
        self.right_layout.addWidget(self.diag_win)

        self.cmd_checker = CmdFormatChecker()
        self.disk = Disk()

        # 初始化椭圆色盘
        colorTag = "".join(self.disk.content[:2])
        colorTag = colorTag.replace("\n", "")
        self.diag_win.colorTag = self.transform(colorTag)

        self.cmd_win.submit.connect(self.getCmd)
        self.editor_win.cmd_signal.connect(self.editorFeedback)

    def editorFeedback(self, cmd, content, fcb_pos, blocks):
        print("content_2:", content)
        if cmd == "q":
            self.editor_win.hide()
            self.cmd_win.show()
            self.cmd_win.setFocus()
        elif cmd == "w":
            self.disk.edit(fcb_pos, blocks, content)
        elif cmd == "wq":
            self.disk.edit(fcb_pos, blocks, content)
            self.editor_win.hide()
            self.cmd_win.show()
            self.cmd_win.setFocus()

        # 通知椭圆视图更新
        colorTag = "".join(self.disk.content[:2])
        colorTag = colorTag.replace("\n", "")
        self.diag_win.colorTag = self.transform(colorTag)
        self.diag_win.update()

    def getCmd(self, cmd: str):
        status, cmd_prompt, info = self.cmd_checker.check(cmd)
        # print(status, cmd_prompt, info)
        # cmd_checker只负责细致检查命令格式，不检查命令是否能执行成功
        # status: bool, True表示命令格式正确，False表示命令格式错误
        # cmd_prompt: str, 命令提示符
        # info: lst, 内容，命令格式正确时为路径等必要信息，命令格式错误时则为报错信息

        print(status, cmd_prompt, info)

        if status:
            if cmd_prompt == "edit":
                fcb_pos, blocks = self.disk.blockInfo("reg", info)
                if blocks[0] is not False:
                    self.editor_win.fcb_pos = fcb_pos
                    self.editor_win.blocks = blocks
                    self.editor_win.show()
                    self.editor_win.setFocus()
                    self.cmd_win.hide()
                    self.editor_win.insertPlainText(self.disk.getContent(blocks).replace("□", ""))
            else:
                result = self.disk.operate(cmd_prompt, info)
                if result:
                    self.respondCmd(result)

    def respondCmd(self, result):
        cmd_prompt = result[0]
        status = result[1]
        print(result)
        info = result[2]
        if status:
            # 判断操作后是否影响了当前工作目录，影响的话重置回根目录
            work_path_exists = self.disk.cd(self.disk.current_dir)[1]
            if not work_path_exists:
                self.cmd_win.title = "Disk:/> "
                self.disk.current_dir = [""]

            # 通知椭圆视图更新
            colorTag = "".join(self.disk.content[:2])
            colorTag = colorTag.replace("\n", "")
            self.diag_win.colorTag = self.transform(colorTag)
            self.diag_win.update()

            method = getattr(self, cmd_prompt + "_cmd", None)
            if method:
                method(info)

    def cd_cmd(self, path):
        if path:
            self.cmd_win.title = "Disk:" + "/".join(path) + "> " if path != [""] else "Disk:/> "

    def closeEvent(self, event):
        print("再见")
        with open("disk.txt", "w", encoding="utf-8") as f:
            for i in self.disk.content:
                f.write(i)
        print("磁盘写入")

        event.accept()

    def transform(self, colorTag):
        new_colorTag = ""
        tag1 = colorTag[0:32]
        tag2 = colorTag[32:64]
        tag3 = colorTag[64:96]
        tag4 = colorTag[96:128]
        for i in range(4):
            new_colorTag += tag1[i * 8 : (i + 1) * 8]
            new_colorTag += tag2[i * 8 : (i + 1) * 8]
            new_colorTag += tag3[i * 8 : (i + 1) * 8]
            new_colorTag += tag4[i * 8 : (i + 1) * 8]
        return new_colorTag


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
