

set -euo pipefail  # 更安全的脚本执行


# 创建数据目录（如果不存在）
mkdir -p "$PGDATA"

# 初始化数据库（仅首次）
if [ ! -f "$PGDATA/PG_VERSION" ]; then
  echo "🔄 初始化 PostgreSQL 数据目录到 $PGDATA ..."
  initdb -D "$PGDATA" --auth=trust --username="$PGUSER" --encoding=UTF8 --locale=C > /dev/null
  echo "✅ PostgreSQL 初始化完成"
fi

# 启动 PostgreSQL（如果未运行）
if ! pg_ctl -D "$PGDATA" status > /dev/null 2>&1; then
  echo "🚀 启动 PostgreSQL 服务（端口: $PGPORT，数据目录: $PGDATA）..."
  pg_ctl -D "$PGDATA" -o "-k $PGHOST -p $PGPORT" start 
  echo "✅ PostgreSQL 已启动"
else
  echo "ℹ️ PostgreSQL 已在运行"
fi
# 检查 dev 数据库是否存在，不存在则创建
if ! psql -lqt | cut -d \| -f 1 | grep -qw "^dev$"; then
  echo "🆕 创建数据库: dev"
  createdb "dev"
fi
echo "💡 使用 psql 连接数据库：psql"
echo "📁 数据文件保存在: $PGDATA"
echo ""