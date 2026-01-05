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
    useTheme,
    Link,
} from '@mui/material';
import { useSubmit, redirect } from 'react-router';
import type { Route } from './+types/auth.login';
import type { Token, User } from '~/types/user';
import { commitSession, getSession } from '~/sessions.server';
import createHttp from '~/utils/http/index.server';



export async function action({
    request }: Route.ActionArgs) {
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
        const user = await http.get<User>("auth/me", {}, { headers: { Authorization: `Bearer ${token.access}` } });
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
    const theme = useTheme();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [loading, setLoading] = useState(false);
    const submit = useSubmit()
    const [error, setError] = useState<string | null>(null);
    // 当 actionData 更新时，表示提交完成
    useEffect(() => {
        if (actionData !== undefined) {
            if (actionData?.error !== undefined) {
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
            <Typography
                component="h1"
                variant="h5"
                sx={{
                    fontWeight: 700,
                    color: theme.palette.text.primary,
                    mb: 2,
                }}
            >
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
                    variant="filled"
                    slotProps={{
                        input: {
                            sx: {
                                color: theme.palette.text.primary,
                                '&:hover': {
                                    '&:not(.Mui-disabled):before': {
                                        borderBottomColor: theme.palette.primary.main,
                                    },
                                },
                                '&.Mui-focused': {
                                    '&:before': {
                                        borderBottomColor: theme.palette.primary.main,
                                    },
                                },
                            },
                        },
                        inputLabel: {
                            sx: {
                                color: theme.palette.text.primary,
                            },
                        },
                    }}
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
                    slotProps={{
                        input: {
                            sx: {
                                color: theme.palette.text.primary,
                                '&:hover': {
                                    '&:not(.Mui-disabled):before': {
                                        borderBottomColor: theme.palette.primary.main,
                                    },
                                },
                                '&.Mui-focused': {
                                    '&:before': {
                                        borderBottomColor: theme.palette.primary.main,
                                    },
                                },
                            },
                        },
                        inputLabel: {
                            sx: {
                                color: theme.palette.text.primary,
                            },
                        },
                    }}
                />
                {error && (
                    <Alert
                        severity="error"
                        sx={{
                            mt: 2,
                            backgroundColor: theme.palette.error.light,
                            borderLeft: `4px solid ${theme.palette.error.main}`,
                        }}
                    >
                        {error}
                    </Alert>
                )}
                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    sx={{
                        mt: 3,
                        mb: 2,
                        background: `linear-gradient(135deg, ${theme.palette.success.main} 0%, ${theme.palette.success.dark} 100%)`,
                        color: 'common.white',
                        fontWeight: 600,
                        borderRadius: 2,
                        padding: '14px 0',
                        '&:hover': {
                            background: `linear-gradient(135deg, ${theme.palette.success.dark} 0%, ${theme.palette.success.main} 100%)`,
                            transform: 'translateY(-1px)',
                        },
                        '&:disabled': {
                            background: theme.palette.action.disabled,
                            color: theme.palette.action.disabled,
                            transform: 'none',
                        },
                    }}
                >
                    {loading ? (
                        <>
                            <CircularProgress size={20} sx={{ mr: 1, color: 'common.white' }} />
                            登录中...
                        </>
                    ) : '登录'}
                </Button>
                <Typography
                    variant="body2"
                    sx={{
                        color: theme.palette.text.secondary,
                        textAlign: 'center',
                        mt: 2,
                    }}
                >
                    还没有账号？{' '}
                    <Link
                        href={`/auth/register`}
                        sx={{
                            color: theme.palette.primary.main,
                            textDecoration: 'none',
                            fontWeight: 500,
                            transition: 'color 0.2s ease',
                            '&:hover': {
                                color: theme.palette.primary.dark,
                            },
                        }}
                    >
                        去注册
                    </Link>
                </Typography>
            </Box>
        </>
    );
}
