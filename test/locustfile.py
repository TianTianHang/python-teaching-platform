# locustfile.py
from locust import HttpUser, task, between
import time

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """每个用户启动时自动注册并登录（使用唯一用户名）"""
        # 生成唯一用户名：基于时间戳和对象ID，避免冲突
        unique_suffix = str(id(self))[-2:]  # 取对象ID后6位作为唯一后缀
        username = f"tiantian"
        st_number = f"{unique_suffix.zfill(6)[:12]}"  # 确保学号长度一致
        password = "19771201qwer"

        # 尝试注册
        # response = self.client.post(
        #     "/auth/register",
        #     data={
        #         "username": username,
        #         "stNumber": st_number,
        #         "password": password,
        #         "confirmPassword": password
        #     },
        #     name="/auth/register (auto)",
        #     allow_redirects=True
        # )
        response = self.client.post(
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
            name="/auth/login",
            allow_redirects=True
        )
        # 可选：检查注册是否成功（根据你的 API 返回判断）
        # 例如：如果返回 200 或包含 success 字段
        # if response.status_code != 200:
        #     print(f"注册失败，用户名: {username}, 状态码: {response.status_code}")
        #print(f"Cookie: {response.cookies}")
        # 注意：如果注册接口自动登录并设置 cookie，则无需额外登录
        # 否则你可能需要再调用 /auth/login
    @task
    def run_code_freely(self):
        code = """print("Hello, World!")"""
        response = self.client.post(
            "/submission",
            data={
                "code": code,
                "language": "python",
                }
            )
        print(f"Run code response: {response.status_code}, {response.text}")
    # @task
    # def get_homepage(self):
    #     self.client.get("/home")

    # @task
    # def get_courses(self):
    #     self.client.get("/courses")
    # @task
    # def get_problems(self):
    #     self.client.get("/problems")
    # @task
    # def login(self):
    #     """每个用户启动时自动注册并登录（使用唯一用户名）"""
    #     # 生成唯一用户名：基于时间戳和对象ID，避免冲突
    #     username = f"tiantian"
    #     password = "19771201qwer"

    #     response = self.client.post(
    #         "/auth/login",
    #         data={
    #             "username": username,
    #             "password": password,
    #         },
    #         name="/auth/login",
    #         allow_redirects=True
    #     )