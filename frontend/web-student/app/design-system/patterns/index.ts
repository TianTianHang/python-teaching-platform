/**
 * Component Patterns - 组件模式库
 *
 * 这里存储可复用的组件模式，这些模式组合设计标记和主题设置，
 * 为常见布局提供一致的外观和行为。
 *
 * @see https://designsystemsrepo.com/components
 */

import { type SxProps, type Theme } from '@mui/material';
import { spacing, borderRadius } from '../tokens';

// =============================================================================
// 卡片模式 (Card Patterns)
// =============================================================================

/**
 * 卡片头部模式
 * 用于带有标题、描述和操作按钮的卡片
 */
export const cardWithHeader = {
  /**
   * 卡片根容器样式
   */
  root: {
    p: spacing.lg,
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.lg,
  },

  /**
   * 卡片头部样式
   */
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    mb: spacing.md,
  },

  /**
   * 标题区域样式
   */
  title: {
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.sm,
  },

  /**
   * 操作按钮区域样式
   */
  actions: {
    display: 'flex',
    gap: spacing.sm,
    mt: spacing.md,
  },

  /**
   * 卡片内容样式
   */
  content: {
    flex: 1,
  },

  /**
   * 卡片底部样式
   */
  footer: {
    pt: spacing.md,
    borderTop: `1px solid`,
    borderColor: 'divider',
  },
} as const;

/**
 * 平面卡片模式
 * 用于无边框、无阴影的卡片
 */
export const flatCard = {
  root: {
    p: spacing.lg,
    borderRadius: borderRadius.sm,
    bgcolor: 'background.paper',
  },
} as const;

/**
 * 分组卡片模式
 * 用于展示相关数据的分组
 */
export const groupedCard = {
  /**
   * 根容器
   */
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: 0, // 组合时添加
  },

  /**
   * 分组头部
   */
  groupHeader: {
    p: spacing.md,
    borderBottom: `1px solid ${({
      palette,
    }: Theme) => palette.divider}`,
    bgcolor: 'background.paper',
    borderRadius: borderRadius.md,
    borderRadiusBottomLeft: 0,
    borderRadiusBottomRight: 0,
  },

  /**
   * 分组内容
   */
  groupContent: {
    p: spacing.lg,
  },

  /**
   * 分组分隔线
   */
  groupDivider: {
    borderBottom: `1px solid ${({
      palette,
    }: Theme) => palette.divider}`,
  },
} as const;

// =============================================================================
// 列表模式 (List Patterns)
// =============================================================================

/**
 * 列表项模式
 * 用于标准列表项的布局
 */
export const listItem = {
  /**
   * 根容器样式
   */
  root: {
    p: spacing.sm,
    display: 'flex',
    alignItems: 'center',
    gap: spacing.sm,
    transition: 'all 0.2s ease',
    '&:hover': {
      bgcolor: 'action.hover',
      borderRadius: borderRadius.sm,
    },
  },

  /**
   * 左侧内容区域 (图标、复选框等)
   */
  leading: {
    flexShrink: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  /**
   * 主要内容区域 (标题、描述等)
   */
  content: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: 0, // 文本使用 Typography 的 gutterBottom
  },

  /**
   * 右侧操作区域 (按钮、菜单等)
   */
  actions: {
    flexShrink: 0,
    display: 'flex',
    alignItems: 'center',
    gap: spacing.sm,
  },

  /**
   * 密集型列表项 (优化空间)
   */
  dense: {
    p: { xs: spacing.sm, sm: 0 },
    gap: { xs: spacing.sm, sm: 0 },
  },
} as const;

/**
 * 带边框列表项模式
 * 用于需要视觉分隔的列表项
 */
export const borderedListItem = {
  /**
   * 基础样式
   */
  ...listItem,

  /**
   * 边框配置
   */
  root: {
    ...listItem.root,
    p: spacing.md,
    borderBottom: `1px solid ${({
      palette,
    }: Theme) => palette.divider}`,
    '&:last-child': {
      borderBottom: 'none',
    },
  },
} as const;

// =============================================================================
// 表单模式 (Form Patterns)
// =============================================================================

/**
 * 表单容器模式
 * 用于创建居中、有最大宽度的表单布局
 */
export const formLayout = {
  /**
   * 表单容器
   */
  container: {
    maxWidth: 600,
    mx: 'auto',
    p: spacing.lg,
    bgcolor: 'background.paper',
    borderRadius: borderRadius.md,
    boxShadow: 1,
  },

  /**
   * 表单组
   */
  field: {
    mb: spacing.md,
    '&:last-child': {
      mb: 0,
    },
  },

  /**
   * 表单字段容器 (包含标签和输入)
   */
  fieldContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.sm,
  },

  /**
   * 标签样式
   */
  label: {
    display: 'block',
    mb: spacing.sm / 2,
    fontWeight: 500,
  },

  /**
   * 错误消息样式
   */
  error: {
    mt: spacing.sm / 2,
    fontSize: '0.875rem',
    color: 'error.main',
  },

  /**
   * 助文本样式
   */
  helperText: {
    mt: spacing.sm / 2,
    fontSize: '0.875rem',
    color: 'text.secondary',
  },

  /**
   * 按钮组
   */
  actions: {
    display: 'flex',
    gap: spacing.sm,
    justifyContent: 'flex-end',
    mt: spacing.lg,
    pt: spacing.lg,
    borderTop: `1px solid ${({
      palette,
    }: Theme) => palette.divider}`,
  },

  /**
   * 次要按钮组 (主要操作在右侧)
   */
  secondaryActions: {
    display: 'flex',
    gap: spacing.sm,
    justifyContent: 'flex-start',
    mt: spacing.lg,
    pt: spacing.lg,
    borderTop: `1px solid ${({ palette }: Theme) => palette.divider}`,
  },

  /**
   * 等宽按钮组 (平均分配空间)
   */
  evenActions: {
    display: 'flex',
    gap: spacing.sm,
    justifyContent: 'flex-end',
    mt: spacing.lg,
    pt: spacing.lg,
    borderTop: `1px solid ${({ palette }: Theme) => palette.divider}`,
    '& > button': {
      flex: 1,
    },
  },
} as const;

