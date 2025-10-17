# shell.nix
{ pkgs ? import <nixpkgs> {} }:

let
  # PostgreSQL 配置
  postgres = pkgs.postgresql_15;  # 可根据需要改为 postgresql_14/16
  dbDir = "./db";                 # 数据库存放目录（项目内）
  port = 5432;                    # PostgreSQL 端口
in
pkgs.mkShell {
  # 基础开发工具
  nativeBuildInputs = with pkgs; [
    nodejs_20
    pnpm
    yarn
    git
    coreutils
    which
    jq
    curl
    wget
    # Go 语言
    go
    gopls        # Go 语言服务器（用于 LSP，VS Code 等）
    delve        # Go 调试器

    # uv: 超快的 Python 工具（pip / venv / pip-tools 替代品）
    uv


  ];

  # 开发依赖（全局 CLI 工具）
  buildInputs = with pkgs; [
    # TypeScript & 构建工具
    typescript
    esbuild
    

    

    # 代码质量
    eslint
    prettier

    # PostgreSQL 客户端（psql, createdb 等）
    postgres

    # 如需 SQLite 可取消注释：
    # sqlite
  ];

  # 启动时自动初始化并运行 PostgreSQL
  shellHook = ''
    echo "✅ JavaScript 全栈开发环境已激活"
    echo "   Node.js: $(node --version)"
    echo "   pnpm:    $(pnpm --version 2>/dev/null || echo 'not used')"
    echo ""

    # === PostgreSQL 自动启动 ===
    export PGDATA="$PWD/${dbDir}"
    export PGHOST="$PWD"           # 使用 Unix socket（更安全）
    export PGPORT="${toString port}"
    export PGUSER="developer"
    export PGDATABASE="dev"

    # 创建 db 目录（如果不存在）
    mkdir -p "$PGDATA"

    # 初始化数据库（仅首次）
    if [ ! -f "$PGDATA/PG_VERSION" ]; then
      echo "🔄 初始化 PostgreSQL 数据目录到 $PGDATA ..."
      ${postgres}/bin/initdb --auth=trust --username="$PGUSER" --encoding=UTF8 --locale=C > /dev/null
      echo "✅ PostgreSQL 初始化完成"
    fi

    # 启动 PostgreSQL（如果未运行）
    if ! ${postgres}/bin/pg_ctl -D "$PGDATA" status > /dev/null 2>&1; then
      echo "🚀 启动 PostgreSQL 服务（端口: $PGPORT，数据目录: $PGDATA）..."
      ${postgres}/bin/pg_ctl -D "$PGDATA" -o "-k $PWD -p $PGPORT" start > /dev/null
      echo "✅ PostgreSQL 已启动"
    else
      echo "ℹ️ PostgreSQL 已在运行"
    fi

    echo "💡 使用 psql 连接数据库：psql"
    echo "📁 数据文件保存在: $PGDATA"
    echo ""

    # 退出 shell 时自动停止 PostgreSQL
    function _cleanup_postgres() {
      echo "🛑 正在停止 PostgreSQL..."
      ${postgres}/bin/pg_ctl -D "$PGDATA" stop -m fast > /dev/null
    }
    trap _cleanup_postgres EXIT

    # npm 全局包路径（避免权限问题）
    export NPM_CONFIG_PREFIX="$HOME/.npm-global"
    export PATH="$NPM_CONFIG_PREFIX/bin:$PATH"
    
  '';
}