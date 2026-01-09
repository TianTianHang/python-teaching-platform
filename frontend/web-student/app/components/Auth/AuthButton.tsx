import { Button, CircularProgress, type ButtonProps } from '@mui/material';
import { forwardRef } from 'react';
import { spacing, borderRadius, transitions } from '~/design-system/tokens';

export interface AuthButtonProps extends Omit<ButtonProps, 'loading'> {
  /**
   * 是否显示加载状态
   */
  loading?: boolean;
  /**
   * 加载时显示的文本
   * @default "处理中..."
   */
  loadingText?: string;
  /**
   * 按钮显示的文本
   */
  children: React.ReactNode;
}

/**
 * 统一的认证页面提交按钮
 *
 * 特性：
 * - 使用主题颜色的渐变背景
 * - 支持加载状态显示
 * - 使用设计系统 tokens 替代硬编码值
 * - 平滑的过渡动画
 *
 * @example
 * <AuthButton
 *   type="submit"
 *   loading={isLoading}
 *   loadingText="登录中..."
 * >
 *   登录
 * </AuthButton>
 */
export const AuthButton = forwardRef<HTMLButtonElement, AuthButtonProps>(
  (props, ref) => {
    const { loading, loadingText = '处理中...', children, disabled, ...rest } = props;

    // 组合 disabled 和 loading 状态
    const isDisabled = disabled || loading;

    return (
      <Button
        ref={ref}
        variant="contained"
        fullWidth
        type="submit"
        disabled={isDisabled}
        {...rest}
        sx={(theme) => ({
          // 使用设计系统 tokens
          mt: spacing.xl,
          py: 1.5, // 24px 高度
          borderRadius: borderRadius.md,
          // 主题感知的渐变背景
          background: `linear-gradient(135deg, ${theme.palette.success.main} 0%, ${theme.palette.success.dark} 100%)`,
          // 禁用状态下的背景
          '&:disabled': {
            background: `linear-gradient(135deg, ${theme.palette.action.disabled} 0%, ${theme.palette.action.disabledBackground} 100%)`,
            cursor: 'not-allowed',
          },
          // 过渡动画
          transition: transitions.fast,
          // 悬停效果
          '&:hover:not(:disabled)': {
            background: `linear-gradient(135deg, ${theme.palette.success.dark} 0%, ${theme.palette.success.main} 100%)`,
            transform: 'translateY(-1px)',
            boxShadow: 4,
          },
          // 点击效果
          '&:active:not(:disabled)': {
            transform: 'translateY(0)',
            boxShadow: 2,
          },
        })}
      >
        {loading ? (
          <>
            <CircularProgress
              size={20}
              thickness={3}
              sx={{
                color: 'inherit',
                mr: 1,
              }}
            />
            {loadingText}
          </>
        ) : (
          children
        )}
      </Button>
    );
  }
);

AuthButton.displayName = 'AuthButton';