// =============================================================================
// 按钮组模式 (Button Group Patterns)
// =============================================================================

/**
 * 主要操作按钮组
 * 用于表单底部的主要操作
 */
export const primaryActions = {
  /**
   * 按钮组容器
   */
  root: {
    display: 'flex',
    gap: spacing.sm,
    justifyContent: 'flex-end',
    alignItems: 'center',
  },

  /**
   * 主要按钮
   */
  primaryButton: {
    ml: spacing.sm, // 与次要按钮的间距
  },
} as const;

/**
 * 次要操作按钮组
 * 用于次要操作或返回
 */
export const secondaryActions = {
  /**
   * 按钮组容器
   */
  root: {
    display: 'flex',
    gap: spacing.sm,
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
} as const;

/**
 * 等宽按钮组
 * 用于按钮需要平均分配空间的情况
 */
export const equalActions = {
  /**
   * 按钮组容器
   */
  root: {
    display: 'flex',
    gap: spacing.sm,
    '& > button': {
      flex: 1,
    },
  },
} as const;

// =============================================================================
// 网格布局模式 (Grid Layout Patterns)
// =============================================================================

/**
 * 两列网格模式
 * 左侧固定宽度，右侧自适应
 */
export const twoColumnLayout = {
  /**
   * 容器
   */
  root: {
    display: 'flex',
    gap: spacing.lg,
  },

  /**
   * 侧边栏 (左侧)
   */
  sidebar: {
    width: 280,
    flexShrink: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.lg,
  },

  /**
   * 主内容区 (右侧)
   */
  main: {
    flex: 1,
    minWidth: 0,
  },

  /**
   * 响应式布局 (小屏幕时转为单列)
   */
  responsive: {
    flexDirection: 'column',
    '& > div:first-of-type': {
      width: '100% !important',
    },
  },
} as const;

/**
 * 卡片网格布局
 * 用于展示多个卡片
 */
export const cardGrid = {
  /**
   * 网格容器
   */
  root: {
    display: 'grid',
    gap: spacing.md,
    gridTemplateColumns: {
      xs: '1fr',
      sm: 'repeat(2, 1fr)',
      md: 'repeat(3, 1fr)',
      lg: 'repeat(4, 1fr)',
    },
  },

  /**
   * 卡片容器
   */
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },

  /**
   * 卡片图片区域
   */
  media: {
    height: 200,
    borderRadius: borderRadius.md,
    overflow: 'hidden',
  },

  /**
   * 卡片内容区域
   */
  content: {
    p: spacing.md,
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.sm,
  },

  /**
   * 卡片操作区域
   */
  actions: {
    p: spacing.md,
    pt: 0,
    borderTop: `1px solid ${({
      palette,
    }: Theme) => palette.divider}`,
  },
} as const;

// =============================================================================
// 工具函数
// =============================================================================

/**
 * 获取响应式样式
 * 根据屏幕尺寸返回不同的样式
 *
 * @param styles - 响应式样式对象
 * @returns 合并后的样式
 *
 * @example
 * ```tsx
 * const responsiveStyles = getResponsiveStyles({
 *   xs: { flex: 1 },
 *   md: { flex: 0, width: 300 },
 * });
 * ```
 */
export function getResponsiveStyles<T extends Record<string, SxProps<Theme>>>(
  styles: T
): SxProps<Theme> {
  return (Object.keys(styles) as Array<keyof T>).reduce(
    (acc, key) => ({
      ...acc,
      [`@media (min-width: ${key === 'xs' ? 0 : 600}px)`]: styles[key],
    }),
    {}
  );
}

/**
 * 创建悬停效果
 * 为元素添加统一的悬停效果
 *
 * @param color - 悬停时的背景色，默认为 'action.hover'
 * @returns 悬停效果样式
 */
export function createHoverEffect(
  color: string = 'action.hover'
): SxProps<Theme> {
  return {
    transition: 'background-color 0.2s ease, transform 0.1s ease',
    '&:hover': {
      bgcolor: color,
    },
    '&:active': {
      transform: 'scale(0.98)',
    },
  };
}

/**
 * 创建阴影效果
 * 为元素添加阴影层级
 *
 * @param level - 阴影级别 (0-5)
 * @returns 阴影样式
 */
export function createShadow(level: 0 | 1 | 2 | 3 | 4 | 5): SxProps<Theme> {
  return {
    boxShadow: (theme: Theme) => theme.shadows[level],
  };
}

