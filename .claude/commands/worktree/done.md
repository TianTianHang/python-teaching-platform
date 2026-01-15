---
description: 合并工作树分支并清理
---

在主目录中执行工作树完成流程：选择并合并工作树分支到 develop，然后清理工作树。

**使用场景**：当您完成工作树开发，希望将变更合并回主分支并清理工作树时使用。

执行以下流程：

1. **环境检查**：

- 确认当前位于主目录中
- 检查主目录工作状态是否清洁
- 验证当前在 develop 分支

2. **工作树分支发现**：

- 自动扫描所有现有的工作树
- 检查每个工作树分支的状态和提交情况
- 显示可合并的工作树分支清单（已有提交且工作目录清洁）

3. **互动式分支选择**：

- 显示工作树分支清单，包含：
- 分支名称
- 最新提交讯息
- 提交时间
- 工作树路径
- 让使用者选择要合并的分支
- 确认合并操作

4. **执行合并流程**：

- 更新 develop 分支：`git pull origin develop`
- 合并选定的工作树分支到 develop
- 推送合并后的 develop 分支到远端
- 执行品质检查确保合并成功

5. **自动清理**：
- 删除已合并的工作树目录
- 移除本地工作树分支
- 显示清理结果

```

**输出范例**：

```
🔍 发现以下可合并的工作树分支：

1. feature/strapi-typescript-optimization
📂 /Users/jackle/workspace/fortuna-feature-strapi-typescript-optimization
📝 feat(typescript): 完成 Strapi v5 TypeScript 优化与 shared 套件建置修正
🕐 2025-07-19 23:41:23

2. feature/workflow-engine-v2
📂 /Users/jackle/workspace/fortuna-feature-workflow-engine-v2
📝 feat(workflow): 实作工作流程执行引擎核心功能
🕐 2025-07-19 15:30:45

请选择要合并的分支 (输入数字):
```

**安全检查**：

- 仅显示已提交且工作目录清洁的工作树
- 合并前确认 develop 分支是最新状态
- 提供合并预览和确认步骤

**注意事项**：

- 必须在主目录中执行（非工作树目录）
- 确保选定的工作树已完成所有开发工作
- 合并后工作树将被自动清理，请确保重要变更已提交