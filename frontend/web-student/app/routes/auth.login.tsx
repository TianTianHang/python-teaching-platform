// LoginPage.tsx
import * as React from 'react';
import { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    Typography,
} from '@mui/material';
import { useUserStore } from '~/stores/userStore'; // Assuming your zustand store is in this path

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login, isAuthenticated,user } = useUserStore();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        await login({ username, password });
    };

    // 如果已登录，可以直接显示消息或重定向
    if (isAuthenticated) {
        return (

            <Box sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ color: 'white' }}>
                    欢迎回来，{ user?.username}！
                </Typography>
                <Button variant="outlined" sx={{ mt: 2, color: 'white', borderColor: 'white' }}>
                    前往仪表盘
                </Button>
            </Box>

        );
    }

    return (
        <>
            <Typography component="h1" variant="h5">
                登录
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="username"
                    label="用户名"
                    name="username"
                    autoComplete="username"
                    autoFocus
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    variant="filled" // 使用实心变体以更好地融入模糊背景
                    sx={{ input: { color: 'white' }, label: { color: 'white' }, '& .MuiFilledInput-underline:before': { borderColor: 'rgba(255,255,255,0.7)' }, '& .MuiFilledInput-underline:after': { borderColor: 'white' } }}
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="password"
                    label="密码"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    variant="filled"
                    sx={{ input: { color: 'white' }, label: { color: 'white' }, '& .MuiFilledInput-underline:before': { borderColor: 'rgba(255,255,255,0.7)' }, '& .MuiFilledInput-underline:after': { borderColor: 'white' } }}
                />
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2, backgroundColor: '#00bf72', '&:hover': { backgroundColor: '#008793' } }}
                >
                    登录
                </Button>
                <Typography variant="body2" sx={{ color: 'white', textAlign: 'center' }}>
                    还没有账号？ <a href="/auth/register" style={{ color: '#a8eb12', textDecoration: 'none' }}>去注册</a>
                </Typography>
            </Box>
        </>
    );
}
