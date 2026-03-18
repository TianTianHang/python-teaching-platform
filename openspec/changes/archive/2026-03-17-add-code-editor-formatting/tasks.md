## 1. CDN Loading Setup

- [x] 1.1 创建 ruffWasmLoader 工具函数，通过 CDN 加载 @astral-sh/ruff-wasm-web
- [x] 1.2 实现加载状态管理和错误处理（加载失败时降级）
- [x] 1.3 验证 Ruff WASM 格式化功能可用

## 2. Core Formatting Implementation

- [x] 2.1 创建 formatPythonCode utility function，使用 Ruff WASM 进行格式化
- [x] 2.2 添加 formatOnLoad option 到 CodeEditor props interface
- [x] 2.3 实现代码加载时自动格式化（异步，格式化完成后替换内容）
- [x] 2.4 Add manual format trigger (Shift+Alt+F keyboard shortcut)

## 3. Error Handling & Edge Cases

- [x] 3.1 Add try-catch wrapper for formatting errors
- [x] 3.2 Ensure fallback to original code on formatting failure
- [x] 3.3 Handle empty code gracefully
- [x] 3.4 Test with invalid Python syntax

## 4. Integration & Testing

- [x] 4.1 Test with various code templates from backend
- [x] 4.2 Verify cursor position preservation after formatting
- [x] 4.3 Test keyboard shortcut works correctly
- [x] 4.4 Run typecheck to ensure TypeScript types are correct

## 5. Performance & Loading Optimization

- [x] 5.1 实现 WASM 模块懒加载（首次需要格式化时才加载）
- [x] 5.2 添加 WASM 加载超时处理
- [ ] 5.3 测试大文件（>1000行）格式化性能
