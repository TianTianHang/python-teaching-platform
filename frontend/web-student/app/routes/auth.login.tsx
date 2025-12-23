// LoginPage.tsx
import * as React from 'react';
import { useEffect, useState } from 'react';
import {
    Box,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
} from '@mui/material';
import { useSubmit, redirect } from 'react-router';
import type { Route } from './+types/auth.login';
import type { Token, User } from '~/types/user';
import { commitSession, getSession } from '~/sessions.server';
import createHttp from '~/utils/http/index.server';



export async function action({
    request}: Route.ActionArgs) {
    const formData = await request.formData();
    const username = String(formData.get("username"));
    const password = String(formData.get("password"));
    
    try {
        const http = createHttp(request);
        const token = await http.post<Token>("auth/login", { username, password })
        // 创建 session
        const session = await getSession(request.headers.get('Cookie'));
        session.set('accessToken', token.access);
        //console.log(`access: ${token.access}`)
        session.set('refreshToken', token.refresh);
        session.set('isAuthenticated', true);
        const user = await http.get<User>("auth/me",{},{headers:{Authorization: `Bearer ${token.access}`}});
        session.set('user', user);
        return redirect(`/home`, {
            headers: {
                'Set-Cookie': await commitSession(session),
            },
        });
    } catch (error) {
        return { error: (error as Error).message };
    }
}

export default function LoginPage({ actionData }: Route.ComponentProps) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [loading, setLoading] = useState(false);
    const submit = useSubmit()
    const [error, setError] = useState<string | null>(null);
    // 当 actionData 更新时，表示提交完成
    useEffect(() => {
        if (actionData !== undefined) {
            if(actionData?.error!==undefined){
                setError(actionData.error)
            }
            
            setLoading(false);
        }
    }, [actionData]);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        submit({ username, password }, { method: 'post' });
    };

    
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
                    还没有账号？ <a href={`/auth/register`} style={{ color: '#a8eb12', textDecoration: 'none' }}>去注册</a>
                </Typography>
            </Box>
        </>
    );
}
