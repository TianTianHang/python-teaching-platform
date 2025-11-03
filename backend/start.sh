#!/bin/bash
set -e

# 定义标记文件路径（放在持久卷目录中，避免容器重启丢失）
FLAG_FILE="/app/static/.first_run_done"

echo "Checking if this is the first run..."

if [ ! -f "$FLAG_FILE" ]; then
    echo "First run detected. Running migrations and collecting static files..."

    # 1. 数据库迁移
    uv run python manage.py migrate --noinput
    uv run python manage.py populate_sample_data
    # 2. 创建超级用户（使用自定义命令）
    uv run python manage.py create_default_superuser

    # 3. 收集静态文件
    uv run python manage.py collectstatic --noinput

    # 创建标记文件（表示首次初始化已完成）
    touch "$FLAG_FILE"
    echo "First run setup completed."
else
    echo "Not first run. Skipping migrations and static collection."
fi

# 3. 启动 Gunicorn（始终执行）
echo "Starting Gunicorn server..."
exec uv run gunicorn --bind 0.0.0.0:8000 core.wsgi:application --workers 4