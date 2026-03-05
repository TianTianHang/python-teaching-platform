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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")  # 支持环境变量配置，默认本地开发

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
    # 代码执行场景：用户需要查看运行结果
    wait_time = between(2, 4)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始测试问题提交场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            # 保存 token
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_playground(self):
        """步骤6：进入 Playground 页面"""
        response = self.client.get("/playground", name="GET /playground")
        print(f"用户 {self.username}: 进入 Playground，状态码: {response.status_code}")

    @task(1)
    def step7_run_code(self):
        """步骤7：运行代码"""
        code = """print("Hello, World!")"""
        response = self.client.post(
            "/submission",
            data={
                "code": code,
                "language": "python",
            },
            name="POST /submission"
        )
        print(f"用户 {self.username}: 运行代码，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 测试场景结束")


class ProblemUserScenario(SequentialTaskSet):
    """问题页面用户场景：按顺序执行的任务集"""
    # 问题浏览场景：用户需要阅读题目内容
    wait_time = between(3, 6)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始问题场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
             f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            # 保存 token
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_problems(self):
        """步骤6：进入问题列表页面"""
        response = self.client.get("/problems", name="GET /problems")
        print(f"用户 {self.username}: 进入问题列表，状态码: {response.status_code}")
      
    @task(1)
    def step7_get_problem_detail(self):
        """步骤7：打开一个具体问题"""
        problem_id = random.choice([1,2,3,4,5])  # 可以根据需要改为随机或从列表中选择
        response = self.client.get(f"/problems/{problem_id}", name="GET /problems/{id}")
        print(f"用户 {self.username}: 打开问题 {problem_id}，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 问题场景结束")


class CourseUserScenario(SequentialTaskSet):
    """课程页面用户场景：按顺序执行的任务集"""
    # 课程学习场景：用户需要阅读课程章节内容，停留时间最长
    wait_time = between(4, 8)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        self.course_id = 2
        self.chapter_id = 7
        print(f"用户 {self.username} 开始课程场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
             f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            # 保存 token
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_courses(self):
        """步骤6：进入课程列表页面"""
        response = self.client.get("/courses", name="GET /courses")
        print(f"用户 {self.username}: 进入课程列表，状态码: {response.status_code}")

    @task(1)
    def step7_get_course_detail(self):
        """步骤7：打开一个具体课程"""
        response = self.client.get(f"/courses/{self.course_id}", name="GET /courses/{id}")
        print(f"用户 {self.username}: 打开课程 {self.course_id}，状态码: {response.status_code}")

    @task(1)
    def step8_post_join_course(self):
        """步骤8：加入课程"""
        with self.client.post(
            f"{BACKEND_URL}/courses/{self.course_id}/enroll/",
            name="POST /courses/{id}/enroll/",
            catch_response=True,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ) as response:
            if response.status_code == 200:
                response.success()
                print(f"用户 {self.username}: 成功加入课程 {self.course_id}")
            elif response.status_code == 400:
                try:
                    if '您已经注册了该课程' in response.text:
                        response.success()
                        print(f"用户 {self.username}: 已加入课程 {self.course_id}")
                    else:
                        response.failure(f"Unexpected 400 error: {response.text}")
                except Exception:
                    response.failure(f"Error parsing response: {response.text}")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def step9_get_chapter(self):
        """步骤9：打开课程的章节"""
        response = self.client.get(f"/courses/{self.course_id}/chapters/{self.chapter_id}", name="GET /courses/{id}/chapters/{self.chapter_id}")
        print(f"用户 {self.username}: 打开课程 {self.course_id} 的 chapter {self.chapter_id}，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 课程场景结束")


class RegisterUserScenario(SequentialTaskSet):
    """注册场景：用户注册新账户"""
    # 注册场景：用户填写表单
    wait_time = between(2, 4)

    def on_start(self):
        """生成唯一的注册信息"""
        import time
# 新增测试场景

class HomeBrowsingScenario(SequentialTaskSet):
    """首页浏览场景：测试首页的 client loader 请求"""
    wait_time = between(3, 6)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始首页浏览场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页（触发 client loader）"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_enrollments(self):
        """步骤6：获取已注册课程（首页 client loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/enrollments/",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/enrollments/"
        )
        print(f"用户 {self.username}: 获取已注册课程，状态码: {response.status_code}")

    @task(1)
    def step7_get_problem_progress(self):
        """步骤7：获取问题进度（首页 client loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/problem-progress/?status_not=solved",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/problem-progress/"
        )
        print(f"用户 {self.username}: 获取问题进度，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 首页浏览场景结束")


