# 组件迁移指南

> Python 教育平台前端组件迁移清单和最佳实践

## 目录

- [新组件开发检查清单](#新组件开发检查清单)
- [现有组件重构优先级](#现有组件重构优先级)
- [迁移步骤指南](#迁移步骤指南)
- [迁移示例](#迁移示例)
- [注意事项](#注意事项)

---

## 新组件开发检查清单

每次开发新组件时，请确保完成以下检查项：

### ✅ 基础规范
- [ ] 使用设计标记进行间距 (`import { spacing } from '~/design-system/tokens'`)
- [ ] 使用主题的语义化颜色名称 (`primary.main`, `text.secondary`)
- [ ] 遵循组件结构模板
- [ ] 使用 TypeScript 完整定义 props 类型
- [ ] 添加 JSDoc 注释说明组件用途

### ✅ 样式规范
- [ ] 优先使用 Layout 原始组件 (PageContainer, SectionContainer)
- [ ] 使用组件模式库 (`~/design-system/patterns`)
- [ ] 响应式设计 (使用 MUI 断点)
- [ ] 支持浅色/深色主题切换
- [ ] 避免硬编码值

### ✅ 用户体验
- [ ] 考虑可访问性 (a11y)
- [ ] 添加适当的加载状态
- [ ] 处理错误状态
- [ ] 提供用户反馈
- [ ] 响应式设计 (移动端友好)

### ✅ 开发体验
- [ ] 编写单元测试 (如果适用)
- [ ] 添加到组件文档
- [ ] 确保向后兼容
- [ ] 运行类型检查

**快速检查:**
```tsx
import { spacing, container, borderRadius } from '~/design-system/tokens';
import { cardWithHeader } from '~/design-system/patterns';
import { PageContainer, SectionContainer, PageHeader } from '~/components/Layout';

// ✅ 好的实践
<PageContainer maxWidth="lg">
  <SectionContainer spacing="lg" variant="card">
    <PageHeader title="标题" />
  </SectionContainer>
</PageContainer>
```

---

## 现有组件重构优先级

### 🎯 高优先级 (用户可见，频繁使用)

#### 1. `_layout.home.tsx` (首页 - 489行)
**当前问题:** 使用硬编码间距，缺乏一致的布局模式
**迁移目标:** 使用 PageContainer, SectionContainer, PageHeader
**预期效果:** 代码减少 30%，提升一致性

**迁移前:**
```tsx
<Box sx={{ p: 3 }}>
  <Typography variant="h4" gutterBottom>欢迎回来</Typography>
  <Card sx={{ mb: 4 }}>
    <CardContent>
      {/* 内容 */}
    </CardContent>
  </Card>
</Box>
```

**迁移后:**
```tsx
<PageContainer maxWidth="lg">
  <PageHeader
    title="欢迎回来"
    subtitle="继续您的学习之旅"
  />
  <SectionContainer spacing="lg" variant="card">
    {/* 课程列表 */}
  </SectionContainer>
</PageContainer>
```

#### 2. `_layout.profile.tsx` (个人资料 - 425行)
**当前问题:** 表单布局不一致，缺乏统一间距
**迁移目标:** 使用 formLayout 模式
**预期效果:** 提升表单一致性，改善用户体验

#### 3. `_layout.problems.tsx` (题目页面 - 197行)
**当前问题:** 列表样式不一致，响应式设计不足
**迁移目标:** 使用 listItem 和 cardWithHeader 模式
**预期效果:** 统一列表样式，改善响应式布局

### 🔄 中优先级 (特定功能，使用频率中等)

#### 4. `components/Thread/DiscussionForum.tsx`
**当前问题:** 论坛卡片样式不一致，缺乏分层
**迁移目标:** 使用 cardWithHeader 模式
**预期效果:** 提升论坛视觉层次感

#### 5. `components/Problem/ChoiceProblemCmp.tsx`
**当前问题:** 选项布局不够清晰，间距不统一
**迁移目标:** 使用 SectionContainer 和表单模式
**预期效果:** 改善选择题的用户体验

#### 6. `components/CheckoutModal.tsx`
**当前问题:** 结账流程布局缺乏一致性
**迁移目标:** 使用 formLayout 模式
**预期效果:** 提升支付流程的视觉一致性

### 🔧 低优先级 (不常用，工具组件)

#### 7. Skeleton 组件
**更新需求:** 使用新的设计标记保持一致性
**工作量:** 小

#### 8. 工具组件 (Notification, MarkdownRenderer 等)
**更新需求:** 确保使用主题颜色和设计标记
**工作量:** 最小

---

## 迁移步骤指南

### 第1步：准备工作

1. **备份当前代码**
   ```bash
   git add .
   git commit -m "refactor: 开始布局系统优化"
   ```

2. **创建特性分支**
   ```bash
   git checkout -b refactor/layout-system
   ```

3. **安装依赖 (如果需要)**
   ```bash
   npm install
   ```

### 第2步：理解现有代码

1. **分析组件结构**
   - 识别硬编码的间距值
   - 找出重复的样式模式
   - 确定组件的使用频率

2. **查看相关样式**
   - 检查 sx prop 中的硬编码值
   - 查看内联样式
   - 分析类名使用情况

### 第3步：迁移单个组件

#### 3.1 导入依赖
```tsx
// 导入设计标记
import { spacing, borderRadius } from '~/design-system/tokens';

// 导入布局组件
import { PageContainer, SectionContainer } from '~/components/Layout';

// 导入模式 (如果需要)
import { cardWithHeader } from '~/design-system/patterns';
```

#### 3.2 替换硬编码值
```tsx
// 迁移前
<Card sx={{ p: 3, mb: 4 }}>

// 迁移后
<Card sx={{ p: spacing.lg, mb: spacing.xl }}>
```

#### 3.3 使用布局组件
```tsx
// 迁移前
<Box sx={{ p: 3 }}>
  <h1>标题</h1>
</Box>

// 迁移后
<PageContainer maxWidth="lg">
  <SectionContainer spacing="lg">
    <Typography variant="h4">标题</Typography>
  </SectionContainer>
</PageContainer>
```

#### 3.4 应用组件模式
```tsx
// 迁移前
<Card>
  <CardContent>
    <Typography variant="h6">标题</Typography>
    <Typography>内容</Typography>
  </CardContent>
</Card>

// 迁移后
<Card sx={cardWithHeader.root}>
  <CardHeader sx={cardWithHeader.header}>
    <Typography variant="h6">标题</Typography>
  </CardHeader>
  <CardContent sx={cardWithHeader.content}>
    <Typography>内容</Typography>
  </CardContent>
</Card>
```

### 第4步：测试组件

1. **功能测试**
   - 确保所有原有功能正常
   - 测试交互效果
   - 验证数据展示

2. **样式测试**
   - 测试浅色/深色模式
   - 验证响应式设计
   - 检查视觉一致性

3. **性能测试**
   - 确认无性能回归
   - 检查渲染时间
   - 验证内存使用

### 第5步：提交更改

```bash
git add .
git commit -m "refactor: 优化 [组件名] 布局"
```

---

## 迁移示例

### 示例1：首页迁移

**文件:** `app/routes/_layout.home.tsx`

**迁移前代码 (片段):**
```tsx
<Box sx={{ p: 3 }}>
  {/* 欢迎标题 */}
  <Card sx={{ mb: 4 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom display="flex" alignItems="center">
        <BookIcon sx={{ mr: 2, color: 'primary.main' }} />
        我的课程
      </Typography>
      {/* 更多内容 */}
    </CardContent>
  </Card>

  <Card sx={{ mb: 4 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom display="flex" alignItems="center">
        <QuizIcon sx={{ mr: 2, color: 'primary.main' }} />
        未完成的题目
      </Typography>
      {/* 更多内容 */}
    </CardContent>
  </Card>
</Box>
```

**迁移后代码:**
```tsx
import { PageContainer, SectionContainer, PageHeader } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import { cardWithHeader } from '~/design-system/patterns';
import BookIcon from '@mui/icons-material/Book';
import QuizIcon from '@mui/icons-material/Quiz';

export default function Home({ loaderData }: Route.ComponentProps) {
  return (
    <PageContainer maxWidth="lg">
      {/* 欢迎区域 */}
      <SectionContainer spacing="lg" variant="card">
        <Typography variant="h4" sx={{ mb: spacing.lg }}>
          欢迎回来，学员！
        </Typography>

        {/* 我的课程 */}
        <Card sx={cardWithHeader.root}>
          <CardHeader sx={cardWithHeader.header}>
            <Box display="flex" alignItems="center" gap={spacing.sm}>
              <BookIcon color="primary" />
              <Typography variant="h6">我的课程</Typography>
            </Box>
          </CardHeader>
          <CardContent sx={cardWithHeader.content}>
            {/* 课程列表 */}
          </CardContent>
        </Card>

        {/* 未完成的题目 */}
        <Card sx={cardWithHeader.root}>
          <CardHeader sx={cardWithHeader.header}>
            <Box display="flex" alignItems="center" gap={spacing.sm}>
              <QuizIcon color="primary" />
              <Typography variant="h6">未完成的题目</Typography>
            </Box>
          </CardHeader>
          <CardContent sx={cardWithHeader.content}>
            {/* 题目列表 */}
          </CardContent>
        </Card>
      </SectionContainer>
    </PageContainer>
  );
}
```

### 示例2：个人资料页迁移

**文件:** `app/routes/_layout.profile.tsx`

**迁移前 (片段):**
```tsx
<Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
  <Card sx={{ mb: 3 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>基本信息</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField label="用户名" fullWidth />
        </Grid>
        <Grid item xs={12}>
          <TextField label="邮箱" fullWidth />
        </Grid>
        {/* 更多字段 */}
      </Grid>
    </CardContent>
  </Card>
</Box>
```

**迁移后:**
```tsx
import { PageContainer, SectionContainer } from '~/components/Layout';
import { formLayout } from '~/design-system/patterns';

export default function Profile() {
  return (
    <PageContainer maxWidth="md">
      <SectionContainer spacing="lg" variant="card">
        <Typography variant="h6" sx={formLayout.title}>
          基本信息
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth sx={formLayout.field}>
              <TextField label="用户名" />
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth sx={formLayout.field}>
              <TextField label="邮箱" />
            </FormControl>
          </Grid>
          {/* 更多字段 */}
        </Grid>

        <Box sx={formLayout.actions}>
          <Button variant="outlined">取消</Button>
          <Button variant="contained">保存</Button>
        </Box>
      </SectionContainer>
    </PageContainer>
  );
}
```

---

## 注意事项

### 1. 向后兼容性
- ✅ 新组件使用新规范
- ✅ 现有组件继续工作
- ✅ 混合使用新旧组件
- ✅ 可以随时停止/恢复迁移

### 2. 样式一致性
- ✅ 使用统一的设计标记
- ✅ 遵循组件模式
- ✅ 保持主题一致性
- ✅ 响应式设计

### 3. 性能考虑
- ✅ 组件懒加载
- ✅ 避免过度嵌套
- ✅ 优化渲染性能
- ✅ 减少样式计算

### 4. 可维护性
- ✅ 清晰的代码结构
- ✅ 完整的类型定义
- ✅ 详细的文档注释
- ✅ 一致的命名规范

### 5. 测试策略
- ✅ 单元测试覆盖
- ✅ 视觉回归测试
- ✅ 可访问性测试
- ✅ 响应式测试

---

## 迁移工具和建议

### VSCode Code Snippets

创建代码片段加速迁移：

**PageContainer.snippets**
```json
{
  "Page Container": {
    "prefix": "page-container",
    "body": [
      "<PageContainer maxWidth=\"lg\">",
      "  $0",
      "</PageContainer>"
    ]
  }
}
```

**SectionContainer.snippets**
```json
{
  "Section Container": {
    "prefix": "section-container",
    "body": [
      "<SectionContainer spacing=\"lg\" variant=\"card\">",
      "  $0",
      "</SectionContainer>"
    ]
  }
}
```

### 批量查找替换工具

使用 VSCode 的查找替换功能：

1. **查找硬编码间距:**
   ```
   查找: p:\s*([1-9]|[1-9][0-9]+)px
   替换: p: spacing.$1
   ```

2. **查找卡片的硬编码样式:**
   ```
   查找: sx:\s*\{\s*p:\s*3,\s*mb:\s*4\s*\}
   替换: sx={{ p: spacing.lg, mb: spacing.xl }}
   ```

### Git 提交消息模板

```
refactor: 布局系统迁移 - [组件名称]

- 使用 PageContainer 替代手动包装器
- 应用 SectionContainer 统一间距
- 使用设计标记替换硬编码值
- 添加响应式支持

Co-authored-by: Your Name <your.email@example.com>
```

---

## 总结

通过遵循本迁移指南，您可以：

1. **确保一致性** - 所有组件使用统一的设计系统
2. **提高效率** - 减少重复代码，提高开发速度
3. **改善用户体验** - 统一的视觉风格和交互模式
4. **便于维护** - 清晰的代码结构和文档
5. **支持扩展** - 为未来功能添加做好准备

按照优先级逐步迁移，您可以在保持应用正常运行的同时，逐步提升代码质量和用户体验。记住，迁移是一个持续的过程，可以根据项目进度灵活调整。