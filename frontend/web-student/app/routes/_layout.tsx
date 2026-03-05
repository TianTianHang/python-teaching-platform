import * as React from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import { formatTitle } from '~/config/meta';
import { data, redirect, useNavigate, useNavigation, useSubmit } from 'react-router';
import type { Route } from './+types/_layout';
import { Outlet } from 'react-router';
import { getSession, getUserCache, isUserCacheValid } from '~/sessions.server';
import { withAuth } from '~/utils/loaderWrapper';
import type { User } from '~/types/user';
import type { UserContextType } from '~/hooks/userUser';
import { getNavItems } from '~/config/navigation';
import { PageContainer } from '~/components/Layout/PageContainer';
import { LoadingState } from '~/components/Layout/LoadingState';
import { AppAppBar } from '~/components/Layout/AppAppBar';
import { MobileDrawer } from '~/components/Layout/MobileDrawer';
import { clientHttp, clientAuth } from '~/utils/http/client';

export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const session = await getSession(request.headers.get('Cookie'));
  if (!session.get('isAuthenticated')) {
    return redirect(`/auth/login`);
  }

  const cachedUser = getUserCache(session);
  const isCacheValid = cachedUser && isUserCacheValid(session);

  return data({
    user: isCacheValid ? cachedUser : null,
    hasUser: !!cachedUser,
    needsRefresh: !isCacheValid,
  });
});

interface LayoutLoaderData {
  user: User | null;
  hasUser: boolean;
  needsRefresh: boolean;
}

export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  const serverData = await serverLoader() as LayoutLoaderData;

  if (serverData.needsRefresh) {
    try {
      const user = await clientHttp.get<User>('auth/me');
      
      const token = clientAuth.getToken();
      if (token) {
        const formData = new FormData();
        formData.set('accessToken', token.access);
        formData.set('refreshToken', token.refresh);
        formData.set('user', JSON.stringify(user));
        
        await fetch('/auth/set-session', {
          method: 'POST',
          body: formData,
        });
      }

      return { ...serverData, user };
    } catch {
      return serverData;
    }
  }

  return serverData;
}
clientLoader.hydrate = true as const;

export default function Layout({ loaderData }: Route.ComponentProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigation = useNavigation();
  const navigate = useNavigate();
  const isNavigating = Boolean(navigation.location);

  const submit = useSubmit()
  const user = loaderData?.user || null;

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
