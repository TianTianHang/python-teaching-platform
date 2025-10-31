# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # 每个用户在任务之间等待 1~3 秒
    wait_time = between(1, 3)

    @task(3)
    def get_homepage(self):
        self.client.get("/home")
    @task
    def get_courses(self):
        self.client.get("/courses")
    # @task(3)  # 权重为 3，表示调用频率是上面任务的 3 倍
    # def get_api(self):
    #     self.client.get("/auth/me")

    def on_start(self):
        """每个用户启动时执行一次：表单登录"""
        # 使用 data=... 发送表单数据（自动设置 Content-Type: application/x-www-form-urlencoded）
        self.client.post(
            "/auth/login",
            data={
                "username": "tiantian",
                "password": "19771201qwer"
            }
        )
        # 登录成功后，后续请求会自动携带 session cookie