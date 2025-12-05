# 部署文档
## 依赖安装

### uv

```shell
pip install uv
```

### nodejs24

```shell
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
npm i -g pnpm
```

### redis 7

```shell
# 从源码构建
# 构建依赖
sudo apt install -y build-essential tcl wget pkg-config
# 下载源码
wget https://mirrors.huaweicloud.com/redis/redis-7.2.5.tar.gz
# 编译安装
tar xzf redis-7.2.5.tar.gz
cd redis-7.2.5
make -j$(nproc)
sudo make install
rm /tmp/redis-7.2.5.tar.gz
rm -rf /tmp/redis-7.2.5
```

install path: /usr/local/bin

sudo adduser --system --group --no-create-home redis

user redis

配置

```shell
# 后台运行（daemonize）
daemonize no

# 绑定地址（根据需求）
bind 127.0.0.1 ::1 
port 6379

logfile /var/log/redis/redis-server.log

dir /var/lib/redis

# 持久化（默认开启 RDB）
save 900 1
save 300 10
save 60 10000

# 安全：重命名危险命令（可选）
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

启动

sudo -u redis redis-server /etc/redis/redis.conf

停止

sudo -u redis redis-cli  shutdown

```shell
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/local/bin/redis-cli -p 6379 shutdown
Restart=always
RestartSec=5
WorkingDirectory=/var/lib/redis
PermissionsStartOnly=true

[Install]
WantedBy=multi-user.target
```

## PostgreSQL 15

```shell
# 从源码构建
# 构建依赖
sudo apt install build-essential libreadline-dev zlib1g-dev flex bison libxml2-dev libxslt1-dev libssl-dev python3-dev libpam0g-dev -y
# 下载源码
cd /tmp
wget https://mirrors.aliyun.com/postgresql/source/v15.6/postgresql-15.6.tar.gz
tar -xzf postgresql-15.6.tar.gz
cd postgresql-15.6
# 编译安装
./configure --prefix=/usr/local/pgsql-15 --with-openssl
make -j$(nproc)
sudo make install
rm /tmp/postgresql-15.6.tar.gz
rm -rf /tmp/postgresql-15.6
```

install path: /usr/local/pgsql-15/bin

sudo adduser --system --group --no-create-home postgres

user：postgres

```shell
sudo mkdir -p /var/lib/pgsql/data
sudo chown postgres:postgres /var/lib/pgsql/data
sudo mkdir -p /var/log/postgresql
sudo chown postgres:postgres /var/log/postgresql
# 初始化（切换到 postgres 用户）
sudo -u postgres /usr/local/pgsql-15/bin/initdb -D /var/lib/pgsql/data --encoding=UTF8
# 设置密码
sudo -u postgres /usr/local/pgsql-15/bin/psql
ALTER USER postgres PASSWORD 'your_secure_password';
# 创建数据库
sudo -u postgres /usr/local/pgsql-15/bin/createdb "teaching_palform"
# 查看数据库是否创建
sudo -u postgres /usr/local/pgsql-15/bin/psql -lqt
# 重载配置
sudo -u postgres /usr/local/pgsql-15/bin/pg_ctl reload -D /var/lib/pgsql/data
```

配置

```shell
# 监听地址（默认只本地）
listen_addresses = 'localhost'          # 仅本地
# listen_addresses = '*'                # 允许远程（需配合 pg_hba.conf）

# 端口（默认 5432）
port = 5432

# 内存设置（根据服务器调整）
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# 日志（可选）
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
logging_collector = on
log_statement = 'none'   # 可设为 'ddl' 或 'all'（调试用）
```
```shell
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

启动

sudo -u postgres /usr/local/pgsql-15/bin/pg\_ctl -D /var/lib/pgsql/data start

停止

sudo -u postgres /usr/local/pgsql-15/bin/pg\_ctl -D /var/lib/pgsql/data stop -m fast

```shell
[Unit]
Description=PostgreSQL 15 Database Server
After=network.target

[Service]
Type=forking
User=postgres
Group=postgres
Environment=PGDATA=/var/lib/pgsql/data
ExecStart=/usr/local/pgsql-15/bin/pg_ctl -D ${PGDATA} -l /var/log/postgresql/postgresql.log start
ExecStop=/usr/local/pgsql-15/bin/pg_ctl -D ${PGDATA} stop -m fast
ExecReload=/usr/local/pgsql-15/bin/pg_ctl -D ${PGDATA} reload
Restart=on-failure
RestartSec=5
TimeoutSec=300

[Install]
WantedBy=multi-user.target
```

## 构建JupyterLite

```shell
cd frontend/JupyterLite
uv sync --index-url='http://mirrors.cloud.aliyuncs.com/pypi/simple/'
./build.sh
```

## 构建web-student

