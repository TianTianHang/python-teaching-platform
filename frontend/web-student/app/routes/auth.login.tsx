// LoginPage.tsx
import * as React from 'react';
import { useState, useEffect } from 'react';
import {
    Box,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
} from '@mui/material';
import { useUserStore } from '~/stores/userStore'; // Assuming your zustand store is in this path
import { useNavigate } from 'react-router';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { login, isAuthenticated, user } = useUserStore();
    const navigate = useNavigate();

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            await login({ username, password });
            // 登录成功后跳转到首页或之前访问的页面
            navigate(`/${localStorage.getItem('preferredLang') || 'zh'}/home`);
        } catch (err) {
            // 错误已经在 store 或 http 拦截器中处理，但我们可以设置本地错误状态
            setError('登录失败，请检查用户名和密码');
        } finally {
            setLoading(false);
        }
    };

    // 如果已登录，自动跳转到首页
    useEffect(() => {
        if (isAuthenticated) {
            navigate(`/${localStorage.getItem('preferredLang') || 'zh'}/home`);
        }
    }, [isAuthenticated, navigate]);

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
                {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        {error}
                    </Alert>
                )}
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    sx={{ mt: 3, mb: 2, backgroundColor: '#00bf72', '&:hover': { backgroundColor: '#008793' } }}
                >
                    {loading ? (
                        <>
                            <CircularProgress size={20} sx={{ mr: 1, color: 'white' }} />
                            登录中...
                        </>
                    ) : '登录'}
                </Button>
                <Typography variant="body2" sx={{ color: 'white', textAlign: 'center' }}>
                    还没有账号？ <a href="/auth/register" style={{ color: '#a8eb12', textDecoration: 'none' }}>去注册</a>
                </Typography>
            </Box>
        </>
    );
}
