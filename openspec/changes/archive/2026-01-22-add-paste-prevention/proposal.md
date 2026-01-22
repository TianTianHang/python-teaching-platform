# Change: Add Paste Prevention in Code Editor

## Why

在教学场景中，需要确保学生真正理解和掌握编程概念，而不是简单地复制粘贴代码。禁止粘贴功能可以：
- 促使学生手动输入代码，加深对语法和结构的理解
- 防止学生从外部来源直接复制答案
- 适用于特定的练习或考试场景

## What Changes

- **BREAKING**: CodeEditor 组件新增 `disablePaste` 属性来控制是否允许粘贴
- 当 `disablePaste={true}` 时，编辑器将拦截所有粘贴操作（鼠标右键菜单、键盘快捷键 Ctrl+V）
- 添加用户友好的提示消息，告知粘贴功能已禁用
- 保留其他编辑功能（复制、剪切、手动输入）的正常使用
- 该功能默认关闭，向后兼容现有使用方式

## Impact

- Affected specs: `code-editor` (MODIFIED)
- Affected code:
  - `frontend/web-student/app/components/CodeEditor.tsx` (新增属性和事件拦截逻辑)
  - 使用 CodeEditor 组件的页面可选择性地启用此功能