class ProfileBrowsingScenario(SequentialTaskSet):
    """个人资料浏览场景：测试个人资料页面的请求"""
    wait_time = between(3, 6)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始个人资料浏览场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_profile(self):
        """步骤5：进入个人资料页面（触发 client loader）"""
        response = self.client.get("/profile", name="GET /profile")
        print(f"用户 {self.username}: 进入个人资料，状态码: {response.status_code}")

    @task(1)
    def step6_get_user_info_again(self):
        """步骤6：获取用户信息（个人资料页 client loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/auth/me (profile)"
        )
        print(f"用户 {self.username}: 获取用户信息（profile），状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 个人资料浏览场景结束")


class MembershipBrowsingScenario(SequentialTaskSet):
    """会员页面浏览场景：测试会员页面的请求"""
    wait_time = between(3, 6)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始会员页面浏览场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_membership(self):
        """步骤5：进入会员页面（触发 server loader）"""
        response = self.client.get("/membership", name="GET /membership")
        print(f"用户 {self.username}: 进入会员页面，状态码: {response.status_code}")

    @task(1)
    def step6_get_membership_types(self):
        """步骤6：获取会员类型（会员页 server loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/membership-types/",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/membership-types/"
        )
        print(f"用户 {self.username}: 获取会员类型，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 会员页面浏览场景结束")


class JupyterScenario(SequentialTaskSet):
    """Jupyter 场景：测试 Jupyter 页面的访问"""
    wait_time = between(5, 10)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        print(f"用户 {self.username} 开始 Jupyter 场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_jupyter(self):
        """步骤5：进入 Jupyter 页面（触发 server loader）"""
        response = self.client.get("/jupyter", name="GET /jupyter")
        print(f"用户 {self.username}: 进入 Jupyter 页面，状态码: {response.status_code}")

    @task(1)
    def step6_get_jupyter_lite(self):
        """步骤6：加载 Jupyter Lite"""
        response = self.client.get("/jupyterlite/lab/index.html", name="GET /jupyterlite/lab/index.html")
        print(f"用户 {self.username}: 加载 Jupyter Lite，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: Jupyter 场景结束")


class ExamScenario(SequentialTaskSet):
    """考试场景：测试考试相关页面的请求"""
    wait_time = between(4, 8)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        self.course_id = 2  # 测试课程 ID
        print(f"用户 {self.username} 开始考试场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_courses(self):
        """步骤6：进入课程列表页面"""
        response = self.client.get("/courses", name="GET /courses")
        print(f"用户 {self.username}: 进入课程列表，状态码: {response.status_code}")

    @task(1)
    def step7_get_course_detail(self):
        """步骤7：打开课程详情"""
        response = self.client.get(f"/courses/{self.course_id}", name="GET /courses/{id}")
        print(f"用户 {self.username}: 打开课程 {self.course_id}，状态码: {response.status_code}")

    @task(1)
    def step8_post_join_course(self):
        """步骤8：加入课程"""
        with self.client.post(
            f"{BACKEND_URL}/courses/{self.course_id}/enroll/",
            name="POST /courses/{id}/enroll/",
            catch_response=True,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ) as response:
            if response.status_code == 200:
                response.success()
                print(f"用户 {self.username}: 成功加入课程 {self.course_id}")
            elif response.status_code == 400:
                try:
                    if '您已经注册了该课程' in response.text:
                        response.success()
                        print(f"用户 {self.username}: 已加入课程 {self.course_id}")
                    else:
                        response.failure(f"Unexpected 400 error: {response.text}")
                except Exception:
                    response.failure(f"Error parsing response: {response.text}")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def step9_get_course_exams(self):
        """步骤9：进入课程考试列表（触发 server loader）"""
        response = self.client.get(f"/courses/{self.course_id}/exams", name="GET /courses/{id}/exams")
        print(f"用户 {self.username}: 进入课程考试列表，状态码: {response.status_code}")

    @task(1)
    def step10_get_course_detail_api(self):
        """步骤10：获取课程详情（考试页 server loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id} (exams)"
        )
        print(f"用户 {self.username}: 获取课程详情，状态码: {response.status_code}")

    @task(1)
    def step11_get_course_exams_api(self):
        """步骤11：获取课程考试列表（考试页 server loader 请求）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}/exams",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}/exams"
        )
        print(f"用户 {self.username}: 获取课程考试列表，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 考试场景结束")


