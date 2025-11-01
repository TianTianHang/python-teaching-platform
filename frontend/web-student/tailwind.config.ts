// tailwind.config.ts
module.exports = {
  mode: 'jit', // 启用 JIT 模式
  purge: [
    './public/**/*.html', // HTML 文件路径
    './app/**/*.{js,jsx,ts,tsx,vue}', // Vue/React/TS 文件路径
    // 根据你的项目结构调整路径
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}