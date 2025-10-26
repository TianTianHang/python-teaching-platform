# 后端项目结构分析

## 项目概述
本项目是一个基于Django框架的Python教学平台后端，采用Django REST Framework构建RESTful API。

## 应用模块

### core (核心配置)
- `settings.py`: 项目全局配置文件
- `urls.py`: 主URL路由配置
- `wsgi.py`/`asgi.py`: WSGI/ASGI应用入口

### accounts (用户账户管理)
- 自定义User模型，扩展了学号字段
- 用户认证相关视图和序列化器
- JWT令牌认证集成

### courses (课程管理)
- 课程、章节、问题模型
- 算法题和选择题的详细实现
- 提交记录和测试用例管理

## 主要依赖
- Django 5.2.7
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.1
- drf-nested-routers 0.95.0
- django-filter 25.2
- requests 2.32.5
- Faker 28.1.0