class ComprehensiveScenario(SequentialTaskSet):
    """综合场景：覆盖所有主要页面的 client loader 请求"""
    wait_time = between(2, 5)

    def on_start(self):
        """用户启动时获取账户"""
        self.account = get_account()
        self.username = self.account['username']
        self.password = self.account['password']
        self.course_id = random.choice([2])
        self.problem_id = random.choice([1, 2, 3, 4, 5])
        print(f"用户 {self.username} 开始综合测试场景")

    @task(1)
    def step1_get_login_page(self):
        """步骤1：进入登录页面"""
        response = self.client.get("/auth/login", name="GET /auth/login")
        print(f"用户 {self.username}: 进入登录页面，状态码: {response.status_code}")

    @task(1)
    def step2_post_login(self):
        """步骤2：提交登录表单，获取 token"""
        response = self.client.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            name="POST /auth/login"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 登录成功，状态码: {response.status_code}")
            try:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
            except Exception as e:
                print(f"用户 {self.username}: 解析 token 失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 登录失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step3_get_user_info(self):
        """步骤3：获取用户信息"""
        response = self.client.get(
            f"{BACKEND_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /auth/me"
        )
        if response.status_code == 200:
            print(f"用户 {self.username}: 获取用户信息成功")
            try:
                self.user_info = response.json()
            except Exception as e:
                print(f"用户 {self.username}: 解析用户信息失败: {e}")
                self.interrupt()
        else:
            print(f"用户 {self.username}: 获取用户信息失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step4_set_session(self):
        """步骤4：设置服务端 session"""
        import json
        response = self.client.post(
            "/auth/set-session",
            data={
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token,
                "user": json.dumps(self.user_info),
            },
            name="POST /auth/set-session"
        )
        if response.status_code in [200, 302]:
            print(f"用户 {self.username}: 设置 session 成功，状态码: {response.status_code}")
        else:
            print(f"用户 {self.username}: 设置 session 失败，状态码: {response.status_code}")
            self.interrupt()

    @task(1)
    def step5_get_home(self):
        """步骤5：进入首页"""
        response = self.client.get("/home", name="GET /home")
        print(f"用户 {self.username}: 进入首页，状态码: {response.status_code}")

    @task(1)
    def step6_get_enrollments(self):
        """步骤6：获取已注册课程（首页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/enrollments/",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/enrollments/"
        )
        print(f"用户 {self.username}: 获取已注册课程，状态码: {response.status_code}")

    @task(1)
    def step7_get_problem_progress(self):
        """步骤7：获取问题进度（首页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/problem-progress/?status_not=solved",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/problem-progress/"
        )
        print(f"用户 {self.username}: 获取问题进度，状态码: {response.status_code}")

    @task(1)
    def step8_get_courses(self):
        """步骤8：进入课程列表"""
        response = self.client.get("/courses", name="GET /courses")
        print(f"用户 {self.username}: 进入课程列表，状态码: {response.status_code}")

    @task(1)
    def step9_get_courses_api(self):
        """步骤9：获取课程列表（课程页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/?page=1&page_size=10",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/"
        )
        print(f"用户 {self.username}: 获取课程列表 API，状态码: {response.status_code}")

    @task(1)
    def step10_get_course_detail(self):
        """步骤10：进入课程详情"""
        response = self.client.get(f"/courses/{self.course_id}", name="GET /courses/{id}")
        print(f"用户 {self.username}: 进入课程详情，状态码: {response.status_code}")

    @task(1)
    def step11_get_course_detail_api(self):
        """步骤11：获取课程详情（课程详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}"
        )
        print(f"用户 {self.username}: 获取课程详情 API，状态码: {response.status_code}")

    @task(1)
    def step12_get_course_enrollment(self):
        """步骤12：获取课程注册信息（课程详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/enrollments/?course={self.course_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/enrollments/?course={id}"
        )
        print(f"用户 {self.username}: 获取课程注册信息，状态码: {response.status_code}")

    @task(1)
    def step13_get_chapters_list(self):
        """步骤13：进入课程章节列表页面"""
        self.chapter_id = random.choice([7])
        response = self.client.get(f"/courses/{self.course_id}/chapters", name="GET /courses/{id}/chapters")
        print(f"用户 {self.username}: 进入课程章节列表，状态码: {response.status_code}")

    @task(1)
    def step14_get_chapters_list_api_1(self):
        """步骤14：获取课程详情（章节列表页 client loader 请求1）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id} (chapters)"
        )
        print(f"用户 {self.username}: 获取课程详情（章节列表），状态码: {response.status_code}")

    @task(1)
    def step15_get_chapters_list_api_2(self):
        """步骤15：获取章节列表（章节列表页 client loader 请求2）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}/chapters/?page=1&page_size=10&exclude=content",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}/chapters/"
        )
        print(f"用户 {self.username}: 获取章节列表，状态码: {response.status_code}")

    @task(1)
    def step16_get_chapter_detail(self):
        """步骤16：打开章节详情页面"""
        response = self.client.get(
            f"/courses/{self.course_id}/chapters/{self.chapter_id}", 
            name="GET /courses/{id}/chapters/{chapterId}"
        )
        print(f"用户 {self.username}: 打开章节详情，状态码: {response.status_code}")

    @task(1)
    def step17_get_chapter_unlock_status(self):
        """步骤17：获取章节解锁状态（章节详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}/chapters/{self.chapter_id}/unlock_status",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}/chapters/{chapterId}/unlock_status"
        )
        print(f"用户 {self.username}: 获取章节解锁状态，状态码: {response.status_code}")

    @task(1)
    def step18_get_chapter_detail_api(self):
        """步骤18：获取章节详情（章节详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}/chapters/{self.chapter_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}/chapters/{chapterId}"
        )
        print(f"用户 {self.username}: 获取章节详情，状态码: {response.status_code}")

    @task(1)
    def step18_5_get_chapter_problems_api(self):
        """步骤18.5：获取章节问题（章节详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/courses/{self.course_id}/chapters/{self.chapter_id}/problems?exclude=recent_threads",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/courses/{id}/chapters/{chapterId}/problems"
        )
        print(f"用户 {self.username}: 获取章节问题，状态码: {response.status_code}")

    @task(1)
    def step19_get_problems(self):
        """步骤19：进入问题列表"""
        response = self.client.get("/problems", name="GET /problems")
        print(f"用户 {self.username}: 进入问题列表，状态码: {response.status_code}")

    @task(1)
    def step20_get_problems_api(self):
        """步骤20：获取问题列表（问题页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/problems/?page=1&page_size=10&exclude=content,recent_threads,status,chapter_title,updated_at",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/problems/"
        )
        print(f"用户 {self.username}: 获取问题列表 API，状态码: {response.status_code}")

    @task(1)
    def step21_get_problem_detail(self):
        """步骤21：进入问题详情"""
        response = self.client.get(f"/problems/{self.problem_id}", name="GET /problems/{id}")
        print(f"用户 {self.username}: 进入问题详情，状态码: {response.status_code}")

    @task(1)
    def step22_get_problem_detail_api(self):
        """步骤22：获取问题详情（问题详情页 client loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/problems/{self.problem_id}",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/problems/{id}"
        )
        print(f"用户 {self.username}: 获取问题详情 API，状态码: {response.status_code}")

    @task(1)
    def step23_get_profile(self):
        """步骤23：进入个人资料"""
        response = self.client.get("/profile", name="GET /profile")
        print(f"用户 {self.username}: 进入个人资料，状态码: {response.status_code}")

    @task(1)
    def step24_get_membership(self):
        """步骤24：进入会员页面"""
        response = self.client.get("/membership", name="GET /membership")
        print(f"用户 {self.username}: 进入会员页面，状态码: {response.status_code}")

    @task(1)
    def step25_get_membership_types(self):
        """步骤25：获取会员类型（会员页 server loader）"""
        response = self.client.get(
            f"{BACKEND_URL}/membership-types/",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            name="GET /api/v1/membership-types/"
        )
        print(f"用户 {self.username}: 获取会员类型，状态码: {response.status_code}")

    @task(1)
    def step26_get_playground(self):
        """步骤26：进入练习场"""
        response = self.client.get("/playground", name="GET /playground")
        print(f"用户 {self.username}: 进入练习场，状态码: {response.status_code}")

    def on_stop(self):
        """用户停止时记录"""
        print(f"用户 {self.username}: 综合测试场景结束")


class WebsiteUser(HttpUser):
    """网站用户：执行完整的测试场景"""
    # wait_time 已在各场景中分别设置，模拟不同操作的真实用户行为
    tasks = [
        (SubmissionScenario, 0),                    # 代码提交场景（禁用）
        (ProblemUserScenario, 3),                   # 问题浏览场景
        (CourseUserScenario, 3),                    # 课程学习场景
        (RegisterUserScenario, 0),                  # 注册场景（禁用）
        (HomeBrowsingScenario, 2),                  # 首页浏览场景（新增）
        (ProfileBrowsingScenario, 2),               # 个人资料浏览场景（新增）
        (MembershipBrowsingScenario, 1),            # 会员页面浏览场景（新增）
        (JupyterScenario, 1),                       # Jupyter 场景（新增）
        (ExamScenario, 2),                          # 考试场景（新增）
        (ComprehensiveScenario, 1),                 # 综合测试场景（新增）
    ]
