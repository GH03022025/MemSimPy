import sys

from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QAction,
    QLineEdit,
    QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from embedded_custom_widgets import RightClickMenu, reNameLineEdit


class Directory(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.icon_root = QIcon("icon/root.png")
        self.icon_folder = QIcon("icon/folder.png")
        self.icon_file = QIcon("icon/file.png")

        # 隐藏标题
        self.header().setVisible(False)

        # 添加节点，不该存在，仅测试玩玩
        self.root = QTreeWidgetItem(self, ["根目录"])
        self.root.setIcon(0, self.icon_root)
        self.root.setData(0, Qt.UserRole, "root")  # 标记根目录

        # 记录当前选择的节点和复制的节点
        self.current_copy_item = None
        self.current_item = None

        self.root.setExpanded(True)  # 展开根节点

        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self, position):
        self.current_item = self.itemAt(position)
        if not self.current_item:
            return
        self.menu = RightClickMenu()

        def add_makdir_action():  # 向右键菜单添加新建目录
            makdir_action = QAction(QIcon("icon/img.png"), "新建目录", self)
            makdir_action.triggered.connect(self.makdir)
            self.menu.addAction(makdir_action)

        def add_create_action():  # 向右键菜单添加新建文件
            makdir_action = QAction(QIcon("icon/img.png"), "新建文件", self)
            makdir_action.triggered.connect(self.create)  # 这里需要改
            self.menu.addAction(makdir_action)

        def add_copy_action():  # 向右键菜单添加复制
            copy_action = QAction(QIcon("icon/img.png"), "复制", self)
            copy_action.triggered.connect(self.copy_item)
            self.menu.addAction(copy_action)

        def add_paste_action():  # 向右键菜单添加粘贴
            paste_action = QAction(QIcon("icon/img.png"), "粘贴", self)
            paste_action.triggered.connect(self.paste_item)
            self.menu.addAction(paste_action)

        def add_delete_action():  # 向右键菜单添加删除
            delete_action = QAction(QIcon("icon/img.png"), "删除", self)
            delete_action.triggered.connect(self.delete_item)
            self.menu.addAction(delete_action)

        def add_rename_action():  # 向右键菜单添加重命名
            rename_action = QAction(QIcon("icon/img.png"), "重命名", self)
            rename_action.triggered.connect(self.rename_item)
            self.menu.addAction(rename_action)

        item_type = self.current_item.data(0, Qt.UserRole)  # 获取节点类型

        if item_type == "root":
            add_makdir_action()
            add_create_action()
        elif item_type == "dir":
            add_makdir_action()
            add_create_action()
            add_paste_action()
            add_delete_action()
            add_rename_action()
        elif item_type == "file":
            add_copy_action()
            add_delete_action()
            add_rename_action()

        self.menu.exec_(self.viewport().mapToGlobal(position))

    def makdir(self):
        item = QTreeWidgetItem(self.current_item, ["新建目录"])
        item.setIcon(0, self.icon_folder)
        item.setData(0, Qt.UserRole, "dir")  # 标记目录
        self.current_item.setExpanded(True)
        print("新建目录")

    def create(self):
        item = QTreeWidgetItem(self.current_item, ["新建文件"])
        item.setIcon(0, self.icon_file)
        item.setData(0, Qt.UserRole, "file")  # 标记文件
        self.current_item.setExpanded(True)
        print("新建文件")

    def copy_item(self):
        if self.current_item:
            self.current_copy_item = self.current_item.clone()
            print(f"复制项: {self.current_item.text(0)}")
        else:
            print("没有选中的项可复制")

    def paste_item(self):
        if self.current_copy_item and self.current_item:
            makdir = self.current_copy_item.clone()
            self.current_item.addChild(makdir)
            self.current_item.setExpanded(True)
            print(f"粘贴项: {makdir.text(0)}")
        else:
            print("没有可粘贴的项或目标项未选择")

    def delete_item(self):
        if self.current_item:
            parent_item = self.current_item.parent()
            if parent_item:
                parent_item.removeChild(self.current_item)
            else:
                index = self.indexOfTopLevelItem(self.current_item)
                if index != -1:
                    self.takeTopLevelItem(index)
            print(f"删除项: {self.current_item.text(0)}")
            self.current_item = None  # 清空当前选中的项

    def rename_item(self):
        if self.current_item:
            # 创建输入框
            line_edit = reNameLineEdit(self)
            line_edit.setText(self.current_item.text(0))
            rect = self.visualItemRect(self.current_item)
            line_edit.setGeometry(
                rect.topLeft().x() + line_edit.size().height(),
                rect.top(),
                line_edit.width(),
                line_edit.height(),
            )
            line_edit.show()
            line_edit.setFocus()  # 设置焦点
            line_edit.selectAll()  # 全选文本，模仿win系统
            old_name = self.current_item.text(0)
            line_edit.editingFinished.connect(
                lambda: self.apply_rename(line_edit, old_name)
            )
            self.current_item.setText(0, "")

    def apply_rename(self, line_edit, old_name):
        new_name = line_edit.text()
        if self.current_item and new_name:
            self.current_item.setText(0, new_name)
        else:
            self.current_item.setText(0, old_name)
        line_edit.close()  # 删除输入框

    def mousePressEvent(self, event):
        # 获取点击位置的item
        item = self.itemAt(event.pos())
        if not item:  # 如果点击位置不是任何item
            self.clearSelection()  # 取消选中
        super().mousePressEvent(event)


"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    tree = Directory()
    tree.show()
    sys.exit(app.exec_())
"""