```shell
cd frontend/web-student
pnpm i
pnpm run build

```

构建产物在build里

使用绝对路径链接

ln -sf ~/python-teaching-platform/frontend/web-student/ /opt/web-student/

chown web-student:web-student  /opt/web-student/

```shell
[Unit]
Description=Web Student SSR Frontend
After=network.target

[Service]
User=web-student
Group=web-student
WorkingDirectory=/opt/web-student/
Environment=NODE_ENV=development
Environment=PORT=3000
Environment=API_BASE_URL=http://localhost:8000/api/v1
Environment=FILE_STORAGE_DIR=/var/www/frontend
ExecStart=pnpm run start
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Environment=NODE\_ENV=production https后开启

## backend

```shell
SECRET_KEY=django-insecure-k9#Lm2$vN8p@Qw4&Ez7!xR5^yT6*uY1(iO0)aP3$sDf9%gHj+
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/teaching_palform
REDIS_URL=redis://localhost:6379/0
JUDGE0_BASE_URL=http://localhost:2358
JUDGE0_API_KEY=
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8080,http://localhost:8080
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@myapp.com
DJANGO_SUPERUSER_PASSWORD=SecurePass123!

```
```shell
# 在backend用户下创建虚拟环境
uv sync --index-url='http://mirrors.cloud.aliyuncs.com/pypi/simple/'
# 1. 数据库迁移
uv run python manage.py migrate --noinput
uv run python manage.py populate_sample_data
# 2. 创建超级用户（使用自定义命令）
uv run python manage.py create_default_superuser
# 3. 收集静态文件
uv run python manage.py collectstatic --noinput
# 静态文件在static里
```

sudo adduser --system --group  backend

```plaintext
[Unit]
Description=Teaching Platform Backend (Django + Gunicorn)
After=network.target redis.service postgresql-15.service

[Service]
User=backend
Group=backend
WorkingDirectory=/opt/backend
EnvironmentFile=/opt/backend/.env
ExecStart=uv run gunicorn --bind 127.0.0.1:8000 --access-logfile - --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' core.wsgi:application
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## judge0

#### Deployment Steps

1.  Download and extract the release archive:
    

```plaintext
wget https://github.com/judge0/judge0/releases/download/v1.13.1/judge0-v1.13.1.zip
unzip judge0-v1.13.1.zip

```

