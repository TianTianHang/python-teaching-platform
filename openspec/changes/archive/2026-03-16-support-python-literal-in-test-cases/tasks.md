## 1. 核心实现

- [x] 1.1 修改 `backend/courses/services.py` 中的 `generate_judge0_code()` 函数，添加 `ast.literal_eval()` 解析逻辑
- [x] 1.2 确保解析顺序：JSON 优先 → Python 字面量 → Fallback 分割
- [x] 1.3 添加必要的 import 语句（`import ast`）

## 2. 测试验证

- [x] 2.1 编写单元测试验证 JSON 格式解析（向后兼容）
- [x] 2.2 编写单元测试验证 Python 元组格式解析
- [x] 2.3 编写单元测试验证 Python 集合、布尔值、None 等格式
- [x] 2.4 编写测试验证安全性（拒绝恶意代码注入）
- [x] 2.5 运行现有测试套件确保无回归

## 3. 文档更新

- [x] 3.1 更新题目导入文档，说明支持的测试用例格式
- [x] 3.2 在示例中添加 Python 字面量格式的使用说明
