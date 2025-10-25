import * as React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  CssBaseline,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  useTheme,
  useMediaQuery,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import { redirect, useNavigate, useSubmit } from 'react-router';
import type { Route } from './+types/($lang)._layout';
import { Link, Outlet } from 'react-router';
import createHttp from '~/utils/http/index.server';
import type { User } from '~/types/user';
import { getSession } from '~/sessions.server';

const drawerWidth = 240; // 定义抽屉宽度
export async function loader({ request, params }: Route.LoaderArgs) {
  const http = createHttp(request);
  const session = await getSession(request.headers.get('Cookie'));
  if (!session.get('isAuthenticated')) {
    return redirect(`/${params.lang || "zh"}/auth/login`);
  }
  const user = await http.get<User>("auth/me");
  session.set('user', user);
  return user
}
export default function Layout({ params, loaderData }: Route.ComponentProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const submit = useSubmit()
  const user = loaderData;
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    submit({}, { action: `/${params.lang || "zh"}/auth/logout`, method: "POST" })
  };

  // 1. 将导航项提取为数组，便于复用
  const navItems = [
    { text: '首页', path: `/${params.lang || "zh"}/home` },
    { text: '课程', path: `/${params.lang || "zh"}/courses` },
    { text: 'Playground', path: `/${params.lang || "zh"}/playground` },
    { text: 'Problems', path: `/${params.lang || "zh"}/Problems` },
  ];

  // 2. 移动端抽屉的 JSX
  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      {/* 同样使用 Toolbar 占位，使内容在 AppBar 下方 */}
      <Toolbar />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            {/* 3. 在移动端菜单项中使用 Link 实现 SPA 导航 */}
            <ListItemButton component={Link} to={item.path} sx={{ textAlign: 'center' }}>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            学习网站
          </Typography>
          {!isMobile && (
            <Box>
              {navItems.map((item) => (
                // 3. 在桌面端按钮中使用 Link 实现 SPA 导航
                <Button
                  key={item.text}
                  color="inherit"
                  component={Link}
                  to={item.path}
                >
                  {item.text}
                </Button>
              ))}
            </Box>
          )}
          {/* 用户菜单 */}
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
            {user ? (
              <>
                <Button
                  size="small"
                  sx={{ color: 'white', textTransform: 'none' }}
                  onClick={handleMenuOpen}
                  startIcon={<AccountCircleIcon />}
                >
                  {user.username}
                </Button>
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
                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                        mt: 1.5,
                        '& .MuiAvatar-root': {
                          width: 32,
                          height: 32,
                          ml: -0.5,
                          mr: 1,
                        },
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
                        },
                      },
                    }
                  }
                  }

                  transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                  anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                >
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    退出登录
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <></>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* 1. 添加移动端抽屉组件 */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // 更好地支持移动端 SEO
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>

      {/* 4. 使用 <main> 标签和 <Toolbar> 占位符 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3, // 添加一些内边距
          width: { xs: '100%', sm: `calc(100% - ${drawerWidth}px)` }, // 为侧边栏布局调整宽度（如果未来添加永久侧边栏）
          mt: '64px', // 为固定AppBar留出空间
        }}
      >
        {/* 将 Container 移到 main 内部，控制内容最大宽度 */}
        <Container maxWidth="lg">
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}