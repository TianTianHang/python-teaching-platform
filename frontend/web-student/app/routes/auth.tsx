import { CssBaseline, Box } from '@mui/material';
import { Outlet, redirect } from 'react-router';
import ThemeToggle from '~/components/ThemeToggle';
import type { Route } from './+types/auth';

export function loader({request}:Route.ActionArgs){
  const url=new URL(request.url)


  if(url.pathname==="/auth"){
    return redirect("/auth/login")
  }

}
export default function AuthLayout() {
  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 1300, // 高于 Material-UI 的 z-index 标准
        }}
      >
        <ThemeToggle />
      </Box>
      <Outlet/>
    </>
  );
}