## Overview

本变更为纯技术架构迁移，不涉及功能需求变更。

### 迁移范围

- `_layout.problems.tsx` - 题目列表页
- `problems.$problemId/route.tsx` - 题目详情页  
- `problems.$problemId.description.tsx` - 题目描述页
- `problems.$problemId.submissions.tsx` - 提交记录页
- `problems.$problemId.check.tsx` - 代码检查页
- `problems.$problemId.save_draft.tsx` - 保存草稿页
- `problems.$problemId.mark_as_solved.tsx` - 标记完成页
- `problems.$problemId.latest_draft.tsx` - 最新草稿页

### 行为变更

仅数据获取方式变更：
- **之前**: 服务器端 loader + session 验证
- **之后**: 客户端 useEffect + JWT token

用户可见行为保持一致：
- 相同的数据展示
- 相同的交互流程
- 相同的错误处理

因此无需创建新的 requirements 或修改现有 requirements。