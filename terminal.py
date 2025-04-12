# import sys
import webbrowser

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor  # QDesktopServices
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit  # QApplication


class Terminal(QPlainTextEdit):
    submit = pyqtSignal(str)  # 信号，用于通知主窗口命令输入完成

    def __init__(self):
        super().__init__()
        self.setWindowTitle("模拟终端")
        self.insertPlainText("Disk:/> ")
        self.font_size = 12  # 字号
        self.text_background_color = "#868686"  # 滑选内容底色

        self.cmd_history = []  # 输入历史
        self.temp_cmd = None  # 当前未键入命令
        self.cmd_history_index = 0  # 输入历史记录索引

        self.is_selecting = False  # 滑选状态标记
        self.cursor_pos_record = None  # 鼠标左键单击位置

        self.select_start_pos = None  # 滑选起始位置
        self.select_end_pos = None  # 滑选结束位置
        self.current_pos = None  # 光标当前位置
        self.extra_selections = self.extraSelections()  # 滑选内容列表
        self.textFormat = QTextCharFormat()  # 文本格式

        self.selection_text = None  # 滑选内容
        self.clipboard = None  # 剪贴板

        self.title = "Disk:/> "  # 标题显示，实际用于显示当前路径

        self.setStyle()

    def setStyle(self):
        self.setStyleSheet(f"""
            Terminal {{
                background-color: rgba(12, 12, 12, 1);
                color: rgba(216, 216, 216, 1);
                font-family: 'Cascadia Mono';
                font-size: {self.font_size}pt;
                border: none;
            }}
        """)
        self.textFormat.setBackground(QColor(self.text_background_color))

    def cursorPosCheck(self, cursor):
        pos_in_block = cursor.positionInBlock()
        current_block = cursor.block()
        next_block = current_block.next()

        if not next_block.isValid():
            return True, pos_in_block
        else:
            return False, pos_in_block

    def restoreHistoryCmd(self, step):
        if (
            step == -1 and self.cmd_history_index == 0
        ):  # 如果是方向键上，且历史命令索引为0，则暂存当前命令
            self.temp_cmd = (
                self.textCursor().block().text()[len(self.title) :]
            )  # 暂存未键入命令

        if self.cmd_history_index is not None:
            if (self.cmd_history_index + step) in range(-len(self.cmd_history), 1):
                self.cmd_history_index += step
                cursor = self.textCursor()
                cursor.movePosition(cursor.StartOfBlock)
                cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
                cursor.removeSelectedText()  # 删除当前块所有内容
                self.insertPlainText(f"{self.title}")  # 重新添加路径显示

                if self.cmd_history_index == 0:
                    self.insertPlainText(f"{self.temp_cmd}")
                else:
                    self.insertPlainText(f"{self.cmd_history[self.cmd_history_index]}")

    def openUrl(self, event):
        cursor = self.cursorForPosition(event.pos())
        pos = cursor.positionInBlock()
        text = cursor.block().text()

        if text[:3] == "(▷)" and pos < len(text):
            webbrowser.open(
                "https://bbs.mihoyo.com/bh3/wiki/content/2298/detail?bbs_presentation_style=no_header"
            )

    def internalCmd(self, text):
        if text == "clear":
            self.clear()  # 清空终端
            self.cmd_history = []  # 清空历史命令
            self.temp_cmd = None  # 清空暂存命令
            return

        if text == "Da Capo":
            self.clear()  # 清空终端
            self.insertPlainText("(▷) Da Capo: ♪\n")
            return

        cmd = text.split(" ")

        if cmd[0] == "setSelectionColor":
            if len(cmd) < 2 or cmd[1][0] != "#" or len(cmd[1]) != 7:
                return
            color = [_ for _ in cmd[1][1:] if _ in "0123456789ABCDEF"]
            if len(color) != 6:
                return
            old_text_background_color = self.text_background_color
            self.text_background_color = "#" + "".join(color)
            self.setStyle()
            self.insertPlainText(
                f"\n选中背景色变更：{old_text_background_color} -> {self.text_background_color}\n"
            )

        if cmd[0] == "setTitle":
            if len(cmd) < 2:
                return
            self.title = " ".join(cmd[1:])

        self.insertPlainText("\n")

    def process(self):
        text = self.textCursor().block().text()[len(self.title) :]
        self.internalCmd(text)  # 处理内部命令
        self.submit.emit(text)  # 提交命令到主窗口
        self.insertPlainText(f"{self.title}")  # 不换行，仅插入title

    def keyPressEvent(self, event):
        last_block, cursor_pos_in_block = self.cursorPosCheck(self.textCursor())

        if self.textCursor().hasSelection() and event.key() == Qt.Key_Backspace:
            return  # 禁止滑选删除

        if event.modifiers() & Qt.ControlModifier:  # 复制 ctrl+c
            if event.key() == Qt.Key_C:
                print("copy")
                self.clipboard = self.selection_text.replace("\n", "")
            elif event.key() == Qt.Key_V:  # 粘贴 ctrl+v
                print("paste")
                if self.clipboard is not None:
                    self.insertPlainText(self.clipboard)
            elif event.key() == Qt.Key_Up:  # 调大文字 ctrl+↑
                if self.font_size < 64:
                    self.font_size += 1
                    self.setStyle()
            elif event.key() == Qt.Key_Down:  # 调小文字 ctrl+↓
                if self.font_size > 1:
                    self.font_size -= 1
                    self.setStyle()
            return

        if event.key() == Qt.Key_Up:  # ↑方向键恢复历史命令
            self.restoreHistoryCmd(-1)
            return

        if event.key() == Qt.Key_Down:  # ↓方向键恢复历史命令
            self.restoreHistoryCmd(1)
            return

        if (
            not last_block or cursor_pos_in_block < len(self.title) + 1
        ):  # 按需求屏蔽退格键和左方向键
            if (
                event.key() in [Qt.Key_Backspace, Qt.Key_Left]
            ) or cursor_pos_in_block < len(self.title):
                return

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # 响应回车键
            self.rmTextBackground()  # 清除滑选内容底色
            self.moveCursor(QTextCursor.EndOfLine)  # 移动光标到行尾
            cmd = self.textCursor().block().text()[len(self.title) :]  # 获取键入命令
            if cmd in self.cmd_history:  # 如果该命令先前使用过，则将其移动到列表最后
                self.cmd_history.remove(cmd)
            if cmd != "":
                self.cmd_history.append(
                    cmd
                )  # 如果该命令先前没有使用过，则将其添加到列表最后
            self.process()  # 模拟处理输入的内容
            return

        self.cmd_history_index = 0  # 重置历史索引
        self.rmTextBackground()  # 清除滑选内容底色

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.openUrl(event)  # 打开超链接
        self.rmTextBackground()  # 清除文字底色
        if event.button() == Qt.LeftButton:
            cursor1 = self.cursorForPosition(event.pos())
            self.select_start_pos = cursor1.position()

            last_block, cursor_pos_in_block = self.cursorPosCheck(
                self.cursorForPosition(event.pos())
            )
            if not last_block or cursor_pos_in_block < len(self.title):
                return  # 如果 不是最后一行 或 点击位置在title所在列，则不改变光标位置
            else:
                self.cursor_pos_record = event.pos()
                return
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor1 = self.cursorForPosition(event.pos())
            self.select_end_pos = cursor1.position()
            if self.select_start_pos is not None:
                full_text = self.toPlainText()
                self.selection_text = full_text[
                    min(self.select_start_pos, self.select_end_pos) : max(
                        self.select_start_pos, self.select_end_pos
                    )
                ]
            if not self.is_selecting and self.cursor_pos_record is not None:
                cursor2 = self.cursorForPosition(self.cursor_pos_record)
                self.setTextCursor(cursor2)
                self.cursor_pos_record = None
            self.is_selecting = False
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.is_selecting = True
        cursor1 = self.cursorForPosition(event.pos())
        self.current_pos = cursor1.position()
        self.setTextBackground(self.select_start_pos, self.current_pos)

    def mouseDoubleClickEvent(self, event):
        self.rmTextBackground()  # 清除文字底色
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
        else:
            super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        event.accept()  # 禁用右键菜单

    def setTextBackground(self, start, end):
        if type(start) is not int or type(end) is not int:
            return
        if start > end:
            start, end = end, start
        # 设置额外的选择区域
        self.extra_selections.clear()
        selection = QTextEdit.ExtraSelection()
        selection.format = self.textFormat
        # 选择要着色的文本范围
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(
            QTextCursor.NextCharacter, QTextCursor.KeepAnchor, end - start
        )
        selection.cursor = cursor
        # 将额外的选择区域添加到列表中
        self.extra_selections.append(selection)
        self.setExtraSelections(self.extra_selections)

    def rmTextBackground(self):
        self.extra_selections.clear()
        self.setExtraSelections(self.extra_selections)


"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Terminal()
    self.show()
    sys.exit(app.exec_())
"""