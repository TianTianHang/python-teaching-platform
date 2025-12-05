import React, { useState } from 'react';
import {
    Box,
    Avatar,
    Typography,
    TextField,
    Button,
    Paper,
    Grid,
    IconButton,
    InputAdornment,
    FormControl,
    InputLabel,
    OutlinedInput,
    FormHelperText,
} from '@mui/material';
import { AccountCircle, Lock, Save, Visibility, VisibilityOff } from '@mui/icons-material';
import type { Route } from './+types/_layout.profile';
import { showNotification } from '~/components/Notification';
import { withAuth } from '~/utils/loaderWrapper';
import createHttp from '~/utils/http/index.server';
import { useSubmit } from 'react-router';
import type { User } from '~/types/user';
import { commitSession, getSession } from '~/sessions.server';
import { useUser } from '~/hooks/useSubmission/userUser';

interface PasswordState {
    currentPassword: string;
    newPassword: string;
    confirmNewPassword: string;
}
export const action = withAuth(async ({ request }: Route.ActionArgs) => {
    const formData = await request.formData();
    const intent = formData.get("intent");
    const http = createHttp(request);
    if (intent === "changePassword") {
        // --- 1. 修改密码逻辑 ---
        const oldPassword = String(formData.get("oldPassword"));
        const newPassword = String(formData.get("newPassword"));
        return await http.put<{ detail: string }>("users/me/change-password/", {
            old_password: oldPassword,
            new_password: newPassword
        });

    } else if (intent === "updateProfile") {
        // --- 2. 更新资料逻辑（username/email/avatar） ---

        // a) 处理文本字段
        const username = String(formData.get("username"));
        const email = String(formData.get("email"));

        // b) 处理头像文件上传
        const avatarFile = formData.get("avatar") as File | null;
        let avatarUrl: string | undefined;


        if (avatarFile && avatarFile.size > 0) {
            // 上传文件并获取 URL
            const url = new URL(request.url);
            const cookieHeader = request.headers.get("Cookie");
            const headers: Record<string, string> = {
                // 确保文件上传的 Content-Type 正确处理，通常由 FormData 和 fetch 自动处理
            };

            if (cookieHeader) {
                // 将客户端发来的 Cookie 头部添加到转发请求中
                headers['Cookie'] = cookieHeader;
            }
            const formData = new FormData();
            formData.append('avatar', avatarFile); // 'avatar' 是后端期望的字段名
            const data = await fetch(`${url.protocol}//${url.host}/upload/avatar`, {
                method: 'POST',
                body: formData,
                headers: headers
            })
            avatarUrl = (await data.json()).url;
        }

        // c) 提交更新
        const updateData: { [key: string]: string } = { username, email };
        if (avatarUrl) {
            updateData.avatar = avatarUrl;
        }

        const updatedUser = await http.put<User>(
            "users/me/update/",
            updateData
        );
        const session = await getSession(request.headers.get('Cookie'));
        session.set("user", updatedUser)

        return Response.json({ detail: "资料更新成功" }, {
            headers: {
                'Set-Cookie': await commitSession(session),
            },
        })

    }
})

