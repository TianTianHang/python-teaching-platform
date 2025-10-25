// RegisterPage.tsx
import * as React from 'react';
import { useState } from 'react';
import { Box, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';
import { useNavigate, useSubmit, useActionData, redirect } from 'react-router';
import type { Route } from './+types/$(lang).auth.register';
import { createHttp } from '~/utils/http/index.server';
import type { User } from '~/types/user';
import { sessionStorage } from '~/sessions.server';


export async function action({
    request,
}: Route.ActionArgs) {
    let formData = await request.formData();
    let username = String(formData.get("username"));
    let password = String(formData.get("password"));
    let stNumber = String(formData.get("stNumber"));
 
    try {
        const http = createHttp(request);
        const response = await http.post<{
            user: User,
            access: string,
            refresh: string
        }>("auth/register", { 
            username, 
            password,
            st_number: stNumber 
        }, { skipNotification: true });
        
        // 创建 session
        const session = await sessionStorage.getSession(request.headers.get('Cookie'));
        session.set('accessToken', response.access);
        session.set('refreshToken', response.refresh);
        session.set('user', response.user);
        session.set('isAuthenticated', true);
        
        return redirect(`/${request.url.split('/')[3] || 'zh'}/home`, {
            headers: {
                'Set-Cookie': await sessionStorage.commitSession(session),
            },
        });
    } catch (error) {
        return { error: '注册失败，请重试' };
    }
}

export default function RegisterPage({params}:Route.ComponentProps) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [stNumber, setStNumber] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const actionData = useActionData<{ error: string }>();
    const navigate = useNavigate();
    const submit = useSubmit();
    
    // Handle server-side errors
    const [error, setError] = useState<string | null>(actionData?.error || null);
    const [success, setSuccess] = useState(false);
    
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
        if (stNumber.length !== 12) {
            setError('学号长度必须为12位!');
            return;
        }
        
        setLoading(true);
        
        try {
            submit({ username, password, stNumber }, { method: "post" });
            setSuccess(true);
        } catch (err) {
            setError('注册失败，请重试');
        } finally {
            setLoading(false);
        }
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
                    已经有账号了？ <a href={`/${params.lang||"zh"}/auth/login`} style={{ color: '#a8eb12', textDecoration: 'none' }}>去登录</a>
                </Typography>
            </Box>
        </>
    );
}
