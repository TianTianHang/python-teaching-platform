# 组件样式编写规范

> 为 Python 教育平台前端制定的设计系统样式规范

## 目录

- [何时使用哪种样式方法](#何时使用哪种样式方法)
- [命名约定](#命名约定)
- [组件结构模板](#组件结构模板)
- [最佳实践](#最佳实践)
- [避免的陷阱](#避免的陷阱)
- [示例代码](#示例代码)

---

## 何时使用哪种样式方法

### 使用 `sx` prop 当:
- ✅ 组件特定的样式覆盖
- ✅ 需要主题感知的值 (颜色、间距)
- ✅ 快速的一次性样式
- ✅ 需要响应式值 (断点)

**示例:**
```tsx
<Button
  sx={{
    backgroundColor: 'primary.main',
    '&:hover': {
      backgroundColor: 'primary.dark',
    },
    [theme.breakpoints.down('sm')]: {
      fontSize: '0.875rem',
    },
  }}
>
  按钮文本
</Button>
```

### 使用 `styled()` 当:
- ✅ 可复用组件，具有复杂样式
- ✅ 多个样式变体
- ✅ 在多个文件中共享
- ✅ 需要动态主题支持

**示例:**
```tsx
import { styled } from '@mui/material/styles';

const CustomCard = styled(Card)(({ theme }) => ({
  padding: spacing.lg,
  backgroundColor: theme.palette.background.paper,
  borderRadius: borderRadius.md,
  '&:hover': {
    boxShadow: theme.shadows[2],
  },
}));

// 使用
<CustomCard>内容</CustomCard>
```

### 使用 Tailwind 当:
- ✅ 仅用于工具类 (flex, grid, positioning)
- ✅ 快速原型的间距工具
- ✅ 布局结构 (而非视觉设计)

**示例:**
```tsx
<div className="flex items-center gap-4 p-6">
  <span>内容</span>
</div>
```

### 使用内联样式 (`style={}`) 当:
- ✅ 动态值计算
- ✅ CSS 变量
- ✅ 与样式无关的视觉属性 (如 transform, opacity)

**避免:**
- ❌ 固定颜色值 (`backgroundColor: '#5B4DFF'`)
- ❌ 硬编码间距 (`padding: '24px'`)
- ❌ 复杂逻辑使用内联样式

---

## 命名约定

### 间距 (Spacing)
使用设计标记系统:

```tsx
// ❌ 硬编码值
sx={{ padding: '24px', margin: '16px 0' }}

// ✅ 使用设计标记
import { spacing } from '~/design-system/tokens';

sx={{ p: spacing.lg, my: spacing.md }}
```

### 颜色 (Colors)
使用语义化颜色名称:

```tsx
// ❌ 直接使用色值
sx={{ color: '#5B4DFF', backgroundColor: '#FFFFFF' }}

// ✅ 使用主题颜色
sx={{ color: 'primary.main', backgroundColor: 'background.paper' }}

// ✅ 特殊状态
sx={{ color: 'error.main', borderColor: 'success.light' }}
```

### 命名变量
使用清晰的描述性名称:

```tsx
// ❌ 模糊的命名
const styles = { root: { p: 16 } };

// ✅ 清晰的命名
const styles = {
  root: { padding: spacing.lg },
  container: { marginBottom: spacing.xl },
  content: { color: 'text.secondary' },
};
```

### 响应式断点
使用主题断点:

```tsx
// ✅ 使用主题断点
sx={{
  display: 'flex',
  [theme.breakpoints.down('sm')]: {
    flexDirection: 'column',
  },
  [theme.breakpoints.up('md')]: {
    alignItems: 'center',
  },
}}
```

---

## 组件结构模板

### 基础组件模板

```tsx
import { forwardRef } from 'react';
import { Box, type BoxProps, type SxProps, type Theme } from '@mui/material';
import { spacing, borderRadius } from '~/design-system/tokens';

interface MyComponentProps extends Omit<BoxProps, 'sx'> {
  children?: React.ReactNode;
  /**
   * 自定义样式
   */
  sx?: SxProps<Theme>;
  /**
   * 组件变体
   * @default 'default'
   */
  variant?: 'default' | 'secondary';
}

export const MyComponent = forwardRef<HTMLDivElement, MyComponentProps>(
  ({ children, variant = 'default', sx, ...props }, ref) => {
    // 1. 钩子和变量
    const theme = useTheme();

    // 2. 样式计算
    const rootStyles: SxProps<Theme> = {
      // 基础样式
      display: 'flex',
      alignItems: 'center',
      gap: spacing.md,

      // 变体样式
      ...(variant === 'secondary' && {
        color: 'secondary.main',
        borderColor: 'secondary.main',
        borderWidth: 1,
        borderStyle: 'solid',
      }),

      // 合并自定义样式
      ...sx,
    };

    // 3. 事件处理
    const handleClick = () => {
      // 事件处理逻辑
    };

    // 4. 渲染
    return (
      <Box
        ref={ref}
        sx={rootStyles}
        onClick={handleClick}
        {...props}
      >
        {children}
      </Box>
    );
  }
);

MyComponent.displayName = 'MyComponent';
```

### 复杂组件模板

```tsx
import { forwardRef } from 'react';
import {
  Box,
  Button,
  type ButtonProps,
  type SxProps,
  type Theme,
} from '@mui/material';
import { spacing, borderRadius } from '~/design-system/tokens';

interface ComplexComponentProps {
  /**
   * 组件标题
   */
  title: string;
  /**
   * 按钮点击处理函数
   */
  onButtonClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
  /**
   * 按钮配置
   */
  buttonProps?: ButtonProps;
  /**
   * 自定义样式
   */
  sx?: SxProps<Theme>;
  /**
   * 禁用状态
   * @default false
   */
  disabled?: boolean;
}

export const ComplexComponent = forwardRef<HTMLDivElement, ComplexComponentProps>(
  ({ title, onButtonClick, buttonProps, sx, disabled = false }, ref) => {
    // 1. 钩子和变量
    const theme = useTheme();

    // 2. 样式对象
    const rootStyles: SxProps<Theme> = {
      // 基础样式
      backgroundColor: 'background.paper',
      borderRadius: borderRadius.md,
      padding: spacing.lg,
      minHeight: 200,

      // 禁用状态
      ...(disabled && {
        opacity: 0.6,
        pointerEvents: 'none',
      }),

      // 合并自定义样式
      ...sx,
    };

    // 3. 事件处理
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled) {
        onButtonClick(e);
      }
    };

    // 4. 渲染
    return (
      <Box ref={ref} sx={rootStyles}>
        {/* 标题 */}
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>

        {/* 描述 */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: spacing.lg }}>
          这是组件描述文本
        </Typography>

        {/* 按钮 */}
        <Button
          onClick={handleClick}
          variant="contained"
          disabled={disabled}
          {...buttonProps}
        >
          按钮文本
        </Button>
      </Box>
    );
  }
);

ComplexComponent.displayName = 'ComplexComponent';
```

---

## 最佳实践

### 1. 优先使用设计标记

```tsx
// ✅ 使用设计标记
import { spacing, container } from '~/design-system/tokens';

<PageContainer maxWidth="lg">
  <SectionContainer spacing="lg">
    <Box sx={{ p: spacing.md, mb: spacing.lg }}>
      内容
    </Box>
  </SectionContainer>
</PageContainer>
```

### 2. 响应式设计

```tsx
// ✅ 使用主题断点
sx={{
  display: 'grid',
  gridTemplateColumns: {
    xs: '1fr',
    md: 'repeat(2, 1fr)',
    lg: 'repeat(3, 1fr)',
  },
  gap: spacing.md,
}}
```

### 3. 主题感知

```tsx
// ✅ 使用主题颜色
sx={{
  color: (theme) => {
    if (theme.palette.mode === 'dark') {
      return '#FFFFFF';
    }
    return '#000000';
  },
}}
```

### 4. 状态管理

```tsx
// ✅ 使用状态样式
const [isHovered, setIsHovered] = React.useState(false);

sx={{
  backgroundColor: isHovered ? 'primary.light' : 'transparent',
  transition: transitions.fast,
}}
```

### 5. 组件组合

```tsx
// ✅ 使用布局组件
<SectionContainer spacing="md">
  <PageHeader
    title="我的课程"
    subtitle="继续学习您的编程课程"
    action={<Button>添加课程</Button>}
  />
  <Card>
    <CardContent>
      内容
    </CardContent>
  </Card>
</SectionContainer>
```

---

## 避免的陷阱

### 1. 硬编码值

```tsx
// ❌ 硬编码颜色和间距
sx={{ backgroundColor: '#5B4DFF', padding: '24px' }}

// ✅ 使用主题和标记
sx={{ backgroundColor: 'primary.main', p: spacing.lg }}
```

### 2. 混合样式方法

```tsx
// ❌ 混合不同的样式方法
<Box
  style={{ padding: '24px' }}
  className="bg-white"
  sx={{ color: 'primary.main' }}
>

</Box>

// ✅ 统一使用 sx prop
sx={{
  p: spacing.lg,
  color: 'primary.main',
}}
```

### 3. 过度嵌套

```tsx
// ❌ 过度嵌套的选择器
sx={{
  '& .MuiCardContent-root .MuiTypography-body2': {
    color: 'text.secondary',
  },
}}

// ✅ 直接使用类名或 sx
<CardContent>
  <Typography sx={{ color: 'text.secondary' }}>内容</Typography>
</CardContent>
```

### 4. 忽视可访问性

```tsx
// ❌ 忽视可访问性
<Button sx={{ width: 100 }}>按钮</Button>

// ✅ 提供合适的间距和尺寸
<Button sx={{ minWidth: 120, py: 1 }}>按钮</Button>
```

---

## 示例代码

### 卡片组件示例

```tsx
import { forwardRef } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  type CardHeaderProps,
  type SxProps,
  type Theme,
} from '@mui/material';
import { spacing, borderRadius } from '~/design-system/tokens';
import { cardWithHeader } from '~/design-system/patterns';

interface CourseCardProps {
  title: string;
  description?: string;
  headerAction?: React.ReactNode;
  sx?: SxProps<Theme>;
}

export const CourseCard = forwardRef<HTMLDivElement, CourseCardProps>(
  ({ title, description, headerAction, sx }, ref) => {
    return (
      <Card
        ref={ref}
        sx={[
          {
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: borderRadius.md,
            transition: transitions.fast,
            '&:hover': {
              boxShadow: 2,
              transform: 'translateY(-2px)',
            },
          },
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
      >
        {/* 使用卡片头部模式 */}
        <CardHeader
          title={title}
          sx={{
            ...cardWithHeader.header,
            '& .MuiCardHeader-content': {
              ...cardWithHeader.title,
              gap: spacing.sm,
            },
          }}
          action={headerAction}
        />

        <CardContent sx={cardWithHeader.content}>
          {description && (
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  }
);
```

### 列表组件示例

```tsx
import { forwardRef } from 'react';
import {
  ListItem,
  ListItemText,
  type SxProps,
  type Theme,
} from '@mui/material';
import { spacing } from '~/design-system/tokens';
import { listItem } from '~/design-system/patterns';
import { isActivePath } from '~/config/navigation';

interface NavigationItemProps {
  text: string;
  path: string;
  currentPath: string;
  onClick?: () => void;
  sx?: SxProps<Theme>;
}

export const NavigationItem = forwardRef<HTMLDivElement, NavigationItemProps>(
  ({ text, path, currentPath, onClick, sx }, ref) => {
    const isActive = isActivePath(currentPath, path);

    return (
      <ListItem
        ref={ref}
        disablePadding
        sx={[
          listItem.root,
          ...(isActive && [
            {
              backgroundColor: 'primary.main',
              '& .MuiListItemText-primary': {
                color: 'primary.contrastText',
              },
            },
          ]),
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
        onClick={onClick}
      >
        <ListItemText
          primary={text}
          sx={listItem.content}
        />
      </ListItem>
    );
  }
);
```

---

## 代码审查清单

### 创建新组件时检查:

- [ ] 使用设计标记进行间距
- [ ] 使用主题的语义化颜色名称
- [ ] 遵循组件结构模板
- [ ] 适当使用 Layout 原始组件
- [ ] 使用 TypeScript 文档化 props
- [ ] 添加必要的 JSDoc 注释
- [ ] 考虑响应式设计
- [ ] 测试浅色和深色模式
- [ ] 确保可访问性
- [ ] 添加示例到文档

### 修改现有组件时检查:

- [ ] 检查是否有硬编码值需要替换
- [ ] 确保样式一致性
- [ ] 验证响应式行为
- [ ] 测试所有主题变体
- [ ] 运行自动化测试 (如果有)

---

## 贡献指南

如果你想要:

1. **添加新的设计标记**
   - 在 `/app/design-system/tokens/index.ts` 中添加
   - 添加类型定义
   - 更新文档说明

2. **创建新的组件模式**
   - 在 `/app/design-system/patterns/index.ts` 中添加
   - 提供详细的使用示例
   - 添加到本文档

3. **改进现有样式**
   - 遵循本文档的最佳实践
   - 确保向后兼容性
   - 更新相关文档

通过遵循这些规范，我们将保持 Python 教育平台前端的一致性和可维护性。