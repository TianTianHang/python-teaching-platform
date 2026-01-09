/**
 * Design Tokens - 设计标记系统
 *
 * 这是设计系统的单一真实来源，提供统一的设计标准。
 * 所有组件应该使用这些标记而不是硬编码值。
 *
 * @see https://www.designsystems.com/spacing-scale/
 */

/**
 * 间距标准 - Spacing Scale
 * 基于 8px 网格系统，符合业界标准
 *
 * 使用示例:
 * ```tsx
 * import { spacing } from '~/design-system/tokens';
 *
 * <Box sx={{ p: spacing.md, mb: spacing.lg }}>Content</Box>
 * ```
 */
export const spacing = {
  xs: 0.5,    // 4px   - 极小间距
  sm: 1,      // 8px   - 小间距
  md: 2,      // 16px  - 中等间距 (默认)
  lg: 3,      // 24px  - 大间距
  xl: 4,      // 32px  - 超大间距
  xxl: 5,     // 40px  - 极大间距
  section: 6, // 48px  - 主要章节间距
} as const;

/**
 * 容器宽度 - Container Widths
 * 定义不同断点的最大内容宽度
 *
 * 使用示例:
 * ```tsx
 * <Container maxWidth={container.lg}>Content</Container>
 * ```
 */
export const container = {
  xs: '100%',
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
} as const;

/**
 * 圆角 - Border Radius
 * 统一的圆角标准
 *
 * 使用示例:
 * ```tsx
 * <Card sx={{ borderRadius: borderRadius.md }}>Content</Card>
 * ```
 */
export const borderRadius = {
  sm: 4,    // 小圆角 - 按钮、输入框
  md: 8,    // 中等圆角 - 卡片 (默认，与主题一致)
  lg: 12,   // 大圆角 - 模态框
  xl: 16,   // 超大圆角 - 特殊组件
  full: 9999, // 完全圆角 - 徽章、头像
} as const;

/**
 * 过渡效果 - Transitions
 * 标准的动画时长和缓动函数
 *
 * 使用示例:
 * ```tsx
 * <Box sx={{ transition: transitions.fast }}>Content</Box>
 * ```
 */
export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',    // 快速 - 悬停效果
  normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',  // 正常 - 主题切换
  slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',    // 慢速 - 页面转换

  // 复合过渡效果 - 用于常见场景
  themeSwitch: 'background-color 300ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1)', // 主题切换

  // 交互效果 - 指定属性的过渡（避免使用 'all'）
  interactive: 'color 150ms cubic-bezier(0.4, 0, 0.2, 1), background-color 150ms cubic-bezier(0.4, 0, 0.2, 1), transform 150ms cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

/**
 * Z-Index 层级 - Z-Index Scale
 * 统一的 z-index 管理避免层级冲突
 *
 * 使用示例:
 * ```tsx
 * <Box sx={{ zIndex: zIndex.drawer }}>Content</Box>
 * ```
 */
export const zIndex = {
  dropdown: 1000,     // 下拉菜单
  sticky: 1020,       // 粘性元素
  fixed: 1030,        // 固定元素
  modalBackdrop: 1040,// 模态框背景
  modal: 1050,        // 模态框
  popover: 1060,      // 弹出框
  tooltip: 1070,      // 工具提示
} as const;

/**
 * 断点 - Breakpoints
 * 响应式设计的断点标准 (与 MUI 主题一致)
 *
 * 使用示例:
 * ```tsx
 * <Box sx={{
 *   [breakpoints.down('sm')]: { fontSize: '0.875rem' }
 * }}>
 *   Content
 * </Box>
 * ```
 */
export const breakpoints = {
  xs: 0,      // 手机竖屏
  sm: 600,    // 手机横屏 / 平板竖屏
  md: 900,    // 平板横屏 / 小笔记本
  lg: 1200,   // 桌面
  xl: 1536,   // 大桌面
} as const;

/**
 * 类型导出
 */
export type Spacing = keyof typeof spacing;
export type ContainerSize = keyof typeof container;
export type BorderRadius = keyof typeof borderRadius;
export type TransitionDuration = keyof typeof transitions;
export type ZIndex = keyof typeof zIndex;
export type Breakpoint = keyof typeof breakpoints;
