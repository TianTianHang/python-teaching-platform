## Context

当前 CodeEditor 组件使用 CodeMirror 6 作为编辑器，代码模板从后端通过 YAML 文件导入。由于 YAML 多行字符串解析的特性，代码缩进可能出现问题，导致显示时代码格式不统一。

现有技术栈：
- CodeMirror 6 作为代码编辑器
- React 19 + TypeScript
- @codemirror/lang-python 提供 Python 语法支持

## Goals / Non-Goals

**Goals:**
- 在代码编辑器中集成 Python 代码格式化功能
- 使用 @astral-sh/ruff-wasm-web 作为格式化引擎（通过 CDN 加载）
- 在初始加载代码时自动格式化
- 支持用户手动触发格式化
- 格式化失败时优雅降级，不影响用户体验

**Non-Goals:**
- 不支持其他语言（如 JavaScript）的格式化
- 不修改后端数据存储（只在展示层格式化）
- 不提供自定义格式化配置界面（使用默认配置）

## Decisions

### Decision: 使用 @astral-sh/ruff-wasm-web 作为格式化引擎（CDN 加载）
**Rationale:**
- Ruff 是高性能的 Python 代码格式化和 lint 工具，兼容 Black 风格
- @astral-sh/ruff-wasm-web 是 Ruff 的 WebAssembly 版本，可在浏览器运行
- 通过 CDN 加载，不增加项目 bundle 大小
- 支持代码格式化（format）功能，可处理各种缩进问题
- 官方维护，活跃更新

**CDN 加载方案：**
- 使用 jsDelivr CDN: `https://cdn.jsdelivr.net/npm/@astral-sh/ruff-wasm-web@latest`
- 动态加载 WASM 模块，按需初始化
- 加载失败时优雅降级到无格式化模式

**Alternatives considered:**
- @prettier/plugin-python：已不再维护，且依赖较多
- 自定义缩进修复函数：简单但不够完善，无法处理复杂格式问题
- 后端格式化：需要修改数据存储和导入流程，影响范围大

### Decision: 异步格式化
**Rationale:**
- Ruff WASM 格式化是 CPU 密集型操作
- WASM 执行天然异步，不会阻塞主线程 UI
- 对于小代码片段，异步处理不会明显影响用户体验

### Decision: 格式化失败时静默降级
**Rationale:**
- 用户不应因格式化错误而无法编辑代码
- 语法错误的代码无法格式化是正常情况
- 静默降级确保编辑器始终可用

### Decision: 在 CodeEditor 组件内部处理格式化
**Rationale:**
- 格式化是展示层功能，不应放在 useCodeDraft hook
- CodeEditor 是代码显示的唯一入口，集中处理最合理
- 不修改现有数据流和状态管理

## Risks / Trade-offs

**[Risk]** CDN 加载失败时无法使用格式化功能
**Mitigation:** 实现加载超时和失败降级机制，网络问题时不影响编辑器正常使用

**[Risk]** 格式化操作可能延迟代码显示
**Mitigation:** 使用异步格式化，显示原始代码的同时在后台格式化，完成后平滑切换

**[Risk]** 格式化后的代码与用户预期风格不一致
**Mitigation:** Ruff 使用 Black 兼容风格，这是 Python 社区标准，接近 PEP 8

**[Risk]** 语法错误的代码无法格式化
**Mitigation:** 优雅降级，显示原始代码，不报错

## Migration Plan

无需迁移步骤，这是纯前端功能增强：
1. 实现 Ruff WASM CDN 加载工具函数
2. 修改 CodeEditor 组件，集成格式化功能
3. 测试各种代码模板
4. 部署

## Open Questions

- 是否需要提供格式化配置选项（如缩进空格数）？
- 是否需要显示格式化状态指示器？
- 大文件（>1000行）的格式化性能如何？
