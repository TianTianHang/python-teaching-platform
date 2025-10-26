# Python教学平台

这是一个基于Django和Vue.js构建的Python教学平台，包含后端API和前端界面。

## 功能特性

### 核心功能
- 用户注册和登录系统
- 课程管理和章节组织
- 在线编程题目（算法题和选择题）
- 代码在线评测系统（集成Judge0）
- 学习进度追踪功能

### 学习进度追踪
平台现在支持学习进度追踪功能，包括：
- 课程参与记录管理
- 章节完成状态跟踪
- 问题解决进度记录
- 学习进度百分比计算

## 快速启动（本地开发）

```bash
# 启动后端
cd backend && python manage.py runserver

# 启动前端
cd frontend/web-student && npm run dev
```

## 技术栈

### 后端
- Python 3.13
- Django 5.2.7
- Django REST Framework 3.16.1
- SQLite数据库（开发环境）

### 前端
- Vue.js 3.x
- Bootstrap 5.x
- Axios HTTP客户端

## 项目结构

```
python-teaching-platform/
├── backend/              # Django后端项目
│   ├── accounts/         # 用户账户管理
│   ├── courses/          # 课程和题目管理
│   ├── core/             # 项目核心配置
│   └── manage.py         # Django管理脚本
├── frontend/             # 前端项目
│   └── web-student/      # 学生端Web界面
└── docs/                 # 项目文档
```

## API文档

详细的API文档请参见 [后端API文档](docs/backend_api.md)