2.  Visit [this website](https://www.random.org/passwords/?num=1&len=32&format=plain&rnd=new)to generate a random password.
    
3.  Use the generated password to update the variable `REDIS_PASSWORD` in the `judge0.conf` file.
    
4.  Visit again [this website](https://www.random.org/passwords/?num=1&len=32&format=plain&rnd=new)to generate another random password.
    
5.  Use the generated password to update the variable `POSTGRES_PASSWORD` in the `judge0.conf` file.
    
6.  Run all services and wait a few seconds until everything is initialized:
    

```plaintext
cd judge0-v1.13.1
docker-compose up -d db redis
sleep 10s
docker-compose up -d
sleep 5s

```

7.  Your instance of Judge0 CE v1.13.1 is now up and running; visit docs at `http://<IP ADDRESS OF YOUR SERVER>:2358/docs`.
    

## ngnix安装配置 1.28

### 编译安装

```shell
sudo apt install -y build-essential libpcre3 libpcre3-dev zlib1g-dev libssl-dev wget curl git
cd /tmp
NGINX_VERSION=1.28.0  # 请根据 https://nginx.org/en/download.html 更新
wget https://github.com/nginx/nginx/releases/download/release-${NGINX_VERSION}/nginx-${NGINX_VERSION}.tar.gz
tar -zxvf nginx-${NGINX_VERSION}.tar.gz
cd nginx-${NGINX_VERSION}
# 编译配置
./configure \
  --prefix=/usr/local/nginx \
  --sbin-path=/usr/local/nginx/sbin/nginx \
  --conf-path=/usr/local/nginx/conf/nginx.conf \
  --error-log-path=/var/log/nginx/error.log \
  --http-log-path=/var/log/nginx/access.log \
  --pid-path=/var/run/nginx.pid \
  --lock-path=/var/run/nginx.lock \
  --user=nginx \
  --group=nginx \
  --with-http_ssl_module \
  --with-http_v2_module \
  --with-http_realip_module \
  --with-http_gzip_static_module \
  --with-http_stub_status_module \
  --with-http_secure_link_module \
  --with-pcre \
  --with-file-aio \
  --with-http_dav_module \
  --with-threads

make -j$(nproc)
sudo make install
rm /tmp/nginx-${NGINX_VERSION}.tar.gz
rm /tmp/nginx-${NGINX_VERSION} -rf
# 创建目录
sudo mkdir -p /var/log/nginx
sudo chown -R nginx:nginx /var/log/nginx
sudo chmod 755 /var/log/nginx
```
```plaintext
# 推荐根据 CPU 核心数设置，'auto' 是最佳实践
worker_processes auto;
events {
    # 增加连接数，需要配合系统 ulimit -n
    worker_connections 4096;
    
    # 启用 epoll 模型，在 Linux 下性能更优
    use epoll;
    
    # 允许 worker 进程一次性接受所有新连接
    multi_accept on;
}
http {
    # MIME 类型配置
    include mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # --- 性能优化 ---
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    
    # --- 安全与限制 ---
    # 隐藏 Nginx 版本号
    server_tokens off; 
    
    # 客户端请求体缓冲区大小
    client_body_buffer_size 128k;
    
    # 允许的最大请求体，例如 16M (根据需求调整)
    client_max_body_size 16m; 
    
    # 客户端超时设置，防止慢连接攻击
    client_header_timeout 10s;
    client_body_timeout 10s;
    send_timeout 10s;

    # --- Gzip 压缩配置 ---
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_min_length 256;
    # 扩展 Gzip 类型，覆盖更多常见资源
    gzip_types 
        application/javascript 
        application/json 
        application/xml
        application/x-font-ttf
        application/vnd.ms-fontobject
        image/svg+xml
        font/opentype
        text/css 
        text/plain 
        text/xml;

    # --- Upstream 定义 ---
    
    # SSR 后端 (web-student)
    upstream ssr_backend {
        server localhost:3000;
        keepalive 32; 
    }

    # Admin 后端 (backend)
    upstream admin_backend {
        server localhost:8000;
        keepalive 32; # 同样建议为 admin 后端启用
    }
    
    # --- Server 1: 前台应用 (端口 80) ---
    server {
        listen 80;
        server_name _; # 捕获所有未匹配的域名
        root /var/www/frontend;
        # ----------------------------------------------------
        # 定义一个命名位置 (@proxy_to_ssr) 用于 SSR 代理转发
        # ----------------------------------------------------
        location @proxy_to_ssr {
            proxy_pass http://ssr_backend;

            # --- 传递关键头信息 ---
            # [重要] 取消注释，后端应用通常需要 Host 头
            proxy_set_header Host $host; 
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # --- 启用 HTTP/1.1 和 Keep-Alive ---
            proxy_http_version 1.1;
            # [重要] 清空 Connection 头，以正确使用 upstream keepalive
            proxy_set_header Connection ""; 
        }
        location / {
            try_files $uri $uri/ @proxy_to_ssr;
        }
        location = /favicon.ico {
            expires 1d;
            add_header Cache-Control "public, immutable";
        }
        # 静态资源 /assets
        location /assets {
            # 优化：为静态资源添加缓存头
            expires 1M; # 缓存 1 个月
            add_header Cache-Control "public, must-revalidate";
        }
        location /jupyterlite {
            # 优化：为静态资源添加缓存头
            expires 1M; # 缓存 1 个月
            add_header Cache-Control "public, must-revalidate";
        }
   
    }

    # --- Server 2: 后台管理 (端口 8080) ---
    server {
        listen 8080;
        server_name admin; # 明确指定 server_name

        # Admin 静态文件
        location /static/ {
            alias /var/www/static/;
            try_files $uri =404;
            expires 30d;
            # 优化：添加 Cache-Control
            add_header Cache-Control "public, must-revalidate";
        }

        # Admin 媒体文件
        location /media {
            alias /var/www/media/;
            try_files $uri =404;
            expires 7d;
            # 优化：添加 Cache-Control
            add_header Cache-Control "public, must-revalidate";
        }

        # Admin 后端应用代理
        location / {
            # 优化：使用 upstream
            proxy_pass http://admin_backend/; 
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 支持 WebSocket (如果 admin 后端需要)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

sudo /usr/local/nginx/sbin/nginx -t

sudo /usr/local/nginx/sbin/nginx -s reload

sudo /usr/local/nginx/sbin/nginx -s stop

```plaintext
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=network.target

[Service]
Type=forking
PIDFile=/var/run/nginx.pid
ExecStartPre=/usr/local/nginx/sbin/nginx -t
ExecStart=/usr/local/nginx/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
KillSignal=SIGQUIT
TimeoutStopSec=5
KillMode=mixed
PrivateTmp=true

[Install]
WantedBy=multi-user.targetnginx.service
```

### 静态资源托管

```plaintext
cp /opt/python-teaching-platform/frontend/web-student/build/client/* /var/www/frontend -r
p /opt/python-teaching-platform/backend/static/* /var/www/static/ -r
p /opt/python-teaching-platform/backend/media/* /var/www/media/ -r
```

_(注：本文档可能包含千问AI生产内容)_