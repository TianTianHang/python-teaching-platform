## Why

当前后端通过 YAML 文件导入题目时，`code_template` 中的 Python 代码可能出现缩进问题。YAML 的多行字符串解析会保留额外的缩进空格，导致代码模板显示时格式错乱，影响学生学习体验。需要在代码编辑器显示前对代码进行自动格式化，确保代码风格统一且可读。

## What Changes

- 在 CodeEditor 组件中集成 Python 代码格式化功能
- 使用 @astral-sh/ruff-wasm-web 作为格式化引擎（通过 CDN 加载）
- 在初始加载代码模板时自动格式化
- 支持用户手动触发格式化（可选快捷键）
- 添加格式化错误降级处理（格式化失败时显示原始代码）

## Capabilities

### New Capabilities

### Modified Capabilities
- `code-editor`: 新增代码自动格式化功能要求
  - 初始代码加载时自动格式化
  - 提供手动格式化接口
  - 格式化失败时优雅降级

## Impact

- **依赖**: 前端通过 CDN 加载 @astral-sh/ruff-wasm-web，不增加 bundle 大小
- **组件**: CodeEditor.tsx 需增加格式化逻辑和 WASM 加载管理
- **性能**: 格式化在客户端执行，大文件可能有轻微延迟
- **用户体验**: 代码模板显示更加统一规范
