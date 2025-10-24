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
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import type { Route } from './+types/_layout';
import { Link, Outlet } from 'react-router';

const drawerWidth = 240; // 定义抽屉宽度

export default function Layout({ params }: Route.ComponentProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // 1. 将导航项提取为数组，便于复用
  const navItems = [
    { text: '首页', path: `/${params.lang}/home` },
    { text: '课程', path: `/${params.lang}/courses` },
    { text: 'Playground', path: `/${params.lang}/playground` },
    { text: 'Problems', path: `/${params.lang}/Problems` },
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
        }}
      >
        
        <Toolbar />
        
        {/* 将 Container 移到 main 内部，控制内容最大宽度 */}
        <Container maxWidth="lg">
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}