const UserProfile = () => {
    const { user } = useUser();

    // 头像状态
    const [avatar, setAvatar] = useState<File | null>(null);
    const [avatarPreview, setAvatarPreview] = useState<string>(
        user?.avatar || ''
    );

    // 密码状态
    const [passwords, setPasswords] = useState<PasswordState>({
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
    });

    const [showPassword, setShowPassword] = useState({
        current: false,
        new: false,
        confirm: false,
    });

    const [errors, setErrors] = useState<PasswordState>({
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
    });
    // --- 资料状态 ---
    const [profile, setProfile] = useState({
        username: user?.username || '',
        email: user?.email || '',
    });

    const [profileErrors, setProfileErrors] = useState({
        username: '',
        email: '',
    });
    const submitPasswd = useSubmit()
    // 处理头像上传 
    const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setAvatar(file);
            setAvatarPreview(URL.createObjectURL(file));
        }
    };
    // --- 新增：处理 Profile 字段输入 ---
    const handleProfileChange = (field: 'username' | 'email') =>
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setProfile((prev) => ({ ...prev, [field]: e.target.value }));
            setProfileErrors((prev) => ({ ...prev, [field]: '' }));
        };
    // 处理密码输入
    const handlePasswordChange = (field: keyof PasswordState) =>
        (e: React.ChangeEvent<HTMLInputElement>) => {
            setPasswords((prev) => ({ ...prev, [field]: e.target.value }));
            setErrors((prev) => ({ ...prev, [field]: '' }));
        };

    // 切换密码可见性
    const toggleShowPassword = (field: keyof typeof showPassword) => () => {
        setShowPassword((prev) => ({ ...prev, [field]: !prev[field] }));
    };

    // 表单验证 & 提交
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        let valid = true;
        const newErrors: PasswordState = {
            currentPassword: '',
            newPassword: '',
            confirmNewPassword: '',
        };

        if (!passwords.currentPassword) {
            newErrors.currentPassword = '请输入当前密码';
            valid = false;
        }
        if (passwords.newPassword.length < 6) {
            newErrors.newPassword = '新密码至少6位';
            valid = false;
        }
        if (passwords.newPassword !== passwords.confirmNewPassword) {
            newErrors.confirmNewPassword = '两次输入不一致';
            valid = false;
        }

        if (!valid) {
            setErrors(newErrors);
            return;
        }

        await submitPasswd({ intent: "changePassword", oldPassword: passwords.currentPassword, newPassword: passwords.newPassword }, { method: 'put' })
        console.log('提交密码修改:', passwords);
        showNotification('success', 'success', '密码修改成功！');
        setPasswords({ currentPassword: '', newPassword: '', confirmNewPassword: '' });
    };
    const submitProfile = useSubmit()
    const handleSubmitProfile = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        let valid = true;
        const newErrors = { username: '', email: '' };

        // 客户端验证
        if (!profile.username.trim()) { newErrors.username = '姓名不能为空'; valid = false; }
        // 简单的 Email 验证
        if (!/\S+@\S+\.\S+/.test(profile.email)) { newErrors.email = '请输入有效邮箱'; valid = false; }

        if (!valid) {
            setProfileErrors(newErrors);
            return;
        }

        // 使用 useSubmit 提交数据，包含 intent
        const formData = new FormData();
        formData.append("intent", "updateProfile");
        formData.append("username", profile.username);
        formData.append("email", profile.email);

        // 只有当用户选择了新文件时才上传
        if (avatar) {
            formData.append("avatar", avatar);
        }

        submitProfile(formData, { method: 'put', encType: 'multipart/form-data' });
        // ⚠️ 注意: 包含文件时必须使用 'multipart/form-data'
    };
    return (
        <Box sx={{ maxWidth: 800, margin: 'auto', p: 3 }}>
            <Typography variant="h4" gutterBottom>
                个人资料
            </Typography>

            {/* 基本信息 + 头像 (使用 Form 提交) */}
            <Paper sx={{ p: 3, mb: 4 }}>
                <form onSubmit={handleSubmitProfile}>
                    <Grid container spacing={3} alignItems="center">
                        {/* 头像部分 */}
                        <Grid size={{ xs: 12, sm: 4 }} textAlign={{ xs: 'center', sm: 'left' }}>
                            <Box position="relative" display="inline-block">
                                <Avatar
                                    src={avatarPreview}
                                    sx={{ width: 120, height: 120, margin: '0 auto' }}
                                />
                                <input
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                    id="avatar-upload"
                                    type="file"
                                    onChange={handleAvatarChange}
                                />
                                <label htmlFor="avatar-upload">
                                    <IconButton
                                        color="primary"
                                        component="span"
                                        sx={{
                                            position: 'absolute',
                                            bottom: 0,
                                            right: 0,
                                            backgroundColor: 'white',
                                            boxShadow: 2,
                                        }}
                                    >
                                        <AccountCircle />
                                    </IconButton>
                                </label>
                            </Box>
                        </Grid>

                        {/* 资料字段部分 */}
                        <Grid size={{ xs: 12, sm: 8 }}>
                            <TextField
                                label="姓名"
                                fullWidth
                                name="username"
                                value={profile.username}
                                onChange={handleProfileChange('username')}
                                margin="normal"
                                error={!!profileErrors.username}
                                helperText={profileErrors.username}
                            />
                            <TextField
                                label="邮箱"
                                fullWidth
                                name="email"
                                value={profile.email}
                                onChange={handleProfileChange('email')}
                                margin="normal"
                                error={!!profileErrors.email}
                                helperText={profileErrors.email}
                            />

                            <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }} startIcon={<Save />}>
                                保存资料
                            </Button>
                        </Grid>
                    </Grid>
                </form>
            </Paper>

            {/* 修改密码 */}
            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                    <Lock sx={{ mr: 1 }} /> 修改密码
                </Typography>
                <form onSubmit={handleSubmit}>
                    <FormControl fullWidth margin="normal" error={!!errors.currentPassword}>
                        <InputLabel htmlFor="current-password">当前密码</InputLabel>
                        <OutlinedInput
                            id="current-password"
                            type={showPassword.current ? 'text' : 'password'}
                            value={passwords.currentPassword}
                            onChange={handlePasswordChange('currentPassword')}
                            endAdornment={
                                <InputAdornment position="end">
                                    <IconButton onClick={toggleShowPassword('current')} edge="end">
                                        {showPassword.current ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            }
                            label="当前密码"
                        />
                        {errors.currentPassword && (
                            <FormHelperText>{errors.currentPassword}</FormHelperText>
                        )}
                    </FormControl>

                    <FormControl fullWidth margin="normal" error={!!errors.newPassword}>
                        <InputLabel htmlFor="new-password">新密码</InputLabel>
                        <OutlinedInput
                            id="new-password"
                            type={showPassword.new ? 'text' : 'password'}
                            value={passwords.newPassword}
                            onChange={handlePasswordChange('newPassword')}
                            endAdornment={
                                <InputAdornment position="end">
                                    <IconButton onClick={toggleShowPassword('new')} edge="end">
                                        {showPassword.new ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            }
                            label="新密码"
                        />
                        {errors.newPassword && <FormHelperText>{errors.newPassword}</FormHelperText>}
                    </FormControl>

                    <FormControl fullWidth margin="normal" error={!!errors.confirmNewPassword}>
                        <InputLabel htmlFor="confirm-password">确认新密码</InputLabel>
                        <OutlinedInput
                            id="confirm-password"
                            type={showPassword.confirm ? 'text' : 'password'}
                            value={passwords.confirmNewPassword}
                            onChange={handlePasswordChange('confirmNewPassword')}
                            endAdornment={
                                <InputAdornment position="end">
                                    <IconButton onClick={toggleShowPassword('confirm')} edge="end">
                                        {showPassword.confirm ? <VisibilityOff /> : <Visibility />}
                                    </IconButton>
                                </InputAdornment>
                            }
                            label="确认新密码"
                        />
                        {errors.confirmNewPassword && (
                            <FormHelperText>{errors.confirmNewPassword}</FormHelperText>
                        )}
                    </FormControl>

                    <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                        保存修改
                    </Button>
                </form>
            </Paper>
        </Box>
    );
};

export default UserProfile;