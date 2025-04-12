# 192表示0，319表示127
# 320(ŀ)表示系统占用，321(Ł)表示end，其它特殊符号顺次后延
# NNNTTRSL N:目录名，T：拓展名，R：读写属性，S：起始盘块号，L：文件长度（目录没有长度）
# print(chr(192))
"""
a = "0"
b = a if len(a) >= 3 else a + "□"* (3 - len(a))
print(b)
"""


class Disk:
    def __init__(self):
        self.clipboard = [None, []]
        f = open("./disk.txt", encoding="utf8")  # 打开磁盘文件
        self.content = f.readlines()  # 读取文件内容
        f.close()  # 关闭文件
        self.current_dir = [""]  # 当前目录，初始化为根目录

        for i in range(20):
            print(self.content[i].replace("\n", ""))

    def operate(self, operation, info):  # 外部调用，用以接收命令并调用函数
        method = getattr(self, operation, None)
        if method:
            print(info)
            result = method(info)
            """
            check = self.blockInfo("dir", self.current_dir)
            if check[1][0] == False:
                self.cd(["", ""])  # 切换回根目录
            """
            return result

    """
    +------------------------------+
    |         功能细分函数          |
    +------------------------------+
    """

    def absolutePath(self, info):  # 接收绝对路径或相对路径，返回绝对路径
        path = list(self.current_dir)
        info = info[:-1] if info[-1] == "" and len(info) != 1 else info
        for i in info:
            if i == ".":
                continue
            elif i == "..":
                path = path[:-1]
                # print(len(path))
                if len(path) == 0:
                    path.append("")
            elif i == "":
                path.clear()
                path.append(i)
            else:
                path.append(i)
        return path

    def blockInfo(self, file_type, path):  # 查找特定文件的FCB位置以及自身占用的空间块号
        path = self.absolutePath(path)  # path: ["", dir1, dir2, ... ,target]
        fcb_pos = [None, None]
        b_p = 2  # b_p: block_pointer 指向当前所在的块号
        f_n_p = 1  # f_n_p: file_name_pointer 指向当前所在的path中的文件名，作为path列表的索引
        num_lst = []

        if path == [""]:
            num_lst = [2]
            return [fcb_pos, num_lst]

        while True:
            for i in range(8):
                # 信息准备阶段
                if f_n_p != len(path) - 1:  # 中间文件名按照目录文件的名称处理方式处理
                    file_name = path[f_n_p]
                    extension_name = ""
                else:  # 最后一个文件按照存入标识符处理
                    if file_type == "reg":
                        if "." in path[f_n_p]:  # 有后缀名的文件名
                            file_name = ".".join(path[f_n_p].split(".")[:-1])
                            extension_name = path[f_n_p].split(".")[-1]
                        else:  # 无有后缀名的文件名
                            file_name = path[f_n_p]
                            extension_name = ""
                    elif file_type == "dir":
                        file_name = path[f_n_p]
                        extension_name = ""

                # 文件名长度补齐
                file_name = (
                    file_name
                    if len(file_name) >= 3
                    else file_name + "□" * (3 - len(file_name))
                )

                # 拓展名长度补齐
                extension_name = (
                    extension_name
                    if len(extension_name) >= 2
                    else extension_name + "□" * (2 - len(extension_name))
                )

                # 组装标准长度文件句柄
                full_name = file_name + extension_name

                print(f"准备匹配句柄：{full_name}")
                print(f"块号指针：{b_p} == {chr(b_p +192)}")
                print(f"块内偏移：{i * 8}")
                print(f"匹配对象：{self.content[b_p][i * 8 : 5 + i * 8]}")

                type_confirm = (
                    (f_n_p != len(path) - 1 and self.content[b_p][7 + i * 8] == "0")
                    or (
                        f_n_p == len(path) - 1
                        and self.content[b_p][7 + i * 8] == "0"
                        and file_type == "dir"
                    )
                    or (
                        f_n_p == len(path) - 1
                        and self.content[b_p][7 + i * 8] == "1"
                        and file_type == "reg"
                    )
                )
                # type_confirm确认当前查找的文件类型，辅助后续文件名匹配
                # 如果文件指针指向路径中间文件，直接按照目录文件处理
                # 如果文件指针指向最后一个文件，按照传入类型处理
                # self.content[b_p][7 + i * 8] 是文件长度，目录为0，普通文件为1
                # type_confirm =（中间 & 0）或（最后 & 0 & dir）或（最后 & 1 & reg）

                # 准备开始匹配文件句柄
                if (
                    full_name == self.content[b_p][i * 8 : 5 + i * 8] and type_confirm
                ):  # 匹配文件名，匹配成功
                    print("匹配成功")
                    if f_n_p == len(path) - 1:  # 是最终文件
                        fcb_pos[0] = b_p
                        fcb_pos[1] = i * 8
                        b_p = (
                            ord(self.content[b_p][6 + i * 8]) - 192
                        )  # 获取自身首块号, 开始在前两行查找块号
                        while True:
                            num_lst.append(b_p)
                            if self.content[b_p // 64][b_p % 64] == "Ł":
                                break
                            else:
                                b_p = ord(self.content[b_p // 64][b_p % 64]) - 192
                        return [fcb_pos, num_lst]

                    else:  # 非最终文件
                        f_n_p += 1
                        # 获取自身首块号, 下一轮进入自己的块空间
                        b_p = ord(self.content[b_p][6 + i * 8]) - 192
                        break
                elif i == 7:  # 匹配文件名，匹配失败
                    b_p = self.content[b_p // 64][b_p % 64]
                    if (
                        b_p == "Ł" or b_p == "ŀ"
                    ):  # :  # “Ł”表示end，"ŀ"表示根目录，即为不存在后续块
                        return [fcb_pos, [False, full_name]]
                    else:  # 有后续块
                        b_p = ord(b_p) - 192
                        break

    def blcokAvailable(self, number):  #  查找空闲块，number为需要的块数
        empty_blocks = []
        for i in range(128):
            if len(empty_blocks) >= number:
                return empty_blocks
            if self.content[i // 64][i % 64] == "□":
                empty_blocks.append(i)
        return empty_blocks

    def preAddFile(self, parent_blocks):  # 根据父级目录块号规划文件本身的位置
        self_pos = None
        fcb_pos = [None, None]  # fcb_pos[0]: FCB所在块号，fcb_pos[1]: FCB在块内偏移
        empty_blocks = self.blcokAvailable(2)  # 防止父级目录空间不足，直接申请两个块
        for i in range(len(parent_blocks)):
            if "□□□□□□□□" in self.content[parent_blocks[i]]:  # 父级目录有空间存放FCB
                for j in range(8):
                    if self.content[parent_blocks[i]][j * 8 : j * 8 + 8] == "□□□□□□□□":
                        fcb_pos[0] = parent_blocks[i]
                        fcb_pos[1] = j * 8
                        self_pos = empty_blocks[0]
                        return [self_pos, fcb_pos]
            else:  # 父级目录无空间存放FCB
                if i == len(parent_blocks) - 1:  # 是最后一个块
                    if parent_blocks[i] == 2:  # 父级目录为根目录，根目录不可拓展
                        return [None, [None, None]]

                    if len(empty_blocks) < 2:  # 空块不足
                        return [None, [None, None]]
                    # 空块足够
                    self.setBlockTag(empty_blocks[0], "Ł")  # 占用第一个申请的空块
                    # 将申请的第一个空白块号写入父级目录先前的最后的块
                    self.setBlockTag(parent_blocks[i], chr(empty_blocks[0] + 192))
                    fcb_pos[0] = empty_blocks[0]
                    fcb_pos[1] = 0
                    self_pos = empty_blocks[1]  # 申请的第二个空白块号留给文件
                    return [self_pos, fcb_pos]

    def addFile(self, file_type, whole_file_name, fcb_pos, self_pos):
        # print("disk-addFile-whole_file_name", whole_file_name)
        if file_type == "reg":  # 判断类型
            file_length = "1"  # 普通文件
            if "." in whole_file_name:
                file_name = ".".join(whole_file_name.split(".")[:-1])
                extension_name = whole_file_name.split(".")[-1]
            else:
                file_name = whole_file_name
                extension_name = ""
        elif file_type == "dir":
            file_length = "0"  # 目录文件
            file_name = whole_file_name
            extension_name = ""
        fcb = (
            (
                file_name
                if len(file_name) >= 3
                else file_name + "□" * (3 - len(file_name))
            )
            + (
                extension_name
                if len(extension_name) >= 2
                else extension_name + "□" * (2 - len(extension_name))
            )
            + "W"
            + chr(self_pos + 192)
            + file_length
        )
        # 添加FCB
        self.content[fcb_pos[0]] = (
            self.content[fcb_pos[0]][: fcb_pos[1]]
            + fcb
            + self.content[fcb_pos[0]][fcb_pos[1] + 8 :]
        )
        # 设置块状态标识符为"Ł"，表示占用
        self.setBlockTag(self_pos, "Ł")

    def setBlockTag(self, self_pos, tag):  # 更改块占用标识符
        block_num = self_pos // 64
        block_pos = self_pos % 64
        self.content[block_num] = (
            self.content[block_num][:block_pos]
            + tag
            + self.content[block_num][block_pos + len(tag) :]
        )

    def createObject(self, file_type, info):
        empty_blocks = self.blcokAvailable(1)  # 检查是否有空闲块
        if len(empty_blocks) < 1:
            return "磁盘空间不足"
        whole_path = self.absolutePath(info)
        file_location = whole_path[:-1]
        whole_file_name = whole_path[-1]
        parent_fcb_pos, parent_blocks = self.blockInfo("dir", file_location)

        print(f"父级目录FCB位置：{parent_fcb_pos}")

        if parent_blocks[0] is False:
            print(f"{parent_blocks[1]} 不存在")
            return "父级目录不存在"

        print(f"路径：{file_location}，占用块：{parent_blocks}")

        self_pos, fcb_pos = self.preAddFile(parent_blocks)
        print(self_pos, fcb_pos[0], fcb_pos[1])

        if None not in [self_pos, fcb_pos[0], fcb_pos[1]]:
            self.addFile(file_type, whole_file_name, fcb_pos, self_pos)

        for i in range(20):
            print(self.content[i].replace("\n", ""))

        return [self_pos, fcb_pos]

    def deleteObject(self, file_type, info):
        def deleteRecursively(file_type, fcb_pos, blocks):
            if file_type == "reg":
                print("进入普通文件删除流程")
                # 移除FCB
                self.content[fcb_pos[0]] = (
                    self.content[fcb_pos[0]][: fcb_pos[1]]
                    + "□□□□□□□□"
                    + self.content[fcb_pos[0]][fcb_pos[1] + 8 :]
                )
                # 更改块标记，释放块空间
                for i in blocks:
                    self.setBlockTag(i, "□")
                    self.content[i] = "□" * 64 + "\n"
                return

            elif file_type == "dir":
                # 检查是否为空
                blocks_str = ""
                for i in blocks:
                    blocks_str += self.content[i]
                blocks_str = blocks_str.replace("\n", "")  # 去除空白块
                if all(char == "□" for char in blocks_str):  # 为真则确认为空目录
                    print("验证为空目录")
                    # 移除FCB
                    self.content[fcb_pos[0]] = (
                        self.content[fcb_pos[0]][: fcb_pos[1]]
                        + "□□□□□□□□"
                        + self.content[fcb_pos[0]][fcb_pos[1] + 8 :]
                    )
                    # 更改块标记，释放块空间
                    for i in range(len(blocks)):
                        self.setBlockTag(blocks[i], "□")
                        self.content[blocks[i]] = "□" * 64 + "\n"
                    return

                print(f"{self.content[fcb_pos[0]][fcb_pos[1]:fcb_pos[1]+8]}不为空")

                for i in blocks:
                    for j in range(8):
                        if self.content[i][j * 8 : j * 8 + 8] == "□□□□□□□□":
                            continue

                        # 获取文件信息
                        child_blocks = []  # 存放文件块号
                        b_p = (
                            ord(self.content[i][j * 8 + 6]) - 192
                        )  # 获取文件首块号，作为块号指针
                        child_type = (
                            "dir" if self.content[i][j * 8 + 7] == "0" else "reg"
                        )  # 根据文件长度判断文件类型
                        while True:
                            child_blocks.append(b_p)
                            print(f"i: {i}, j: {j}")
                            print(f"递归b_p：{b_p} {type(b_p)}")
                            print(chr(b_p + 192))
                            print(
                                f"递归child_blocks：{child_blocks} {type(child_blocks)}"
                            )
                            print(f"递归child_type：{child_type} {type(child_type)}")
                            print(self.content[b_p // 64][b_p % 64])

                            if self.content[b_p // 64][b_p % 64] == "Ł":
                                break
                            else:
                                b_p = ord(self.content[b_p // 64][b_p % 64]) - 192

                        deleteRecursively(child_type, [i, j * 8], child_blocks)
            # 再次检查是否为空
            blocks_str = ""
            for i in blocks:
                blocks_str += self.content[i]
            blocks_str = blocks_str.replace("\n", "")  # 去除空白块
            if all(char == "□" for char in blocks_str):  # 为真则确认为空目录
                print("后续验证为空目录")
                # 移除FCB
                self.content[fcb_pos[0]] = (
                    self.content[fcb_pos[0]][: fcb_pos[1]]
                    + "□□□□□□□□"
                    + self.content[fcb_pos[0]][fcb_pos[1] + 8 :]
                )
                # 更改块标记，释放块空间
                for i in range(len(blocks)):
                    self.setBlockTag(blocks[i], "□")
                    self.content[blocks[i]] = "□" * 64 + "\n"
                return

        file_location = self.absolutePath(info)
        fcb_pos, blocks = self.blockInfo(file_type, file_location)
        print(fcb_pos)

        if blocks[0] is False:
            print(f"{blocks[1]} 不存在")
            return f"{blocks[1]} 不存在"

        if fcb_pos == [None, None]:
            print("根目录不可删除")
            return "根目录不可删除"

        deleteRecursively(file_type, fcb_pos, blocks)

        for i in range(20):
            print(self.content[i].replace("\n", ""))

        return "删除成功"

    def getContent(self, blocks):
        content = ""
        for i in blocks:
            content += self.content[i][:-1].replace("↵", "\n")
        return content

    """
    +------------------------------+
    |         磁盘指令函数          |
    +------------------------------+
    """

    def cd(self, info):  # 切换当前工作目录
        test_path = self.absolutePath(info)
        fcb_pos, blocks = self.blockInfo("dir", test_path)

        if blocks[0] is False:
            return [None, False, None]
        print(test_path)
        self.current_dir = test_path

        return ["cd", True, self.current_dir]

    def create(self, info):
        duplicate = self.blockInfo("reg", info)[1][0]
        if duplicate is not False:
            print("文件重名")
            return ["create", False, "文件已存在"]

        msg = self.createObject("reg", info)
        print(msg)
        return ["create", True, "文件创建成功"]

    def delete(self, info):
        msg = self.deleteObject("reg", info)
        return msg

    def makdir(self, info):
        duplicate = self.blockInfo("dir", info)[1][0]
        if duplicate is not False:
            print("目录重名")
            return ["makdir", False, "目录已存在"]

        msg = self.createObject("dir", info)
        print(msg)
        return ["makfir", True, "目录创建成功"]

    def deldir(self, info):
        msg = self.deleteObject("dir", info)
        print(msg)
        return msg

    def copy(self, info):
        fcb_pos, blocks = self.blockInfo("reg", info)
        if None in fcb_pos:
            return ["copy", False, "文件不存在"]
        self.clipboard = [None, []]  # 剪切板初始化
        self.clipboard[0] = self.content[fcb_pos[0]][fcb_pos[1] : fcb_pos[1] + 8]
        for i in blocks:
            self.clipboard[1].append(self.content[i])
        return ["copy", True, "复制成功"]

    def paste(self, info):
        # 先检查剪切板是否为空
        if self.clipboard[0] is None:
            return ["paste", False, "剪切板为空"]
        # 检查是否有重名文件
        self_path = self.absolutePath(info)
        print("self_path", self_path)

        duplicate = self.blockInfo("reg", self_path)[1][0]
        if duplicate is not False:
            print("文件重名")
            return ["paste", False, "文件已存在"]
        result = self.createObject("reg", self_path)  # 尝试创建临时文件
        if type(result) is str:  # 创建失败
            return ["paste", False, result]
        empties = self.blcokAvailable(len(self.clipboard[1]) - 1)  # 尝试更多块
        if len(empties) < len(self.clipboard[1]) - 1:  # 空间不足
            self.deletObject("reg", self_path)  # 删除临时文件
            return ["paste", False, "磁盘空间不足"]
        # 开始粘贴
        for i in range(len(empties)):
            n = empties[i]
            if i != len(empties) - 1:
                self.content[n // 64] = (
                    self.content[n // 64][: n % 64]
                    + chr(n + 192)
                    + self.content[n // 64][n % 64 + 1 :]
                )
            else:
                self.content[n // 64] = (
                    self.content[n // 64][: n % 64]
                    + "Ł"
                    + self.content[n // 64][n % 64 + 1 :]
                )

        print("result", result)
        print("empties", empties)
        print("self.content[result[0]]", self.content[result[0]])
        print("self.clipboard", self.clipboard)

        self_blocks = [result[0]]
        self_blocks.extend(empties)
        print("result[0]", result[0])
        print("self_blocks", self_blocks)
        for i in range(0, len(self.clipboard[1])):
            if i != len(self.clipboard[1]) - 1:
                self.setBlockTag(self_blocks[i], chr(self_blocks[i + 1] + 192))
            else:
                self.setBlockTag(self_blocks[i], "Ł")

            self.content[self_blocks[i]] = self.clipboard[1][i]

        for i in range(20):
            print(self.content[i].replace("\n", ""))

        return ["paste", True, "粘贴成功"]

    def move(self, info):
        print(info)
        self.copy(info[0])
        result = self.paste(info[1])
        if result[1]:
            self.delete(info[0])
        return ["move", True, "无论成功与否都会返回True，就是玩"]

    def edit(self, fcb_pos, blocks, content):
        print("content_3:", content)
        print("blocks:", blocks)
        length = (
            len(content) // 64 if len(content) % 64 == 0 else len(content) // 64 + 1
        )
        length = 1 if length == 0 else length
        print("length:", length)

        if length > len(blocks):
            empties = self.blcokAvailable(length - len(blocks))
            if len(empties) < length - len(blocks):
                return ["edit", False, "磁盘空间不足"]
            blocks.extend(empties)
            for i in range(len(blocks)):
                if i != len(blocks) - 1:
                    self.setBlockTag(blocks[i], chr(blocks[i + 1] + 192))
                else:
                    self.setBlockTag(blocks[i], "Ł")

        elif length < len(blocks):
            blocks_rm = blocks[-(len(blocks) - length) :]
            for i in blocks_rm:
                self.setBlockTag(i, "□")
                self.content[i] = "□" * 64 + "\n"
            blocks = blocks[: -len(blocks_rm)]
            try:
                self.setBlockTag(blocks[-1], "Ł")
            except Exception:
                pass
        else:
            pass

        for i in range(len(blocks)):
            text = content[i * 64 : (i + 1) * 64]
            text = text + (64 - len(text)) * "□" + "\n"
            print("text:", text)
            print("self.content[blocks[i]]:", self.content[blocks[i]])
            self.content[blocks[i]] = text

        for i in range(20):
            print(self.content[i].replace("\n", ""))

        return ["edit", True, "编辑成功"]
