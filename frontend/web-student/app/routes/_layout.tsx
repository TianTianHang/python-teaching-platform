import * as React from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import { formatTitle } from '~/config/meta';
import { data, redirect, useNavigate, useNavigation, useSubmit } from 'react-router';
import type { Route } from './+types/_layout';
import { Outlet } from 'react-router';
import { commitSession, getSession, getUserCache, isUserCacheValid, setUserCache, clearUserCache } from '~/sessions.server';
import { withAuth } from '~/utils/loaderWrapper';
import createHttp from '~/utils/http/index.server';
import type { User } from '~/types/user';
import type { UserContextType } from '~/hooks/userUser';
import { getNavItems } from '~/config/navigation';
import { PageContainer } from '~/components/Layout/PageContainer';
import { LoadingState } from '~/components/Layout/LoadingState';
import { AppAppBar } from '~/components/Layout/AppAppBar';
import { MobileDrawer } from '~/components/Layout/MobileDrawer';

export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const session = await getSession(request.headers.get('Cookie'));
  if (!session.get('isAuthenticated')) {
    return redirect(`/auth/login`);
  }

  const http = createHttp(request);

  // 优先从 Session 读取用户缓存
  const cachedUser = getUserCache(session);

  // 检查缓存是否有效
  if (cachedUser && isUserCacheValid(session)) {
    // 缓存有效，直接使用
    return data(cachedUser);
  }

  // 缓存无效或不存在，调用 auth/me API
  try {
    const user = await http.get<User>("auth/me");
    // 更新缓存
    setUserCache(session, user);
    return data(user, {
      headers: {
        'Set-Cookie': await commitSession(session),
      },
    });
  } catch (error: any) {
    // 处理 401 错误：尝试 refresh token
    if (error?.response?.status === 401) {
      try {
        const refreshToken = session.get('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // 尝试刷新 token
        const refreshResponse = await http.post<{ access: string; refresh: string }>('auth/refresh', {
          refresh: refreshToken,
        });

        // 更新 session 中的 tokens
        session.set('accessToken', refreshResponse.access);
        session.set('refreshToken', refreshResponse.refresh);

        // 重试 auth/me 并更新缓存
        const user = await http.get<User>("auth/me");
        setUserCache(session, user);

        return data(user, {
          headers: {
            'Set-Cookie': await commitSession(session),
          },
        });
      } catch (refreshError) {
        // refresh token 失败，清除缓存并重定向到登录页
        clearUserCache(session);
        session.set('isAuthenticated', false);
        return redirect(`/auth/login`, {
          headers: {
            'Set-Cookie': await commitSession(session),
          },
        });
      }
    }

    // 其他错误，直接抛出
    throw error;
  }
})

export default function Layout({ loaderData }: Route.ComponentProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigation = useNavigation();
  const navigate = useNavigate();
  const isNavigating = Boolean(navigation.location);

  const submit = useSubmit()
  const user = loaderData || null;

  // 获取当前路径
  const currentPath = navigation.location?.pathname || '';

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    submit({}, { action: `/auth/logout`, method: "POST" })
  };

  const handleNavigateToProfile = () => {
    navigate("/profile");
  };

  // 使用导航配置
  const navItems = getNavItems();

  return (
    <>
      <title>{formatTitle('Python教学平台')}</title>
      <PageContainer sx={{backgroundColor: 'background.paper', minHeight: '100vh'}} maxWidth={false}>
      {/* 顶部应用栏 */}
      <AppAppBar
        user={user}
        onLogout={handleLogout}
        navItems={navItems}
        currentPath={currentPath}
        isMobile={isMobile}
        mobileOpen={mobileOpen}
        onDrawerToggle={handleDrawerToggle}
        isNavigating={isNavigating}
        onNavigateToProfile={handleNavigateToProfile}
      />

      {/* 移动端抽屉 */}
      <MobileDrawer
        open={mobileOpen}
        onClose={handleDrawerToggle}
        navItems={navItems}
        currentPath={currentPath}
      />

      {/* 主内容区域 */}
      <PageContainer>
         <Box
        component="main"
        sx={{
          mt: '64px', // 为固定 AppBar 留出空间
        }}
        
      >
        <Outlet context={{ user } satisfies UserContextType} />

        {/* 加载状态 */}
        {isNavigating && (
          <LoadingState
            variant="loading"
            message="加载页面中..."
          />
        )}
      </Box>
      </PageContainer>
     

    </PageContainer>
    </>
  );
}
