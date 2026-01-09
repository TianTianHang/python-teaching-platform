import { Box, useTheme, type BoxProps } from '@mui/material';
import { forwardRef } from 'react';
import { SectionContainer } from '~/components/Layout/SectionContainer';
import { spacing } from '~/design-system/tokens';

export interface AuthContainerProps extends Omit<BoxProps, 'title'> {
  /**
   * 页面标题 (可选)
   */
  title?: string;
  /**
   * 页面副标题 (可选)
   */
  subtitle?: string;
}

/**
 * 认证页面容器组件
 *
 * 提供统一的认证页面布局，包括：
 * - 居中的卡片式布局
 * - 可选的标题和副标题
 * - 统一的间距和样式
 * - 支持深色/浅色模式
 *
 * 使用 SectionContainer variant="card" 和设计系统 tokens，
 * 替代了 auth.tsx 中的硬编码布局。
 *
 * @example
 * <AuthContainer title="登录" subtitle="请输入您的账号信息">
 *   <LoginForm />
 * </AuthContainer>
 */
export const AuthContainer = forwardRef<HTMLDivElement, AuthContainerProps>(
  (props, ref) => {
    const { title, subtitle, children, sx, ...boxProps } = props;
    const theme = useTheme();
    const isDark = theme.palette.mode === 'dark';

    return (
      <Box
        ref={ref}
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',

          // 基础渐变背景
          background: isDark
            ? 'linear-gradient(135deg, #121212 0%, #1A1A1A 100%)'
            : 'linear-gradient(135deg, #FAFAFA 0%, #F5F5F5 100%)',

          // 网格叠加层
          backgroundImage: `
            linear-gradient(${isDark ? 'rgba(123, 109, 255, 0.15)' : 'rgba(91, 77, 255, 0.12)'} 1px, transparent 1px),
            linear-gradient(90deg, ${isDark ? 'rgba(123, 109, 255, 0.15)' : 'rgba(91, 77, 255, 0.12)'} 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
          backgroundPosition: 'center center',

          // 确保背景固定，内容滚动
          position: 'relative',
          overflow: 'hidden',

          // 左上角圆形光晕装饰
          '&::before': {
            content: '""',
            position: 'absolute',
            width: { xs: '200px', md: '400px' },
            height: { xs: '200px', md: '400px' },
            background: `radial-gradient(circle, ${isDark ? 'rgba(123, 109, 255, 0.12)' : 'rgba(91, 77, 255, 0.10)'} 0%, transparent 70%)`,
            top: '-100px',
            left: '-100px',
            borderRadius: '50%',
            pointerEvents: 'none',
          },

          // 右下角圆形光晕装饰
          '&::after': {
            content: '""',
            position: 'absolute',
            width: { xs: '300px', md: '500px' },
            height: { xs: '300px', md: '500px' },
            background: `radial-gradient(circle, ${isDark ? 'rgba(123, 109, 255, 0.12)' : 'rgba(91, 77, 255, 0.10)'} 0%, transparent 70%)`,
            bottom: '-150px',
            right: '-150px',
            borderRadius: '50%',
            pointerEvents: 'none',
          },

          // 透传自定义样式
          ...sx,
        }}
        {...boxProps}
      >
        {/* 右上角旋转方框装饰 */}
        <Box
          sx={{
            position: 'absolute',
            top: { xs: '10%', md: '15%' },
            right: { xs: '5%', md: '10%' },
            width: { xs: '60px', md: '100px' },
            height: { xs: '60px', md: '100px' },
            border: `2px solid ${isDark ? 'rgba(123, 109, 255, 0.20)' : 'rgba(91, 77, 255, 0.15)'}`,
            transform: 'rotate(45deg)',
            opacity: 0.8,
            pointerEvents: 'none',
          }}
        />

        <SectionContainer variant="card" spacing="lg" maxWidth="600px">
          {/* 标题区域 */}
          {(title || subtitle) && (
            <Box sx={{ textAlign: 'center', mb: spacing.lg }}>
              {title && (
                <Box
                  component="h1"
                  sx={{
                    fontSize: 'h4.fontSize',
                    fontWeight: 600,
                    color: 'text.primary',
                    lineHeight: 1.2,
                    mb: subtitle ? spacing.sm : 0,
                  }}
                >
                  {title}
                </Box>
              )}
              {subtitle && (
                <Box
                  sx={{
                    fontSize: 'body1.fontSize',
                    color: 'text.secondary',
                    lineHeight: 1.5,
                  }}
                >
                  {subtitle}
                </Box>
              )}
            </Box>
          )}

          {/* 内容区域 */}
          {children}
        </SectionContainer>
      </Box>
    );
  }
);

AuthContainer.displayName = 'AuthContainer';