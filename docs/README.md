# 后端项目概览

这是一个基于Django框架构建的Python教学平台后端项目，采用了Django REST Framework(DRF)来提供RESTful API接口。

## 技术栈

- **Python版本**: 3.13
- **Web框架**: Django 5.2.7
- **API框架**: Django REST Framework 3.16.1
- **认证机制**: JWT (djangorestframework-simplejwt)
- **数据库**: SQLite (开发环境)
- **依赖管理**: pyproject.toml

## 项目结构

```
backend/
├── accounts/           # 用户账户管理应用
│   ├── models.py      # 自定义User模型
│   ├── views.py       # 认证相关视图
│   ├── serializers.py # 序列化器
│   └── urls.py        # 账户相关URL路由
├── courses/           # 课程管理应用
│   ├── models.py      # 课程、章节、问题等相关模型
│   ├── views.py       # 视图集
│   ├── serializers.py # 序列化器
│   └── urls.py        # 课程相关URL路由
├── core/              # 项目核心配置
│   ├── settings.py    # 项目设置
│   ├── urls.py        # 主URL配置
│   └── wsgi.py        # WSGI入口
├── manage.py          # Django管理脚本
└── pyproject.toml     # 项目依赖配置
```

## 主要功能模块

### 用户认证系统
- 用户注册、登录、登出
- JWT令牌认证
- 用户信息获取

### 课程管理系统
- 课程创建、查看、更新、删除
- 章节管理(嵌套在课程下)
- 问题管理(算法题、选择题)

### 在线编程评测系统
- 代码提交
- 代码执行(Judge0集成)
- 测试用例管理
- 提交记录查看

## API特点

1. **统一前缀**: 所有API接口都位于`/api/v1/`路径下
2. **JWT认证**: 使用Bearer Token方式进行认证
3. **嵌套路由**: 章节管理使用了嵌套路由(`/courses/{course_pk}/chapters/`)
4. **分页支持**: 默认每页显示10条记录
5. **权限控制**: 默认只允许认证用户访问API

## 数据模型关系

```
User(自定义) ←→ Submission(一对多)
Course ←→ Chapter(一对多)
Chapter ←→ Problem(一对多)
Problem ←→ AlgorithmProblem(一对一)
Problem ←→ ChoiceProblem(一对一)
AlgorithmProblem ←→ TestCase(一对多)
```

## 部署方式

项目支持多种部署方式:
- 本地开发服务器(`python manage.py runserver`)
- Gunicorn生产服务器
- uWSGI生产服务器
- Docker容器化部署(需自行创建Dockerfile)

更多详细信息请参考以下文档:
- [项目结构详解](backend_structure.md)
- [数据模型文档](backend_models.md)
- [API接口文档](backend_api.md)
- [项目配置说明](backend_config.md)
- [部署流程指南](backend_deployment.md)