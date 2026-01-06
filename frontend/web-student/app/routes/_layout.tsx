import * as React from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import { data, redirect, useNavigate, useNavigation, useSubmit } from 'react-router';
import type { Route } from './+types/_layout';
import { Outlet } from 'react-router';
import { commitSession, getSession } from '~/sessions.server';
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
  const user = await http.get<User>("auth/me");
  session.set('user', user);
  return data(user, {
    headers: {
      'Set-Cookie': await commitSession(session),
    },
  })
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
    <PageContainer  maxWidth={false}>
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
      <PageContainer maxWidth="lg" disableTopSpacing>
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
  );
}
