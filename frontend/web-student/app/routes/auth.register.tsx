// RegisterPage.tsx
import * as React from 'react';
import { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';
import { useUserStore } from '~/stores/userStore';
import { useNavigate } from 'react-router';
import { useGolbalStore } from '~/stores/globalStore';

export default function RegisterPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [stNumber, setStNumber] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const { register, isAuthenticated } = useUserStore();
    const navigate = useNavigate();
    const {error:globalError} = useGolbalStore()
    
    // 如果已登录，自动跳转到首页
    useEffect(() => {
        if (isAuthenticated) {
            navigate(`/${localStorage.getItem('preferredLang') || 'zh'}/home`);
        }
    }, [isAuthenticated, navigate]);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setError(null);
        
        // 验证密码是否匹配
        if (password !== confirmPassword) {
            setError('密码和确认密码不匹配');
            return;
        }
        
        // 验证密码长度
        if (password.length < 6) {
            setError('密码长度至少为6位');
            return;
        }
        // 学号
        if (stNumber.length!=12){
            setError('学号长度12位!');
            return;
        }
        setLoading(true);
        
        try {
            await register({ username, password, stNumber});
            setSuccess(true);
            // 注册成功后跳转到登录页面
            setTimeout(() => {
                navigate('/auth/login');
            }, 2000);
        } catch (err) {
            setError(globalError?.message||'注册失败，请重试');
        } finally {
            setLoading(false);
        }
    };

    // 如果已登录，显示欢迎信息并跳转
    if (isAuthenticated) {
        return (
            <Box sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ color: 'white' }}>
                    欢迎回来！
                </Typography>
            </Box>
        );
    }

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
                    variant="filled"
                    sx={{ input: { color: 'white' }, label: { color: 'white' }, '& .MuiFilledInput-underline:before': { borderColor: 'rgba(255,255,255,0.7)' }, '& .MuiFilledInput-underline:after': { borderColor: 'white' } }}
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="stNumber"
                    label="学号"
                    name="stNumber"
                    autoComplete="stNumber"
                    autoFocus
                    value={stNumber}
                    onChange={(e) => setStNumber(e.target.value)}
                    variant="filled"
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
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="confirmPassword"
                    label="确认密码"
                    type="password"
                    id="confirmPassword"
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    variant="filled"
                    sx={{ input: { color: 'white' }, label: { color: 'white' }, '& .MuiFilledInput-underline:before': { borderColor: 'rgba(255,255,255,0.7)' }, '& .MuiFilledInput-underline:after': { borderColor: 'white' } }}
                />
                {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        {error}
                    </Alert>
                )}
                {success && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                        注册成功！正在跳转到登录页面...
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
                            注册中...
                        </>
                    ) : '注册'}
                </Button>
                <Typography variant="body2" sx={{ color: 'white', textAlign: 'center' }}>
                    已经有账号了？ <a href="/auth/login" style={{ color: '#a8eb12', textDecoration: 'none' }}>去登录</a>
                </Typography>
            </Box>
        </>
    );
}
