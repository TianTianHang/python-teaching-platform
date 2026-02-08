# locustfile.py
import random
from locust import HttpUser, SequentialTaskSet, task, between
import csv
import os
from threading import Lock
# 账户池管理（线程安全）
ACCOUNT_POOL = []
ACCOUNT_LOCK = Lock()
ACCOUNTS_LOADED = False


def load_accounts():
    """从CSV文件加载账户池"""
    global ACCOUNT_POOL, ACCOUNTS_LOADED
    csv_path = os.path.join(os.path.dirname(__file__), 'accounts.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"账户文件不存在: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ACCOUNT_POOL = list(reader)

    ACCOUNTS_LOADED = True
    # print(f"已加载 {len(ACCOUNT_POOL)} 个测试账户")


def get_account():
    """从账户池中获取一个账户（线程安全，每个账户只使用一次）"""
    global ACCOUNT_POOL, ACCOUNTS_LOADED

    if not ACCOUNTS_LOADED:
        with ACCOUNT_LOCK:
            if not ACCOUNTS_LOADED:
                load_accounts()

    with ACCOUNT_LOCK:
        if not ACCOUNT_POOL:
            raise RuntimeError("账户池已耗尽，所有账户已被使用")
        return ACCOUNT_POOL.pop()


class SubmissionScenario(SequentialTaskSet):
    """用户场景：按顺序执行的任务集"""

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        # print(f"用户 {self.username} 开始测试场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        # print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单"""
        response = self.client.post(
            "/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login",
            allow_redirects=True
        )
        if response.status_code in [200, 302]:
            # print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            pass
        else:
            # print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_home(self):
        """步骤3：进入首页"""
        response = self.client.get("/home", name="GET /home")
        # print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step4_get_playground(self):
        """步骤4：进入 Playground 页面"""
        response = self.client.get("/playground", name="GET /playground")
        # print(f"用户 {self.username}: 进入 Playground，状态码: {response.status_code}")

    @task(1)
    def step5_run_code(self):
        """步骤5：运行代码"""
        code = """print("Hello, World!")"""
        response = self.client.post(
            "/submission",
            data={
                "code": code,
                "language": "python",
            },
            name="POST /submission"
        )
        # print(f"用户 {self.username}: 运行代码，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        # print(f"用户 {self.username}: 测试场景结束")


class ProblemUserScenario(SequentialTaskSet):
    """问题页面用户场景：按顺序执行的任务集"""

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        # print(f"用户 {self.username} 开始问题场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        # print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单"""
        response = self.client.post(
            "/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login",
            allow_redirects=True
        )
        if response.status_code in [200, 302]:
            # print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            pass
        else:
            # print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_home(self):
        """步骤3：进入首页"""
        response = self.client.get("/home", name="GET /home")
        # print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step4_get_problems(self):
        """步骤4：进入问题列表页面"""
        response = self.client.get("/problems", name="GET /problems")
        # print(f"用户 {self.username}: 进入问题列表，状态码: {response.status_code}")

    @task(1)
    def step5_get_problem_detail(self):
        """步骤5：打开一个具体问题"""
        problem_id = random.choice([1,2,3,4,5])  # 可以根据需要改为随机或从列表中选择
        response = self.client.get(f"/problems/{problem_id}", name="GET /problems/{id}")
        # print(f"用户 {self.username}: 打开问题 {problem_id}，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        # print(f"用户 {self.username}: 问题场景结束")


class CourseUserScenario(SequentialTaskSet):
    """课程页面用户场景：按顺序执行的任务集"""

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        self.course_id = 2
        self.chapter_id = 2
        # print(f"用户 {self.username} 开始课程场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        # print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单"""
        response = self.client.post(
            "/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login",
            allow_redirects=True
        )
        if response.status_code in [200, 302]:
            # print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            pass
        else:
            # print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_home(self):
        """步骤3：进入首页"""
        response = self.client.get("/home", name="GET /home")
        # print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step4_get_courses(self):
        """步骤4：进入课程列表页面"""
        response = self.client.get("/courses", name="GET /courses")
        # print(f"用户 {self.username}: 进入课程列表，状态码: {response.status_code}")

    @task(1)
    def step5_get_course_detail(self):
        """步骤5：打开一个具体课程"""
        response = self.client.get(f"/courses/{self.course_id}", name="GET /courses/{id}")
        # print(f"用户 {self.username}: 打开课程 {self.course_id}，状态码: {response.status_code}")

    @task(1)
    def step6_post_join_course(self):
        """步骤6：加入课程"""
        with self.client.post(
            f"/courses/{self.course_id}",
            name="POST /courses/{id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                # print(f"用户 {self.username}: 成功加入课程 {self.course_id}")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    if error_data.get('detail') == '您已经注册了该课程':
                        response.success()
                        # print(f"用户 {self.username}: 已加入课程 {self.course_id}")
                    else:
                        response.failure(f"Unexpected 400 error: {error_data}")
                except Exception:
                    response.failure(f"400 error but cannot parse JSON")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def step7_get_chapter(self):
        """步骤7：打开课程的2章节"""
        response = self.client.get(f"/courses/{self.course_id}/chapters/{self.chapter_id}", name="GET /courses/{id}/chapters/{self.chapter_id}")
        # print(f"用户 {self.username}: 打开课程 {self.course_id} 的 chapter {self.chapter_id}，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        # print(f"用户 {self.username}: 课程场景结束")


class RegisterUserScenario(SequentialTaskSet):
    """注册场景：用户注册新账户"""

    def on_start(self):
        """生成唯一的注册信息"""
        import time
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        self.username = f"newuser_{timestamp}_{random_suffix}"
        self.password = "NewPass123!"
        self.st_number = f"2025{random_suffix:06d}"
        # print(f"准备注册新用户: {self.username}")

    @task(1)
    def step1_get_register_page(self):
        """步骤1：进入注册页面"""
        response = self.client.get("/auth/register", name="GET /auth/register")
        # print(f"进入注册页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_register(self):
        """步骤2：提交注册表单"""
        response = self.client.post(
            "/auth/register",
            data={
                "username": self.username,
                "password": self.password,
                "st_number": self.st_number,
            },
            name="POST /auth/register",
            allow_redirects=True
        )
        if response.status_code in [200, 302]:
            # print(f"用户 {self.username}: 注册成功，状态码: {response.status_code}")
            pass
        else:
            # print(f"用户 {self.username}: 注册失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_home(self):
        """步骤3：进入首页"""
        response = self.client.get("/home", name="GET /home")
        # print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        # print(f"用户 {self.username}: 注册场景结束")


class WebsiteUser(HttpUser):
    """网站用户：执行完整的测试场景"""
    wait_time = between(1, 3)
    tasks = [
    (SubmissionScenario, 2),
    (ProblemUserScenario, 3),
    (CourseUserScenario, 5),
    # (RegisterUserScenario, 1),
]