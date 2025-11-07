import React, { useContext, useState } from 'react';
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
import { AccountCircle, Lock, Visibility, VisibilityOff } from '@mui/icons-material';
import type { Route } from './+types/_layout.profile';
import { useUser } from './_layout';
import { showNotification } from '~/components/Notification';

interface PasswordState {
    currentPassword: string;
    newPassword: string;
    confirmNewPassword: string;
}

const UserProfile = ({ loaderData }: Route.ComponentProps) => {
    const { user } = useUser();

    // 头像状态
    const [avatar, setAvatar] = useState<File | null>(null);
    const [avatarPreview, setAvatarPreview] = useState<string>(
        user?.avatar || '/upload/avatar/user-1.png'
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

    // 处理头像上传
    const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setAvatar(file);
            setAvatarPreview(URL.createObjectURL(file));
        }
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
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
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

        // TODO: 调用 API 更新密码
        
        console.log('提交密码修改:', passwords);
        showNotification('success','success','密码修改成功！');
        setPasswords({ currentPassword: '', newPassword: '', confirmNewPassword: '' });
    };

    return (
        <Box sx={{ maxWidth: 800, margin: 'auto', p: 3 }}>
            <Typography variant="h4" gutterBottom>
                个人资料
            </Typography>

            {/* 基本信息 + 头像 */}
            <Paper sx={{ p: 3, mb: 4 }}>
                <Grid container spacing={3} alignItems="center">
                    <Grid size={{ xs: 12, sm: 8 }} textAlign={{ xs: 'center', sm: 'left' }}>
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
                    <Grid size={{ xs: 12, sm: 8 }}>
                        <TextField
                            label="姓名"
                            fullWidth
                            value={user?.username}
                            margin="normal"
                            slotProps={{
                                input: {
                                    readOnly: true,
                                },
                            }}
                        />
                        <TextField
                            label="邮箱"
                            fullWidth
                            value={user?.email}
                            margin="normal"
                            slotProps={{
                                input: {
                                    readOnly: true,
                                },
                            }}
                        />
                    </Grid>
                </Grid>
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