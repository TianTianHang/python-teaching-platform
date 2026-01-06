/**
 * AppAppBar - 应用顶部导航栏组件
 *
 * 提供统一的顶部应用栏，包含：
 * - Logo 和标题
 * - 响应式导航菜单（桌面端按钮 + 移动端汉堡菜单）
 * - 主题切换按钮
 * - 用户菜单（头像下拉）
 *
 * @example
 * ```tsx
 * import { AppAppBar } from '~/components/Layout/AppAppBar';
 *
 * <AppAppBar
 *   user={user}
 *   onLogout={handleLogout}
 *   navItems={navItems}
 *   currentPath={location.pathname}
 *   isMobile={isMobile}
 *   mobileOpen={mobileOpen}
 *   onDrawerToggle={handleDrawerToggle}
 * />
 * ```
 */

import * as React from 'react';
import {
  AppBar,
  Box,
  Button,
  Divider,
  IconButton,
  LinearProgress,
  Menu,
  MenuItem,
  ListItemIcon,
  Toolbar,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';
import LogoutIcon from '@mui/icons-material/Logout';
import { forwardRef, type MouseEvent } from 'react';
import type { User } from '~/types/user';
import type { NavItem } from '~/config/navigation';
import { isActivePath } from '~/config/navigation';
import { Link } from 'react-router';
import ThemeToggle from '~/components/ThemeToggle';
import { spacing } from '~/design-system/tokens';

export interface AppAppBarProps {
  /** 用户对象 */
  user: User | null;
  /** 登出回调 */
  onLogout: () => void;
  /** 导航项配置 */
  navItems: NavItem[];
  /** 当前路径 */
  currentPath: string;
  /** 是否为移动端 */
  isMobile: boolean;
  /** 移动端抽屉是否打开 */
  mobileOpen: boolean;
  /** 移动端抽屉切换回调 */
  onDrawerToggle: () => void;
  /** 是否正在导航 */
  isNavigating?: boolean;
  /** 用户信息导航回调 */
  onNavigateToProfile: () => void;
}

/**
 * 应用顶部导航栏组件
 */
export const AppAppBar = forwardRef<HTMLDivElement, AppAppBarProps>(
  (
    {
      user,
      onLogout,
      navItems,
      currentPath,
      isMobile,
      mobileOpen,
      onDrawerToggle,
      isNavigating = false,
      onNavigateToProfile,
    },
    ref
  ) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

    const handleMenuOpen = (event: MouseEvent<HTMLElement>) => {
      setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
      setAnchorEl(null);
    };

    return (
      <AppBar
        ref={ref}
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: `1px solid`,
          borderColor: 'divider',
          boxShadow: 'none',
        }}
      >
        {/* 导航加载进度条 */}
        {isNavigating && <LinearProgress color="primary" />}

        <Toolbar>
          {/* 移动端汉堡菜单按钮 */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={onDrawerToggle}
              sx={{ mr: spacing.md }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Logo 和标题 */}
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ flexGrow: 1, fontWeight: 700 }}
          >
            学习网站
          </Typography>

          {/* 桌面端导航按钮 */}
          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {navItems.map((item) => {
                const isActive = isActivePath(currentPath, item.path);
                return (
                  <Button
                    key={item.text}
                    color={isActive ? 'primary' : 'inherit'}
                    component={Link}
                    to={item.path}
                    sx={{
                      borderRadius: 2,
                      transition: 'all 0.2s ease',
                      ...(isActive && {
                        backgroundColor: 'primary.main',
                        color: 'primary.contrastText',
                      }),
                      '&:hover': {
                        ...(isActive
                          ? {
                              backgroundColor: 'primary.dark',
                            }
                          : {
                              backgroundColor: 'action.hover',
                            }),
                      },
                    }}
                  >
                    {item.text}
                  </Button>
                );
              })}
            </Box>
          )}

          {/* 分隔线 */}
          <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />

          {/* 主题切换按钮 */}
          <ThemeToggle />

          {/* 用户菜单 */}
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
            {user ? (
              <>
                {/* 用户头像按钮 */}
                <IconButton
                  size="small"
                  onClick={handleMenuOpen}
                  sx={{
                    color: 'text.secondary',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      color: 'primary.main',
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.username}
                      style={{ width: 24, height: 24, borderRadius: '50%' }}
                    />
                  ) : (
                    <AccountCircleIcon fontSize="small" />
                  )}
                </IconButton>

                {/* 用户下拉菜单 */}
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                  onClick={handleMenuClose}
                  slotProps={{
                    paper: {
                      elevation: 0,
                      sx: {
                        overflow: 'visible',
                        filter: (theme) => theme.shadows[4],
                        mt: 1.5,
                        minWidth: 200,
                        '&:before': {
                          content: '""',
                          display: 'block',
                          position: 'absolute',
                          top: 0,
                          right: 14,
                          width: 10,
                          height: 10,
                          bgcolor: 'background.paper',
                          transform: 'translateY(-50%) rotate(45deg)',
                          zIndex: 0,
                          border: `1px solid`,
                          borderColor: 'divider',
                        },
                      },
                    },
                  }}
                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                >
                  {/* 用户信息菜单项 */}
                  <MenuItem
                    onClick={onNavigateToProfile}
                    sx={{
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon>
                      <ManageAccountsIcon fontSize="small" />
                    </ListItemIcon>
                    用户信息
                  </MenuItem>

                  {/* 退出登录菜单项 */}
                  <MenuItem
                    onClick={onLogout}
                    sx={{
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    退出登录
                  </MenuItem>
                </Menu>
              </>
            ) : null}
          </Box>
        </Toolbar>
      </AppBar>
    );
  }
);

AppAppBar.displayName = 'AppAppBar';

export default AppAppBar;
