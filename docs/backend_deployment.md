# 部署流程文档

## 本地开发环境部署

### 环境准备
1. 确保已安装 Python 3.13
2. 安装项目依赖:
   ```bash
   pip install -e .
   ```
   或者使用 uv 工具(如果项目使用):
   ```bash
   uv sync
   ```

### 数据库初始化
1. 运行数据库迁移:
   ```bash
   python manage.py migrate
   ```

### 创建超级用户(可选)
```bash
python manage.py createsuperuser
```

### 启动开发服务器
```bash
python manage.py runserver
```

## 生产环境部署

### 环境准备
1. 安装 Python 3.13
2. 安装项目依赖:
   ```bash
   pip install -e .
   ```

### 配置设置
1. 设置环境变量:
   - SECRET_KEY: Django密钥(必须设置)
   - DEBUG: 设置为False
   - ALLOWED_HOSTS: 设置允许访问的域名/IP地址
   - DATABASE_URL: 数据库连接URL(如果使用PostgreSQL等)

2. 修改 `core/settings.py` 中的相关配置或使用环境变量覆盖默认设置

### 静态文件收集
```bash
python manage.py collectstatic
```

### 数据库迁移
```bash
python manage.py migrate
```

### Web服务器选择
可以选择以下几种方式部署:

#### 使用Gunicorn
1. 安装Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. 启动服务:
   ```bash
   gunicorn core.wsgi:application --bind 0.0.0.0:8000
   ```

#### 使用uWSGI
1. 安装uWSGI:
   ```bash
   pip install uwsgi
   ```
2. 创建uWSGI配置文件:
   ```ini
   [uwsgi]
   module = core.wsgi:application
   master = true
   processes = 4
   socket = :8000
   chmod-socket = 666
   vacuum = true
   die-on-term = true
   ```
3. 启动服务:
   ```bash
   uwsgi --ini uwsgi.ini
   ```

#### 使用Daphne(ASGI服务器)
1. 安装Daphne:
   ```bash
   pip install daphne
   ```
2. 启动服务:
   ```bash
   daphne core.asgi:application --bind 0.0.0.0 --port 8000
   ```

### 反向代理配置(Nginx示例)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
}
```

### Docker部署(建议)
由于项目中暂未包含Dockerfile，建议创建以下文件:

#### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - ALLOWED_HOSTS=localhost,127.0.0.1
    volumes:
      - static_volume:/app/staticfiles
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=teaching_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:
  static_volume:
```

注意: 当前项目使用SQLite数据库，生产环境中建议切换到PostgreSQL或MySQL等更稳定的数据库系统。