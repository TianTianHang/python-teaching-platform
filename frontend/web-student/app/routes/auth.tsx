import { Box, Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { Outlet, redirect } from 'react-router';
import type { Route } from './+types/auth';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});
export function loader({request}:Route.ActionArgs){
  const url=new URL(request.url)

  
  if(url.pathname==="/auth"){
    return redirect("/auth/login")
  }
  
}
export default function AuthLayout() {

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          // 示例背景样式
          backgroundImage: 'linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12)', // 炫酷的渐变背景
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: 3, // 内边距
        }}
      >
        <Container component="main" maxWidth="sm">
          <Box
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)', // 半透明白色背景
              backdropFilter: 'blur(10px)', // 磨砂玻璃效果
              borderRadius: 2,
              boxShadow: 3,
              p: 4, // 内边距
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Outlet/>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}