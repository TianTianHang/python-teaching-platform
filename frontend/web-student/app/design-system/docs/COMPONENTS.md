# 组件使用指南

> Python 教育平台前端组件库的使用说明

## 目录

- [布局组件](#布局组件)
- [表单组件](#表单组件)
- [数据展示组件](#数据展示组件)
- [反馈组件](#反馈组件)
- [导航组件](#导航组件)
- [最佳实践](#最佳实践)

---

## 布局组件

### PageContainer

页面主容器组件，提供统一的页面包装器。

**用途:**
- 所有页面的最外层容器
- 提供响应式最大宽度
- 水平居中
- 统一的内外边距

**使用示例:**
```tsx
import { PageContainer } from '~/components/Layout/PageContainer';

export default function MyPage() {
  return (
    <PageContainer maxWidth="lg">
      <h1>页面标题</h1>
      <p>页面内容</p>
    </PageContainer>
  );
}
```

**Props:**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| maxWidth | 'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| 'false' | 'lg' | 内容的最大宽度 |
| disableTopSpacing | boolean | false | 是否禁用顶部间距 |
| disableBottomSpacing | boolean | false | 是否禁用底部间距 |
| sx | SxProps<Theme> | - | 自定义样式 |

### SectionContainer

内容区块容器组件，为页面内提供一致的内容区块间距。

**用途:**
- 页面内内容区块的容器
- 提供垂直间距管理
- 支持卡片和平面两种样式变体

**使用示例:**
```tsx
import { SectionContainer } from '~/components/Layout/SectionContainer';

<SectionContainer spacing="lg" variant="card">
  <Typography variant="h5">区块标题</Typography>
  <p>区块内容</p>
</SectionContainer>
```

**Props:**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| spacing | 'sm' \| 'md' \| 'lg' | 'md' | 垂直间距大小 |
| variant | 'card' \| 'plain' | 'plain' | 样式变体 |
| disableTopSpacing | boolean | false | 是否禁用顶部间距 |
| disableBottomSpacing | boolean | false | 是否禁用底部间距 |

### PageHeader

标准页面头部组件，提供统一的标题、副标题和操作按钮布局。

**用途:**
- 页面的标题区域
- 包含标题和副标题
- 支持面包屑导航
- 支持操作按钮
- 响应式设计

**使用示例:**
```tsx
import { PageHeader } from '~/components/Layout/PageHeader';
import { Button } from '@mui/material';

<PageHeader
  title="我的课程"
  subtitle="继续学习您的编程课程"
  action={<Button variant="contained">添加课程</Button>}
/>
```

**Props:**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | React.ReactNode | - | 页面标题 (必填) |
| subtitle | React.ReactNode | - | 页面副标题 |
| action | React.ReactNode | - | 操作按钮或操作元素 |
| breadcrumbs | React.ReactNode | - | 面包屑导航 |
| titleVariant | 'h1' \| 'h2' \| 'h3' \| 'h4' \| 'h5' \| 'h6' | 'h3' | 标题大小 |
| divider | boolean | false | 是否显示分隔线 |

### LoadingState

统一加载状态组件，提供 Loading、Error、Empty 等状态的统一显示。

**用途:**
- 页面或组件的加载状态
- 错误状态显示
- 空数据状态显示
- 自定义消息和内容

**使用示例:**
```tsx
import { LoadingState } from '~/components/Layout/LoadingState';

// 加载状态
<LoadingState message="加载课程中..." />

// 错误状态
<LoadingState
  variant="error"
  message="加载失败"
  children={<div>错误详情：网络连接失败</div>}
/>

// 空状态
<LoadingState
  variant="empty"
  message="暂无数据"
/>
```

**Props:**
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| variant | 'loading' \| 'error' \| 'empty' | 'loading' | 状态类型 |
| message | string | - | 显示的消息 (必填) |
| children | React.ReactNode | - | 子内容 (主要用于空状态) |
| showSpinner | boolean | true | 是否显示加载动画 |

---

## 表单组件

### FormContainer

使用表单模式创建表单容器。

**使用示例:**
```tsx
import { Button } from '@mui/material';
import { formLayout } from '~/design-system/patterns';

<FormContainer sx={formLayout.container}>
  <Typography variant="h6">登录</Typography>

  <FormControl fullWidth sx={formLayout.field}>
    <InputLabel>用户名</InputLabel>
    <Input />
  </FormControl>

  <FormControl fullWidth sx={formLayout.field}>
    <InputLabel>密码</InputLabel>
    <Input type="password" />
  </FormControl>

  <Box sx={formLayout.actions}>
    <Button variant="outlined">取消</Button>
    <Button variant="contained">登录</Button>
  </Box>
</FormContainer>
```

### FormField

表单字段的标准化包装。

**使用示例:**
```tsx
import { TextField } from '@mui/material';
import { formLayout } from '~/design-system/patterns';

<FormControl fullWidth sx={formLayout.field}>
  <InputLabel>邮箱地址</InputLabel>
  <TextField
    type="email"
    variant="outlined"
    helperText="请输入有效的邮箱地址"
  />
  <Typography variant="caption" color="error">
    {errors.email}
  </Typography>
</FormControl>
```

---

## 数据展示组件

### CardList

使用卡片模式展示数据列表。

**使用示例:**
```tsx
import { cardGrid } from '~/design-system/patterns';

<Box sx={cardGrid.root}>
  {courses.map(course => (
    <Card key={course.id} sx={cardGrid.card}>
      <CardMedia sx={cardGrid.media} image={course.thumbnail} />
      <CardContent sx={cardGrid.content}>
        <Typography variant="h6">{course.title}</Typography>
        <Typography variant="body2" color="text.secondary">
          {course.description}
        </Typography>
      </CardContent>
      <CardActions sx={cardGrid.actions}>
        <Button size="small">查看详情</Button>
        <Button size="small" color="primary">开始学习</Button>
      </CardActions>
    </Card>
  ))}
</Box>
```

### TwoColumnLayout

两列布局模式，适用于带侧边栏的页面。

**使用示例:**
```tsx
import { twoColumnLayout } from '~/design-system/patterns';

<Box sx={[twoColumnLayout.root, theme.breakpoints.down('md')]}>
  <Box sx={twoColumnLayout.sidebar}>
    <Sidebar />
  </Box>
  <Box sx={twoColumnLayout.main}>
    <MainContent />
  </Box>
</Box>
```

---

## 反馈组件

### HoverCard

带有悬停效果的卡片组件。

**使用示例:**
```tsx
import { createHoverEffect } from '~/design-system/patterns';

<Card sx={[flatCard.root, createHoverEffect()]}>
  <CardContent>
    <Typography variant="h6">卡片标题</Typography>
    <Typography variant="body2">悬停时有效果</Typography>
  </CardContent>
</Card>
```

### ActionButton

带有动画效果的操作按钮。

**使用示例:**
```tsx
import { createHoverEffect } from '~/design-system/patterns';

<Button
  sx={[
    {
      py: 1,
      px: 2,
      borderRadius: 2,
      fontWeight: 500,
    },
    createHoverEffect(),
  ]}
>
  操作按钮
</Button>
```

---

## 导航组件

### NavigationLink

使用组件模式的导航链接。

**使用示例:**
```tsx
import { listItem } from '~/design-system/patterns';

<ListItem
  button
  component={Link}
  to="/courses"
  sx={[
    listItem.root,
    isActive && {
      backgroundColor: 'primary.main',
      '& .MuiListItemText-primary': {
        color: 'primary.contrastText',
      },
    },
  ]}
>
  <ListItemText primary="课程" />
</ListItem>
```

### NavigationMenu

导航菜单组件，支持嵌套结构。

**使用示例:**
```tsx
import { getNavItems } from '~/config/navigation';
import { listItem } from '~/design-system/patterns';

{getNavItems().map(item => (
  <ListItem key={item.path} disablePadding>
    <ListItemButton component={Link} to={item.path}>
      <ListItemText primary={item.text} />
    </ListItemButton>
  </ListItem>
))}
```

---

## 最佳实践

### 1. 组合使用布局组件

```tsx
// ✅ 正确的组件组合
<PageContainer maxWidth="lg">
  <PageHeader
    title="课程列表"
    subtitle="发现和学习新的技能"
    action={<Button>添加课程</Button>}
  />

  <SectionContainer spacing="lg" variant="card">
    <CourseList courses={courses} />
  </SectionContainer>
</PageContainer>
```

### 2. 响应式设计

```tsx
// ✅ 使用断点和组件模式
<SectionContainer variant="card">
  <Box sx={{
    display: 'grid',
    gridTemplateColumns: {
      xs: '1fr',
      md: 'repeat(2, 1fr)',
      lg: 'repeat(3, 1fr)',
    },
    gap: spacing.md,
  }}>
    {items.map(item => (
      <ItemCard key={item.id} item={item} />
    ))}
  </Box>
</SectionContainer>
```

### 3. 表单布局

```tsx
// ✅ 使用表单模式
<FormContainer>
  <Typography variant="h6">用户注册</Typography>

  <FormControl sx={formLayout.field}>
    <InputLabel>用户名</InputLabel>
    <Input />
  </FormControl>

  <FormControl sx={formLayout.field}>
    <InputLabel>邮箱</InputLabel>
    <Input type="email" />
  </FormControl>

  <Box sx={formLayout.actions}>
    <Button>注册</Button>
  </Box>
</FormContainer>
```

### 4. 数据展示

```tsx
// ✅ 使用数据展示模式
<Box sx={cardGrid.root}>
  {data.map(item => (
    <Card key={item.id} sx={cardGrid.card}>
      <CardMedia sx={cardGrid.media} image={item.image} />
      <CardContent sx={cardGrid.content}>
        <Typography variant="h6">{item.title}</Typography>
        <Typography variant="body2" color="text.secondary">
          {item.description}
        </Typography>
      </CardContent>
      <CardActions sx={cardGrid.actions}>
        <Button size="small">查看</Button>
      </CardActions>
    </Card>
  ))}
</Box>
```

---

## 示例页面

### 课程列表页面

```tsx
import {
  PageContainer,
  SectionContainer,
  PageHeader,
  LoadingState,
} from '~/components/Layout';
import { Button } from '@mui/material';
import { courseGrid } from '~/design-system/patterns';
import { CourseCard } from '~/components/Course';

export default function CoursesPage() {
  const { data: courses, isLoading, error } = useCourses();

  if (isLoading) {
    return <LoadingState message="加载课程中..." />;
  }

  if (error) {
    return <LoadingState variant="error" message="加载失败" />;
  }

  return (
    <PageContainer maxWidth="lg">
      <PageHeader
        title="课程列表"
        subtitle="发现和学习新的编程技能"
        action={
          <Button variant="contained" startIcon={<AddIcon />}>
            添加课程
          </Button>
        }
      />

      <SectionContainer spacing="lg" variant="card">
        {courses.length === 0 ? (
          <LoadingState
            variant="empty"
            message="暂无课程"
            children={
              <Typography variant="body1">
                您还没有创建任何课程，点击上方按钮开始创建。
              </Typography>
            }
          />
        ) : (
          <Box sx={courseGrid.root}>
            {courses.map(course => (
              <CourseCard key={course.id} course={course} />
            ))}
          </Box>
        )}
      </SectionContainer>
    </PageContainer>
  );
}
```

### 用户资料页面

```tsx
import {
  PageContainer,
  SectionContainer,
  PageHeader,
} from '~/components/Layout';
import { formLayout } from '~/design-system/patterns';
import { TextField, Button } from '@mui/material';

export default function ProfilePage() {
  return (
    <PageContainer maxWidth="md">
      <PageHeader
        title="个人资料"
        subtitle="管理您的个人信息"
      />

      <SectionContainer spacing="lg" variant="card">
        <Box sx={formLayout.container}>
          <Typography variant="h6">基本信息</Typography>

          <FormControl fullWidth sx={formLayout.field}>
            <InputLabel>用户名</InputLabel>
            <TextField value="张三" />
          </FormControl>

          <FormControl fullWidth sx={formLayout.field}>
            <InputLabel>邮箱</InputLabel>
            <TextField value="zhangsan@example.com" type="email" />
          </FormControl>

          <FormControl fullWidth sx={formLayout.field}>
            <InputLabel>手机号</InputLabel>
            <TextField value="13800138000" />
          </FormControl>

          <Box sx={formLayout.actions}>
            <Button variant="outlined">取消</Button>
            <Button variant="contained" type="submit">
              保存更改
            </Button>
          </Box>
        </Box>
      </SectionContainer>
    </PageContainer>
  );
}
```

---

## 组件索引

| 组件 | 路径 | 描述 |
|------|------|------|
| PageContainer | `~/components/Layout/PageContainer.tsx` | 页面主容器 |
| SectionContainer | `~/components/Layout/SectionContainer.tsx` | 内容区块容器 |
| PageHeader | `~/components/Layout/PageHeader.tsx` | 页面头部 |
| LoadingState | `~/components/Layout/LoadingState.tsx` | 加载状态 |

| 模式库 | 路径 | 描述 |
|--------|------|------|
| 表单模式 | `~/design-system/patterns` | 表单布局模式 |
| 卡片模式 | `~/design-system/patterns` | 卡片布局模式 |
| 列表模式 | `~/design-system/patterns` | 列表布局模式 |
| 网格模式 | `~/design-system/patterns` | 网格布局模式 |

通过使用这些组件和模式，您可以快速构建一致、美观且易于维护的用户界面。