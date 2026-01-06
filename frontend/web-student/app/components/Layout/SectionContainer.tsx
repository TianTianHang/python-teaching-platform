/**
 * SectionContainer - 内容区块容器组件
 *
 * 为页面内提供一致的内容区块间距和样式。
 * 适用于标题、卡片、表单等内容的容器。
 *
 * @example
 * ```tsx
 * import { SectionContainer } from '~/components/Layout/SectionContainer';
 *
 * <SectionContainer spacing="lg">
 *   <Typography variant="h5">区块标题</Typography>
 *   <p>区块内容</p>
 * </SectionContainer>
 * ```
 */

import { Box, type BoxProps, type SxProps, type Theme } from '@mui/material';
import { forwardRef } from 'react';
import { spacing as spacingTokens } from '~/design-system/tokens';

export type SectionVariant = 'card' | 'plain';

export interface SectionContainerProps extends Omit<BoxProps, 'sx'> {
  /**
   * 垂直间距大小
   * @default 'md'
   */
  spacing?: 'sm' | 'md' | 'lg';
  /**
   * 区块样式变体
   * - 'card': 卡片样式 (有背景、圆角、阴影)
   * - 'plain': 平面样式 (纯背景，无阴影)
   * @default 'plain'
   */
  variant?: SectionVariant;
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
 * 内容区块容器组件
 *
 * 提供统一的内容区块容器，包含:
 * - 垂直间距管理
 * - 样式变体 (card/plain)
 * - 可配置的背景和边框
 */
export const SectionContainer = forwardRef<HTMLDivElement, SectionContainerProps>(
  (
    {
      children,
      spacing = 'md',
      variant = 'plain',
      sx,
      disableTopSpacing = false,
      disableBottomSpacing = false,
      ...props
    },
    ref
  ) => {
    // 间距映射
    const spacingMap = {
      sm: spacingTokens.md,
      md: spacingTokens.lg,
      lg: spacingTokens.xl,
    };

    // 样式变体配置
    const variantStyles = {
      card: {
        backgroundColor: 'background.paper',
        borderRadius: 2,
        boxShadow: 1,
        p: spacingTokens.lg,
        mt: disableTopSpacing ? 0 : spacingMap[spacing],
        mb: disableBottomSpacing ? 0 : spacingMap[spacing],
      },
      plain: {
        mt: disableTopSpacing ? 0 : spacingMap[spacing],
        mb: disableBottomSpacing ? 0 : spacingMap[spacing],
      },
    };

    return (
      <Box
        ref={ref}
        sx={{
          // 应用变体样式
          ...variantStyles[variant],
          // 过渡效果
          transition: 'background-color 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            // 轻微的悬停效果 (仅卡片变体)
            ...(variant === 'card' && {
              boxShadow: 2,
            }),
          },
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

SectionContainer.displayName = 'SectionContainer';

export default SectionContainer;
