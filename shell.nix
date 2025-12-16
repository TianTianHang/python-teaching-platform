# shell.nix
{ pkgs ? import <nixpkgs> {} }:

let
  postgres = pkgs.postgresql_15;
  dbDir = "./db";
  pgPort = 5432;

  redis = pkgs.redis;
  redisDir = "./redis-data";
  redisPort = 6379;
in
pkgs.mkShell {
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
    go
    gopls
    delve
    uv
    redis  # 提供 redis-server 和 redis-cli
  ];

  buildInputs = with pkgs; [
    typescript
    esbuild
    eslint
    prettier
    postgres
  ];

  shellHook = ''
    echo "✅ JavaScript 全栈开发环境已激活"
    echo "   Node.js: $(node --version)"
    echo ""

    #=== PostgreSQL 环境变量（按需启用）===
    export PGDATA="$PWD/${dbDir}"
    export PGHOST="$PWD"
    export PGPORT="${toString pgPort}"
    export PGUSER="developer"
    export PGDATABASE="dev"

    # === Redis 环境变量（始终设置，供外部脚本使用）===
    export REDIS_PORT="${toString redisPort}"
    export REDIS_DIR="$PWD/${redisDir}"
    export REDIS_CONF="$REDIS_DIR/redis.conf"

    # 确保目录存在（避免脚本报错）
    mkdir -p "$REDIS_DIR"

    echo "💡 Redis 配置路径: $REDIS_CONF"
    echo "💡 启动 Redis: ./scripts/start-redis.sh"
    echo ""

    # npm 全局包路径
    export NPM_CONFIG_PREFIX="$HOME/.npm-global"
    export PATH="$NPM_CONFIG_PREFIX/bin:$PATH"
  '';
}