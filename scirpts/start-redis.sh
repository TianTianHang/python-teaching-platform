#!/bin/sh
# scripts/start-redis.sh
# 手动启动 Redis，依赖 shell.nix 中设置的环境变量

set -e

if [ -z "$REDIS_PORT" ] || [ -z "$REDIS_DIR" ] || [ -z "$REDIS_CONF" ]; then
  echo "❌ 错误：请先运行 'nix-shell' 以设置 Redis 环境变量。"
  exit 1
fi

# 生成配置文件（如果不存在）
if [ ! -f "$REDIS_CONF" ]; then
  echo "📝 生成 Redis 配置: $REDIS_CONF"
  cat > "$REDIS_CONF" <<EOF
port $REDIS_PORT
dir $REDIS_DIR
bind 127.0.0.1
daemonize no
loglevel notice
logfile ""
EOF
fi

echo "🚀 启动 Redis 服务..."
echo "   端口: $REDIS_PORT"
echo "   数据目录: $REDIS_DIR"
echo "   配置文件: $REDIS_CONF"
echo ""

exec redis-server "$REDIS_CONF"