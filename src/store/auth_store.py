"""
Servo Store - 认证 / 用户状态数据驱动
管理当前登录用户、上班打卡、权限等全局状态
"""
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import datetime


class AuthStore(QObject):
    """认证与用户状态存储"""
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- 用户 / 打卡 ----
        self.current_user: str = ""            # 当前登录用户名
        self.clock_in_time: float = 0.0        # 上班时间戳 (epoch seconds)
        self.operation_count: int = 0           # 操作次数

        # ---- 权限 ----
        self.permission_group: str = ""        # 当前用户的权限组 (e.g. "admin", "operator", "viewer")
        self.permission_routes: list = []      # 权限路由列表 (e.g. ["/gas", "/manual", "/settings"])
        self.user_groups: dict = {}            # 用户名→权限组映射 (e.g. {"张三": "operator", "李四": "admin"})

    # ---- 便捷方法 ----

    def login(self, username: str, group: str = "", routes: list = None):
        """用户登录"""
        self.current_user = username
        self.permission_group = group
        self.permission_routes = routes or []
        if username and group:
            self.user_groups[username] = group  # 记录用户名→权限组映射
        self.dataChanged.emit()

    def logout(self):
        """用户登出，清空所有状态"""
        self.current_user = ""
        self.clock_in_time = 0.0
        self.operation_count = 0
        self.permission_group = ""
        self.permission_routes = []
        self.dataChanged.emit()

    def clock_in(self):
        """打卡上班，记录当前时间戳"""
        self.clock_in_time = datetime.now().timestamp()
        self.dataChanged.emit()

    def increment_operation(self):
        """操作次数 +1"""
        self.operation_count += 1
        self.dataChanged.emit()

    def has_route(self, route: str) -> bool:
        """检查当前用户是否有某路由的权限"""
        return route in self.permission_routes

    def get_user_group(self, username: str) -> str:
        """查询指定用户名所属的权限组"""
        return self.user_groups.get(username, "")

    def to_dict(self) -> dict:
        return {
            "current_user": self.current_user,
            "clock_in_time": self.clock_in_time,
            "operation_count": self.operation_count,
            "permission_group": self.permission_group,
            "permission_routes": list(self.permission_routes),
            "user_groups": dict(self.user_groups),
        }
