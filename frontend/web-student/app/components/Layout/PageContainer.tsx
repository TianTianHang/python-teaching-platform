/**
 * PageContainer - 页面主容器组件
 *
 * 提供统一的页面包装器，确保一致的内外边距、最大宽度和居中。
 * 这是所有页面的标准容器组件。
 *
 * @example
 * ```tsx
 * import { PageContainer } from '~/components/Layout/PageContainer';
 *
 * export default function MyPage() {
 *   return (
 *     <PageContainer maxWidth="lg">
 *       <h1>页面标题</h1>
 *       <p>页面内容</p>
 *     </PageContainer>
 *   );
 * }
 * ```
 */

import { Box, type BoxProps, type SxProps, type Theme } from '@mui/material';
import { forwardRef } from 'react';
import { container, spacing, transitions } from '~/design-system/tokens';

export interface PageContainerProps extends Omit<BoxProps, 'maxWidth'> {
  /**
   * 内容的最大宽度
   * @default 'lg'
   */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  /**
   * 自定义样式
   */
  sx?: SxProps<Theme>;
  /**
   * 是否禁用顶部间距
   * @default false
   */
  disableTopSpacing?: boolean;
  /**
   * 是否禁用底部间距
   * @default false
   */
  disableBottomSpacing?: boolean;
}

/**
 * 页面主容器组件
 *
 * 提供统一的页面容器，包含:
 * - 响应式最大宽度
 * - 水平居中
 * - 适当的内边距
 * - 可选的垂直间距
 */
export const PageContainer = forwardRef<HTMLDivElement, PageContainerProps>(
  (
    {
      children,
      maxWidth = 'lg',
      sx,
      disableTopSpacing = false,
      disableBottomSpacing = false,
      ...props
    },
    ref
  ) => {
    // 计算垂直间距
    const verticalPadding = () => {
      const padding: { pt?: number; pb?: number } = {};
      if (!disableTopSpacing) {
        padding.pt = spacing.lg;
      }
      if (!disableBottomSpacing) {
        padding.pb = spacing.xl;
      }
      return padding;
    };

    return (
      <Box
        ref={ref}
        sx={{
          // 水平居中和最大宽度
          maxWidth: maxWidth === false ? undefined : container[maxWidth],
          mx: 'auto',
          // 水平内边距 (在小屏幕上)
          px: { xs: spacing.md, sm: spacing.lg },
          // 垂直间距 (可配置)
          ...verticalPadding(),
          transition: transitions.themeSwitch,
          // 合并自定义样式
          ...sx,
        }}
        {...props}
      >
        {children}
      </Box>
    );
  }
);

PageContainer.displayName = 'PageContainer';

export default PageContainer;
