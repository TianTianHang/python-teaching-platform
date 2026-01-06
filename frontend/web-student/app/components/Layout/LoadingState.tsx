/**
 * LoadingState - 统一加载状态组件
 *
 * 提供 Loading、Error、Empty 等状态的统一显示方式。
 * 可以用于页面级或组件级的加载状态展示。
 *
 * @example
 * ```tsx
 * import { LoadingState } from '~/components/Layout/LoadingState';
 *
 * // 简单加载状态
 * <LoadingState message="加载课程中..." />
 *
 * // 错误状态
 * <LoadingState error={true} message="加载失败" />
 *
 * // 空状态
 * <LoadingState empty={true} message="暂无数据" />
 * ```
 */

import { Box, type BoxProps, type SxProps, type Theme } from '@mui/material';
import { forwardRef } from 'react';
import { spacing } from '~/design-system/tokens';

export interface LoadingStateProps extends Omit<BoxProps, 'sx'> {
  /**
   * 加载状态类型
   * @default 'loading'
   */
  variant?: 'loading' | 'error' | 'empty';
  /**
   * 显示的消息文本
   */
  message: string;
  /**
   * 子内容 (空状态时可添加额外内容)
   */
  children?: React.ReactNode;
  /**
   * 是否显示圆环加载动画
   * @default true (仅当 variant 为 'loading' 时)
   */
  showSpinner?: boolean;
  /**
   * 自定义样式
   */
  sx?: SxProps<Theme>;
  /**
   * 图标或自定义渲染器
   */
  renderIcon?: (variant: 'loading' | 'error' | 'empty') => React.ReactNode;
}

/**
 * 统一加载状态组件
 *
 * 统一处理各种状态的显示:
 * - 加载中: 显示加载动画和消息
 * - 错误: 显示错误图标和错误消息
 * - 空数据: 显示空状态图标和消息
 */
export const LoadingState = forwardRef<HTMLDivElement, LoadingStateProps>(
  (
    {
      variant = 'loading',
      message,
      children,
      showSpinner = variant === 'loading',
      sx,
      renderIcon,
      ...props
    },
    ref
  ) => {
    // 渲染图标
    const renderLoadingIcon = () => {
      if (!showSpinner) return null;

      if (renderIcon) {
        return renderIcon(variant);
      }

      // 默认的图标
      switch (variant) {
        case 'loading':
          return (
            <Box
              component="span"
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 24,
                height: 24,
                mr: spacing.sm,
              }}
            >
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  border: '2px solid',
                  borderColor: 'primary.main',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                  },
                }}
              />
            </Box>
          );

        case 'error':
          return (
            <Box
              component="span"
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 24,
                height: 24,
                mr: spacing.sm,
                color: 'error.main',
              }}
            >
              <Box sx={{ fontSize: 20 }}>⚠️</Box>
            </Box>
          );

        case 'empty':
          return (
            <Box
              component="span"
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                mr: spacing.sm,
                color: 'text.secondary',
              }}
            >
              <Box sx={{ fontSize: 32 }}>📋</Box>
            </Box>
          );

        default:
          return null;
      }
    };

    // 颜色映射
    const colorMap = {
      loading: 'text.secondary',
      error: 'error.main',
      empty: 'text.secondary',
    };

    return (
      <Box
        ref={ref}
        sx={[
          {
            // 基础样式
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: { xs: 200, sm: 300 },
            py: spacing.xl,
            textAlign: 'center',
          },
          // 特定变体样式
          {
            color: colorMap[variant],
            ...(variant === 'error' && {
              '.MuiAlert-root': {
                bgcolor: 'error.lighter',
                color: 'error.main',
                borderColor: 'error.main',
              },
            }),
          },
          // 合并自定义样式
          ...(Array.isArray(sx) ? sx : [sx]),
        ]}
        {...props}
      >
        {/* 图标 */}
        <Box sx={{ mb: spacing.md }}>
          {renderLoadingIcon()}
        </Box>

        {/* 消息文本 */}
        <Box
          sx={{
            typography: variant === 'error' ? 'body2' : 'body1',
            lineHeight: 1.5,
            maxWidth: 400,
            mx: 'auto',
          }}
        >
          {message}
        </Box>

        {/* 错误详情 (如果有) */}
        {variant === 'error' && children && (
          <Box
            sx={{
              mt: spacing.md,
              maxWidth: 500,
              width: '100%',
              bgcolor: 'error.lighter',
              border: `1px solid ${({
                palette,
              }: Theme) => palette.error.main}20`,
              borderRadius: 1,
              p: spacing.md,
            }}
          >
            {children}
          </Box>
        )}

        {/* 子内容 (主要用于空状态) */}
        {variant !== 'error' && children && (
          <Box sx={{ mt: spacing.md }}>{children}</Box>
        )}
      </Box>
    );
  }
);

LoadingState.displayName = 'LoadingState';

export default LoadingState;
