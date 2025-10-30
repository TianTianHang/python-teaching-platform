#!/bin/bash

# 确保所有后续命令都在失败时退出
set -e

echo "Running Django checks and migrations..."
# 这是一个可选但推荐的步骤：等待数据库就绪（如果需要）
# 生产环境中建议使用 'wait-for-it.sh' 或类似工具来等待 DB
# 这里我们跳过等待，但通常需要这一步。

# 1. 运行数据库迁移 (可选，但通常在启动时执行) 
uv run python manage.py migrate --noinput

# 2. 收集静态文件
# 假设环境变量 (如 DEBUG, SECRET_KEY, DATABASE_URL) 已经通过 docker-compose 传入
echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

# 3. 启动 Gunicorn 服务器
echo "Starting Gunicorn server..."
# 使用 exec 确保 gunicorn 成为 PID 1，以便接收信号
exec uv run gunicorn --bind 0.0.0.0:8000 core.wsgi:application
