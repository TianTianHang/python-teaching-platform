import { Link, type LinkProps } from '@mui/material';
import { forwardRef } from 'react';
import { transitions } from '~/design-system/tokens';

export interface AuthLinkProps extends Omit<LinkProps, 'children' | 'to'> {
  /**
   * 链接目标
   * @example "/auth/register"
   */
  to: string;
  /**
   * 前置文本
   * @example "还没有账号？"
   */
  text: React.ReactNode;
  /**
   * 链接文本
   * @example "去注册"
   */
  linkText: React.ReactNode;
}

/**
 * 统一的认证页面链接组件
 *
 * 用于创建认证页面间的导航链接，如：
 * - "还没有账号？<去注册>"
 * - "已有账号？<去登录>"
 *
 * 特性：
 * - 使用 MUI Link 组件保持一致性
 * - 主题感知的颜色
 * - 平滑的过渡动画
 * - 统一的悬停效果
 *
 * @example
 * <AuthLink
 *   to="/auth/register"
 *   text="还没有账号？"
 *   linkText="去注册"
 * />
 */
export const AuthLink = forwardRef<HTMLAnchorElement, AuthLinkProps>(
  (props, ref) => {
    const { text, linkText, sx, ...linkProps } = props;

    return (
      <>
        {text}
        <Link
          ref={ref}
          href={props.to}
          {...linkProps}
          sx={{
            // 默认样式
            color: 'primary.main',
            textDecoration: 'none',
            fontWeight: 500,
            fontSize: 'body2.fontSize',
            // 过渡动画
            transition: transitions.fast,
            // 悬停效果
            '&:hover': {
              color: 'primary.dark',
              textDecoration: 'underline',
            },
            // 透传自定义样式
            ...sx,
          }}
        >
          <span style={{ color: 'inherit' }}>{linkText}</span>
        </Link>
      </>

    );
  }
);

AuthLink.displayName = 'AuthLink';