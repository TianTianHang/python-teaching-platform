# 项目配置文档

## 环境配置

### Python版本
项目使用 Python 3.13 版本

### 依赖管理
项目使用 `pyproject.toml` 文件管理依赖，主要依赖包括：
- Django >= 5.2.7
- djangorestframework >= 3.16.1
- djangorestframework-simplejwt >= 5.5.1
- drf-nested-routers >= 0.95.0
- django-filter >= 25.2
- requests >= 2.32.5
- Faker >= 28.1.0

## Django设置 (core/settings.py)

### 安全设置
- SECRET_KEY: 用于加密签名的密钥
- DEBUG: 开发模式开关，默认为True
- ALLOWED_HOSTS: 允许访问的主机列表，默认为空

### 应用配置
INSTALLED_APPS 包括：
- Django内置应用: admin, auth, contenttypes, sessions, messages, staticfiles
- 第三方应用: rest_framework, rest_framework_simplejwt, rest_framework_simplejwt.token_blacklist, django_filters
- 本地应用: courses, accounts

### REST Framework配置
- DEFAULT_AUTHENTICATION_CLASSES: 默认认证类，包括JWT认证和Session认证
- DEFAULT_PERMISSION_CLASSES: 默认权限类，只允许认证用户访问
- DEFAULT_PAGINATION_CLASS: 默认分页类，使用PageNumberPagination
- PAGE_SIZE: 默认每页数据条数，设置为10
- DEFAULT_RENDERER_CLASSES: 默认渲染器类，包括JSONRenderer和BrowsableAPIRenderer
- DEFAULT_FILTER_BACKENDS: 默认过滤后端，使用DjangoFilterBackend

### JWT设置 (SIMPLE_JWT)
- ACCESS_TOKEN_LIFETIME: 访问令牌有效期，30分钟
- REFRESH_TOKEN_LIFETIME: 刷新令牌有效期，7天
- ROTATE_REFRESH_TOKENS: 是否轮换刷新令牌，设为True
- BLACKLIST_AFTER_ROTATION: 轮换后是否将旧令牌加入黑名单，设为True
- ALGORITHM: 加密算法，使用HS256
- SIGNING_KEY: 签名密钥，使用项目SECRET_KEY
- AUTH_HEADER_TYPES: 认证头部类型，使用Bearer

### 自定义用户模型
- AUTH_USER_MODEL: 指定自定义用户模型为 'accounts.User'

### 中间件
使用的中间件包括：
- SecurityMiddleware
- SessionMiddleware
- CommonMiddleware
- CsrfViewMiddleware
- AuthenticationMiddleware
- MessageMiddleware
- XFrameOptionsMiddleware

### 数据库配置
- ENGINE: 数据库引擎，使用sqlite3
- NAME: 数据库文件名，db.sqlite3

### 国际化设置
- LANGUAGE_CODE: 语言代码，en-us
- TIME_ZONE: 时区，UTC
- USE_I18N: 是否启用国际化，True
- USE_TZ: 是否启用时区支持，True

### 静态文件设置
- STATIC_URL: 静态文件URL前缀，static/

### 其他设置
- DEFAULT_AUTO_FIELD: 默认主键字段类型，BigAutoField