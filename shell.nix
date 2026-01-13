{ pkgs ? import <nixpkgs> {} }:

let
  postgres = pkgs.postgresql_15;
  dbDir = "./db";
  pgPort = 5432;

  redis = pkgs.redis;
  redisDir = "./redis-data";
  redisPort = 6379;

  micromamba-tarball = pkgs.fetchurl {
    url = "https://micro.mamba.pm/api/micromamba/linux-64/latest";
    sha256 = "sha256-PbzKTEs+ZOKwx8pxITB+aHtsEM5/6InyHVwQ2Bf5g6k=";
  };

  micromamba = pkgs.stdenv.mkDerivation {
    name = "micromamba-latest";
    nativeBuildInputs = [ pkgs.gnutar];
    unpackPhase = ''
      mkdir -p $out/bin
      tar -xvjf ${micromamba-tarball} --strip-components=1 -C $out/bin bin/micromamba
    '';
    installPhase = ''
      chmod +x $out/bin/micromamba
    '';
  };

  # 基础 shell 环境（非 FHS）
  baseShell = pkgs.mkShell {
    allowUnfree = true;
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
      redis
      ngrok
    ];

    buildInputs = with pkgs; [
      typescript
      esbuild
      eslint
      prettier
      postgres
      libarchive
      micromamba
    ];

    shellHook = ''
      echo "✅ JavaScript 全栈开发环境已激活"
      echo "   Node.js: $(node --version)"
      echo ""

      # PostgreSQL
      export PGDATA="$PWD/${dbDir}"
      export PGHOST="$PWD"
      export PGPORT="${toString pgPort}"
      export PGUSER="developer"
      export PGDATABASE="dev"

      # Redis
      export REDIS_PORT="${toString redisPort}"
      export REDIS_DIR="$PWD/${redisDir}"
      export REDIS_CONF="$REDIS_DIR/redis.conf"
      mkdir -p "$REDIS_DIR"
      echo "💡 Redis 配置路径: $REDIS_CONF"
      echo "💡 启动 Redis: ./scripts/start-redis.sh"
      echo ""

      # npm & micromamba
      export NPM_CONFIG_PREFIX="$HOME/.npm-global"
      export PATH="$NPM_CONFIG_PREFIX/bin:$PATH:${postgres}/bin"
      export MAMBA_ROOT_PREFIX=$(pwd)/.mamba
      
      eval "$(${micromamba}/bin/micromamba shell hook --shell bash)"
    '';
  };

in
# 使用 FHS 环境包装
(pkgs.buildFHSEnv {
  name = "js-fullstack-fhs-env";
  targetPkgs = pkgs: (with pkgs; [
    # 必需的基础系统包（模拟标准 Linux 环境）
    bash
    coreutils
    gnugrep
    gawk
    gcc
    glibc
    zlib
    openssl
    ncurses
    util-linux
    procps
    shadow  # 提供 id、groups 等
    findutils
    diffutils
    which
    file
    curl
    wget
    git
    jq
    libarchive
  ]) ++ (baseShell.nativeBuildInputs ++ baseShell.buildInputs);

  runScript = "${pkgs.bashInteractive}/bin/bash";
  profile = ''
    ${baseShell.shellHook}
  '';
}).env