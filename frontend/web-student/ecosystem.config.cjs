module.exports = {
  apps: [
    {
      name: 'react-router-ssr', // 你的应用名
      // 注意：这里直接指定 pnpm 脚本，PM2 会自动识别 shell
      script: 'pnpm',
      args: ['run', 'start'],  // 参数分开写
      cwd:"/opt/web-student",
      // === 集群模式配置 ===
      instances: "max",        // 启动的实例数量，"max" 代表 CPU 核心数
      exec_mode: "cluster",    // 执行模式：cluster (集群) 或 fork (单例)

      // 可选：如果你需要指定环境
      env: {
        PROT: 3000,
        NODE_ENV:"develop",
        API_BASE_URL:"http://localhost:8000/api/v1",
        FILE_STORAGE_DIR:"/var/www/frontend/uploads"
      }
    }
  ]
};