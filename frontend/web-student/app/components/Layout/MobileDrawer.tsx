/**
 * MobileDrawer - 移动端侧边栏抽屉组件
 *
 * 为移动端提供侧边栏导航菜单，在小屏幕上显示。
 * 支持激活状态高亮和点击关闭。
 *
 * @example
 * ```tsx
 * import { MobileDrawer } from '~/components/Layout/MobileDrawer';
 *
 * <MobileDrawer
 *   open={mobileOpen}
 *   onClose={handleDrawerToggle}
 *   navItems={navItems}
 *   currentPath={location.pathname}
 * />
 * ```
 */

import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Toolbar,
} from '@mui/material';
import { forwardRef } from 'react';
import type { NavItem } from '~/config/navigation';
import { isActivePath } from '~/config/navigation';
import { Link } from 'react-router';
import { spacing } from '~/design-system/tokens';

export interface MobileDrawerProps {
  /** 是否打开抽屉 */
  open: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 导航项配置 */
  navItems: NavItem[];
  /** 当前路径 */
  currentPath: string;
  /** 抽屉宽度 */
  drawerWidth?: number;
}

/**
 * 移动端侧边栏抽屉组件
 */
export const MobileDrawer = forwardRef<HTMLDivElement, MobileDrawerProps>(
  ({ open, onClose, navItems, currentPath, drawerWidth = 240 }, ref) => {
    // 抽屉内容
    const drawerContent = (
      <Box onClick={onClose} sx={{ textAlign: 'center' }}>
        {/* Toolbar 占位，使内容在 AppBar 下方 */}
        <Toolbar />
        <List>
          {navItems.map((item) => {
            const isActive = isActivePath(currentPath, item.path);
            return (
              <ListItem key={item.text} disablePadding>
                {/* 移动端菜单项使用 Link 实现 SPA 导航 */}
                <ListItemButton
                  component={Link}
                  to={item.path}
                  sx={{
                    textAlign: 'center',
                    ...(isActive && {
                      backgroundColor: 'primary.main',
                      '& .MuiListItemText-primary': {
                        color: 'primary.contrastText',
                      },
                    }),
                  }}
                >
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    );

    return (
      <Drawer
        ref={ref}
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // 更好地支持移动端性能
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }
);

MobileDrawer.displayName = 'MobileDrawer';

export default MobileDrawer;
