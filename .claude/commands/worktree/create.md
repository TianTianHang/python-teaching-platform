---
argument-hint: [name]
description: 创建新的 Git Worktree
allowed-tools: Bash(git worktree add:*)
---

### `/worktree-create [name]`  
**功能**：创建新的 Git Worktree 并自动配置完整的共享开发环境  

---

#### **参数说明**
- `name`：功能描述或识别名称（必填）  
  - 支持中文或英文输入  
  - AI 将自动判断类型并标准化命名  

---

#### **执行流程**

1. **智能解析与命名优化**  
   - **类型判断**：
     - 含「修复」「fix」「bug」「hotfix」→ `hotfix/...`  
     - 其他 → `feature/...`（默认）  
   - **中文转英文**：
     - 语义准确翻译为英文短语  
     - 转换为 **kebab-case**（小写 + 连字符）  
     - 遵循 **4–6 个单词** 的描述性命名原则  
     - 示例：  
       - `用户仪表盘重构` → `feature/user-dashboard-redesign`  
       - `支付回调失败修复` → `hotfix/payment-callback-failure-fix`

2. **安全创建工作树**  
   - 检查是否已存在同名分支或工作树目录  
   - 执行：  
     ```bash
     git worktree add ../<branch-name> -b <branch-name>
     ```

3. **自动配置共享开发环境**  
   在新工作树中创建以下**符号链接**，确保与主工作区共享关键环境文件和依赖：

   **后端（`backend/`）**：
   ```bash
   ln -sf $(realpath ../../main/backend/.env) backend/.env
   ln -sf $(realpath ../../main/backend/.keys) backend/.keys
   ln -sf $(realpath ../../main/backend/.venv) backend/.venv
   ln -sf $(realpath ../../main/backend/media) backend/media
   ```

   **前端（`frontend/web-student/`）**：
   ```bash
   ln -sf $(realpath ../../../main/frontend/web-student/.env) frontend/web-student/.env
   ln -sf $(realpath ../../../main/frontend/web-student/node_modules) frontend/web-student/node_modules
   ```

   > ✅ **说明**：  
   > - 假设主工作区位于 `../main`（相对于新工作树的同级目录）  
   > - 使用 `realpath` 确保链接绝对路径正确，避免嵌套问题  
   > - 若主工作区路径不同，可动态探测或提示用户确认

4. **生成完成报告**  
   输出包含以下信息：
   - 📝 原始输入：`“权限验证修复”`  
   - 🔧 转换结果：`hotfix/permission-validation-fix`  
   - 🌳 工作树路径：`../hotfix-permission-validation-fix`  
   - 🌿 分支名称：`hotfix/permission-validation-fix`  
   - 🔗 环境链接：已配置 backend & frontend 共享依赖  