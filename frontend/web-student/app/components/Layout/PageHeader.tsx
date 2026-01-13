/**
 * PageHeader - 标准页面头部组件
 *
 * 提供统一的页面标题、副标题和操作按钮布局。
 * 支持面包屑导航和自定义操作元素。
 *
 * @example
 * ```tsx
 * import { PageHeader } from '~/components/Layout/PageHeader';
 *
 * <PageHeader
 *   title="我的课程"
 *   subtitle="继续学习您的编程课程"
 *   action={<Button>添加课程</Button>}
 * />
 * ```
 */

import { Box, type BoxProps, type SxProps, type Theme, useTheme } from '@mui/material';
import { forwardRef } from 'react';
import { spacing, transitions } from '~/design-system/tokens';

export interface PageHeaderProps extends Omit<BoxProps, 'title' | 'sx'> {
  /**
   * 页面标题 (必填)
   */
  title: React.ReactNode;
  /**
   * 页面副标题 (可选)
   */
  subtitle?: React.ReactNode;
  /**
   * 操作按钮或操作元素 (可选)
   */
  action?: React.ReactNode;
  /**
   * 面包屑导航 (可选)
   */
  breadcrumbs?: React.ReactNode;
  /**
   * 标题大小
   * @default 'h3'
   */
  titleVariant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  /**
   * 是否显示分隔线
   * @default false
   */
  divider?: boolean;
  /**
   * 自定义样式
   */
  sx?: SxProps<Theme>;
}

/**
 * 页面头部组件
 *
 * 标准化的页面标题布局，包含:
 * - 标题和副标题
 * - 操作按钮
 * - 面包屑导航
 * - 分隔线 (可选)
 */
export const PageHeader = forwardRef<HTMLDivElement, PageHeaderProps>(
  (
    {
      title,
      subtitle,
      action,
      breadcrumbs,
      titleVariant = 'h3',
      divider = false,
      sx,
      children,
      ...props
    },
    ref
  ) => {
    const theme = useTheme();
    return (
      <Box
        ref={ref}
        sx={[
          {
            // 主容器样式
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: { xs: 'stretch', md: 'space-between' },
            alignItems: { xs: 'flex-start', md: 'center' },
            gap: { xs: 1, md: spacing.md },
            mb: spacing.lg,
            transition: transitions.themeSwitch,
          },
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
        {...props}
      >
        {/* 左侧内容 */}
        <Box sx={{ flex: 1 }}>
          {/* 面包屑导航 */}
          {breadcrumbs && (
            <Box sx={{ mb: spacing.sm }}>{breadcrumbs}</Box>
          )}

          {/* 标题和副标题 */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
            {/* 标题 */}
            <Box
              sx={{
                // 动态标题样式
                typography: titleVariant,
                color: 'text.primary',
                lineHeight: 1.3,
                // 移动端优化
                [theme.breakpoints.down('md')]: {
                  fontSize: '1.5rem',
                },
              }}
            >
              {title}
            </Box>

            {/* 副标题 */}
            {subtitle && (
              <Box
                sx={{
                  typography: 'subtitle1',
                  color: 'text.secondary',
                  lineHeight: 1.5,
                }}
              >
                {subtitle}
              </Box>
            )}
          </Box>
        </Box>

        {/* 右侧操作按钮 */}
        {action && (
          <Box
            sx={{
              // 移动端按钮优化
              display: { xs: 'none', md: 'flex' },
              alignItems: 'center',
              gap: 1,
              // 移动端时显示在标题下方
              [theme.breakpoints.down('md')]: {
                display: 'block',
                width: '100%',
                mt: spacing.sm,
                textAlign: 'right',
              },
            }}
          >
            {action}
          </Box>
        )}

        {/* 分隔线 */}
        {divider && (
          <Box
            sx={{
              width: '100%',
              height: 1,
              mt: { xs: spacing.lg, md: spacing.md },
              backgroundColor: 'divider',
            }}
          />
        )}

        {/* 响应式操作按钮 (移动端) */}
        {action && (
          <Box
            sx={{
              display: { xs: 'block', md: 'none' },
              width: '100%',
              mt: spacing.sm,
              textAlign: 'right',
            }}
          >
            {action}
          </Box>
        )}

        {/* 子内容 */}
        {children && (
          <Box
            sx={{
              width: '100%',
              mt: spacing.md,
            }}
          >
            {children}
          </Box>
        )}
      </Box>
    );
  }
);

PageHeader.displayName = 'PageHeader';

export default PageHeader;
