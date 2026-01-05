import { Box, Container, CssBaseline, useTheme } from '@mui/material';
import { Outlet, redirect } from 'react-router';
import type { Route } from './+types/auth';

export function loader({request}:Route.ActionArgs){
  const url=new URL(request.url)

  
  if(url.pathname==="/auth"){
    return redirect("/auth/login")
  }
  
}
export default function AuthLayout() {
  const theme = useTheme();

  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundImage: theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
            : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: 3,
        }}
      >
        <Container component="main" maxWidth="sm">
          <Box
            sx={{
              backgroundColor: theme.palette.mode === 'dark'
                ? 'rgba(30, 41, 59, 0.8)'
                : 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(12px)',
              borderRadius: 2,
              boxShadow: theme.palette.mode === 'dark'
                ? '0 8px 32px rgba(0, 0, 0, 0.3)'
                : '0 8px 32px rgba(0, 0, 0, 0.1)',
              p: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              border: theme.palette.mode === 'dark'
                ? '1px solid rgba(255, 255, 255, 0.1)'
                : '1px solid rgba(0, 0, 0, 0.1)',
            }}
          >
            <Outlet/>
          </Box>
        </Container>
      </Box>
    </>
  );
}