// RegisterPage.tsx
import * as React from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
import { useState } from 'react';
import { useUserStore } from '~/stores/userStore';
import { useNavigate } from 'react-router';

export default function RegisterPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { register } = useUserStore();
    const navigate = useNavigate()
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        await register({ username, password });
        // 注册后可以导向登录页或者显示成功消息
        navigate("auth/login")
    };

    return (
        <>
            <Typography component="h1" variant="h5">
                注册
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
                    autoComplete="new-password"
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
                    注册
                </Button>
                <Typography variant="body2" sx={{ color: 'white', textAlign: 'center' }}>
                    已经有账号了？ <a href="/auth/login" style={{ color: '#a8eb12', textDecoration: 'none' }}>去登录</a>
                </Typography>
            </Box>
        </>

    );
}
