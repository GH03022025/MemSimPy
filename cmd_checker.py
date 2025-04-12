import re


class CmdFormatChecker:
    def check(self, cmd: str):
        try:
            cmd_lst = re.split(r"\s+", cmd)
        except Exception:
            return False, "None", [None]

        method = getattr(self, cmd_lst[0], None)
        if method:
            result = method(cmd_lst)
            return result
        else:
            return False, "None", ["未知命令"]

    def cd(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "cd", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]
            
        for i in path:
            if "." in i and i != "." and i != "..":
                return False, "cd", [f"‘{i}’不是目录"]

        return True, "cd", path

    def create(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "create", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        if "." in path[-1]:
            file_name = ".".join(path[-1].split(".")[:-1])
            extension_name = path[-1].split(".")[-1]
        else:
            file_name = path[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "create",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "create",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )

        print("create check")
        return True, "create", path

    def delete(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "delete", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        if "." in path[-1]:
            file_name = ".".join(path[-1].split(".")[:-1])
            extension_name = path[-1].split(".")[-1]
        else:
            file_name = path[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "delete",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "create",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )

        print("delete check")
        return True, "delete", path

    def makdir(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "makdir", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        file_name = path[-1]

        print(file_name)

        if len(file_name) < 1 or len(file_name) > 3:
            return (
                False,
                "makdir",
                [f"‘{file_name}’：目录名应为 1~3 字符"],
            )

        return True, "makdir", path

    def deldir(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "deldir", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])
        
        if path[-1] == "":
            path = path[:-1]

        file_name = path[-1]

        print(file_name)

        if len(file_name) < 1 or len(file_name) > 3:
            return (
                False,
                "deldir",
                [f"‘{file_name}’：目录名应为 1~3 字符"],
            )

        return True, "deldir", path

    def copy(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "copy", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        if "." in path[-1]:
            file_name = ".".join(path[-1].split(".")[:-1])
            extension_name = path[-1].split(".")[-1]
        else:
            file_name = path[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "copy",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "copy",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )

        print("copy check")
        return True, "copy", path

    def paste(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "paste", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        if "." in path[-1]:
            file_name = ".".join(path[-1].split(".")[:-1])
            extension_name = path[-1].split(".")[-1]
        else:
            file_name = path[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "paste",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "paste",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )

        print("paste check")

        return True, "paste", path

    def move(self, cmd_lst):
        if len(cmd_lst) != 3 or cmd_lst[2] == "":
            return False, "move", ["命令格式错误"]
        # 路径1
        path_1 = re.split(r"/+", cmd_lst[1])

        if path_1[-1] == "":
            path_1 = path_1[:-1]

        if "." in path_1[-1]:
            file_name = ".".join(path_1[-1].split(".")[:-1])
            extension_name = path_1[-1].split(".")[-1]
        else:
            file_name = path_1[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "move",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "move",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )
        # 路径2
        path_2 = re.split(r"/+", cmd_lst[2])

        if path_2[-1] == "":
            path_2 = path_2[:-1]

        if "." in path_2[-1]:
            file_name = ".".join(path_2[-1].split(".")[:-1])
            extension_name = path_2[-1].split(".")[-1]
        else:
            file_name = path_2[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "move",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "move",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )
        
        return True, "move", [path_1, path_2]

    def edit(self, cmd_lst):
        if len(cmd_lst) != 2 or cmd_lst[1] == "":
            return False, "edit", ["命令格式错误"]

        path = re.split(r"/+", cmd_lst[1])

        if path[-1] == "":
            path = path[:-1]

        if "." in path[-1]:
            file_name = ".".join(path[-1].split(".")[:-1])
            extension_name = path[-1].split(".")[-1]
        else:
            file_name = path[-1]
            extension_name = ""

        print(file_name, extension_name)

        if len(file_name) < 0 or len(file_name) > 3:
            return (
                False,
                "edit",
                [f"‘{file_name}.{extension_name}’：文件名应为 0~3 字符"],
            )

        if len(extension_name) > 2:
            return (
                False,
                "edit",
                [f"‘{file_name}.{extension_name}’：拓展名应为 1~2 字符"],
            )

        print("edit check")
        return True, "edit", path
