import { Box, Button, Card, CardContent, Chip, Divider, Grid, List, ListItem, ListItemIcon, ListItemText, Skeleton, Stack, Typography, useTheme } from "@mui/material";
import type { Theme } from "@mui/material/styles";
import type { Route } from "./+types/_layout.home";
import React from "react";
import {
    Book as BookIcon,
    Code as CodeIcon,
    Quiz as QuizIcon,
    PlayArrow as PlayArrowIcon,
    CheckCircle as CheckCircleIcon,
    HourglassEmpty as HourglassEmptyIcon,
    Cancel as CancelIcon,
    RadioButtonUnchecked as RadioButtonUncheckedIcon
} from '@mui/icons-material';
import { withAuth } from "~/utils/loaderWrapper";
import createHttp from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import type { Enrollment, ProblemProgress } from "~/types/course";
import { Await, useNavigate } from "react-router";
import { getDifficultyLabel } from "~/utils/chips";
import ResolveError from "~/components/ResolveError";
import type { AxiosError } from "axios";
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
    const http = createHttp(request);
    const enrollments = http.get<Page<Enrollment>>('enrollments/')
        .catch((e: AxiosError) => {
            return {
                status: e.status,
                message: e.message,
            }
        });;
    const unfinished_problems = http.get<Page<ProblemProgress>>('problem-progress/?status_not=solved')
        .catch((e: AxiosError) => {
            return {
                status: e.status,
                message: e.message,
            }
        });;
    return { enrollments, unfinished_problems }
})


export default function Home({ loaderData }: Route.ComponentProps) {
    const theme = useTheme();
    const enrolledCourses = loaderData.enrollments;
    const unfinished_problems = loaderData.unfinished_problems;

    // const recentDiscussions = [
    //     { id: 1, title: "第3章链表插入逻辑疑问", author: "张三", replies: 5, createdAt: "2小时前" },
    //     { id: 2, title: "两数之和测试用例不通过？", author: "李四", replies: 12, createdAt: "1天前" },
    // ];

    const getProblemStatusIcon = (status: string) => {
        switch (status) {
            case 'solved':
                return <CheckCircleIcon color="success" fontSize="small" />;
            case 'in_progress':
                return <HourglassEmptyIcon color="warning" fontSize="small" />;
            case 'failed':
                return <CancelIcon color="error" fontSize="small" />;
            case 'not_started':
            default:
                return <RadioButtonUncheckedIcon color="disabled" fontSize="small" />;
        }
    };

    const getProblemStatusChip = (status: string) => {
        const statusMap = {
            'solved': { label: '已解决', color: 'success' as const },
            'in_progress': { label: '进行中', color: 'warning' as const },
            'failed': { label: '未通过', color: 'error' as const },
            'not_started': { label: '未开始', color: 'default' as const },
        };
        const statusConfig = statusMap[status as keyof typeof statusMap] || statusMap['not_started'];

        return (
            <Chip
                label={statusConfig.label}
                color={statusConfig.color}
                size="small"
                variant="outlined"
                sx={{
                    fontWeight: 500,
                }}
            />
        );
    };

    const navigate = useNavigate();
    return (
        <Box sx={{ p: 3 }}>
            {/* 欢迎标题 */}
            {/* <Typography variant="h4" gutterBottom>
        欢迎回来，学员！
      </Typography> */}

            {/* 第一部分：我的课程 */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                        <BookIcon sx={{ mr: 1 }} /> 我的课程
                    </Typography>
                    <Grid container spacing={2}>
                        <React.Suspense fallback={<EnrolledCoursesSkeleton />}>
                            <Await
                                resolve={enrolledCourses}
                                children={(resolvedEnrolledCourses) => {
                                    if ('status' in resolvedEnrolledCourses) {
                                        return (
                                            <ResolveError status={resolvedEnrolledCourses.status} message={resolvedEnrolledCourses.message}>
                                                <Grid size={12}>
                                                    <Typography color="error">无法加载课程列表 😬</Typography>
                                                </Grid>
                                            </ResolveError>)
                                    }
                                    return (
                                        resolvedEnrolledCourses.results.length > 0 ? (
                                            resolvedEnrolledCourses.results.map((course) => (
                                                <Grid size={{ xs: 12, md: 6 }} key={course.id}>
                                                    <Card
                                                        elevation={2}
                                                        sx={{
                                                            p: 3,
                                                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                                            position: 'relative',
                                                            overflow: 'hidden',
                                                            cursor: 'pointer',
                                                            '&:hover': {
                                                                elevation: 8,
                                                                transform: 'translateY(-4px)',
                                                            },
                                                            '&:hover::before': {
                                                                content: '""',
                                                                position: 'absolute',
                                                                top: 0,
                                                                left: 0,
                                                                right: 0,
                                                                height: '3px',
                                                                background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                                                            },
                                                        }}
                                                    >
                                                        {/* Progress indicator */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Typography
                                                                variant="h6"
                                                                component="div"
                                                                sx={{
                                                                    fontWeight: 600,
                                                                    color: 'text.primary',
                                                                    fontSize: '1.125rem',
                                                                }}
                                                            >
                                                                {course.course_title}
                                                            </Typography>
                                                            <Typography
                                                                variant="body2"
                                                                sx={{ color: 'text.secondary' }}
                                                            >
                                                                课程进度
                                                            </Typography>
                                                        </Box>

                                                        {/* Progress bar */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Box
                                                                sx={{
                                                                    display: 'flex',
                                                                    justifyContent: 'space-between',
                                                                    alignItems: 'center',
                                                                    mb: 1,
                                                                }}
                                                            >
                                                                <Typography
                                                                    variant="body2"
                                                                    sx={{
                                                                        color: 'text.secondary',
                                                                    }}
                                                                >
                                                                    {course.progress_percentage}%
                                                                </Typography>
                                                                <Typography
                                                                    variant="caption"
                                                                    sx={{
                                                                        color: 'text.disabled',
                                                                    }}
                                                                >
                                                                    完成进度
                                                                </Typography>
                                                            </Box>
                                                            <Box
                                                                sx={{
                                                                    height: 8,
                                                                    borderRadius: 4,
                                                                    backgroundColor: theme.palette.mode === 'dark'
                                                                        ? theme.palette.grey[800]
                                                                        : theme.palette.grey[200],
                                                                    overflow: 'hidden',
                                                                }}
                                                            >
                                                                <Box
                                                                    sx={{
                                                                        height: '100%',
                                                                        width: `${course.progress_percentage}%`,
                                                                        background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                                                                        transition: 'width 0.6s ease',
                                                                        borderRadius: 4,
                                                                    }}
                                                                />
                                                            </Box>
                                                        </Box>

                                                        {/* Next chapter and button */}
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                            <Box>
                                                                <Typography
                                                                    variant="body2"
                                                                    sx={{
                                                                        color: 'text.secondary',
                                                                        mt: 1,
                                                                    }}
                                                                >
                                                                    下一章：{course.next_chapter?.title || '暂无'}
                                                                </Typography>
                                                            </Box>
                                                            <Button
                                                                variant="contained"
                                                                size="small"
                                                                startIcon={<PlayArrowIcon />}
                                                                onClick={() =>
                                                                    navigate(`/courses/${course.course}/chapters/${course.next_chapter?.id}`)
                                                                }
                                                                disabled={!course.next_chapter}
                                                                sx={{
                                                                    background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                                                                    color: 'common.white',
                                            borderRadius: 2,
                                            boxShadow: theme.shadows[2],
                                            fontWeight: 600,
                                            transition: 'all 0.2s ease',
                                            '&:hover': {
                                                transform: 'scale(1.05)',
                                                boxShadow: theme.shadows[3],
                                                background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                                            },
                                                                }}
                                                            >
                                                                继续学习
                                                            </Button>
                                                        </Box>
                                                    </Card>
                                                </Grid>
                                            ))
                                        ) : (
                                            <Grid size={12}>
                                                <Typography color="text.secondary">暂无已报名课程</Typography>
                                            </Grid>
                                        )
                                    )
                                }}
                            />
                        </React.Suspense>
                    </Grid>
                </CardContent>
            </Card>

            <Grid container spacing={3}>
                {/* 第二部分：待解决问题 */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                                <QuizIcon sx={{ mr: 1 }} /> 待解决问题
                            </Typography>
                            <List dense>
                                <React.Suspense fallback={<UnfinishedProblemsSkeleton />}>
                                    <Await
                                        resolve={unfinished_problems}
                                        children={(resolvedProblems) => {
                                            if ('status' in resolvedProblems) {
                                                return (
                                                    <ResolveError status={resolvedProblems.status} message={resolvedProblems.message}>
                                                        <ListItem>
                                                            <ListItemText primary="无法加载未完成题目 😬" slotProps={{ primary: { color: "error" } }} />
                                                        </ListItem>
                                                    </ResolveError>)
                                            }
                                            return (
                                                resolvedProblems.results.length > 0 ? (
                                                    resolvedProblems.results.map((prob) => (
                                                        <React.Fragment key={prob.id}>
                                                            <ListItem
                                                                sx={{
                                                                    padding: '0',
                                                                    '& .MuiListItemAvatar-root': {
                                                                        minWidth: 40,
                                                                    },
                                                                    transition: 'all 0.2s ease',
                                                                    '&:hover': {
                                                                        backgroundColor: theme.palette.action.hover,
                                                                    },
                                                                }}
                                                            >
                                                                <ListItemIcon>
                                                                    {getProblemStatusIcon(prob.status)}
                                                                </ListItemIcon>
                                                                <ListItemText
                                                                    primary={
                                                                        <Stack direction="row" spacing={1} alignItems="center">
                                                                            <Typography
                                                                                variant="subtitle2"
                                                                                sx={{
                                                                                    fontWeight: 600,
                                                                                    color: 'text.primary',
                                                                                    mr: 0.5,
                                                                                }}
                                                                            >
                                                                                {prob.problem_title}
                                                                            </Typography>
                                                                            {getDifficultyLabel(prob.problem_difficulty)}
                                                                            {getProblemStatusChip(prob.status)}
                                                                            <Chip
                                                                                label={prob.problem_type === 'algorithm' ? '算法题' : '选择题'}
                                                                                size="small"
                                                                                variant="outlined"
                                                                                color="info"
                                                                            />
                                                                        </Stack>
                                                                    }
                                                                    secondary={
                                                                        <Typography
                                                                            variant="body2"
                                                                            sx={{
                                                                                color: 'text.secondary',
                                                                                fontSize: '0.875rem',
                                                                            }}
                                                                        >
                                                                            {prob.problem_type === 'algorithm' ? '点击提交代码' : '点击作答'}
                                                                        </Typography>
                                                                    }
                                                                />
                                                                <Button
                                                                    size="small"
                                                                    variant="outlined"
                                                                    color="primary"
                                                                    startIcon={prob.problem_type === 'algorithm' ? <CodeIcon /> : <QuizIcon />}
                                                                    onClick={() => navigate(`/problems/${prob.problem}`)}
                                                                    sx={{
                                                                        borderRadius: 2,
                                                                        fontWeight: 500,
                                                                        transition: 'all 0.2s ease',
                                                                        '&:hover': {
                                                                            backgroundColor: 'primary.main',
                                                                            borderColor: 'primary.main',
                                                                            color: 'common.white',
                                                                        },
                                                                    }}
                                                                >
                                                                    {prob.status === 'solved' ? '查看' : '开始'}
                                                                </Button>
                                                            </ListItem>
                                                            <Divider variant="inset" component="li" sx={{ margin: 0 }} />
                                                        </React.Fragment>
                                                    ))
                                                ) : (
                                                    <ListItem>
                                                        <ListItemText primary="暂无未完成题目" slotProps={{ primary: { color: "text.secondary" } }} />
                                                    </ListItem>
                                                )
                                            )
                                        }}
                                    />
                                </React.Suspense>
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* 第三部分：最新讨论 */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        {/* <CardContent>
                            <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                                <ForumIcon sx={{ mr: 1 }} /> 最新讨论
                            </Typography>
                            <List dense>
                                {recentDiscussions.map((thread) => (
                                    <React.Fragment key={thread.id}>
                                        <ListItem>
                                            <Avatar sx={{ bgcolor: 'grey.200', color: 'text.primary', mr: 2 }}>
                                                {thread.author.charAt(0)}
                                            </Avatar>
                                            <ListItemText
                                                primary={thread.title}
                                                secondary={`${thread.author} · ${thread.createdAt} · ${thread.replies} 条回复`}
                                            />
                                        </ListItem>
                                        <Divider variant="inset" component="li" />
                                    </React.Fragment>
                                ))}
                            </List>
                            <CardActions>
                                <Button size="small" onClick={() => console.log('查看全部讨论')}>
                                    查看全部
                                </Button>
                            </CardActions>
                        </CardContent> */}
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}





const EnrolledCoursesSkeleton = () => {
    return (
        <Grid container spacing={2}>
            {/* 渲染两个卡片，xs 下堆叠，md+ 并排 */}
            <Grid size={{ xs: 12, md: 6 }}>
                <CourseCardSkeleton theme={useTheme()} />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
                <CourseCardSkeleton theme={useTheme()} />
            </Grid>
        </Grid>
    );
};

// 单个课程卡片骨架
const CourseCardSkeleton = ({ theme }: { theme: Theme }) => {
    return (
        <Box
            sx={{
                p: 3,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                bgcolor: 'background.paper',
                boxShadow: theme.shadows[1],
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box sx={{ flex: 1 }}>
                    <Skeleton variant="text" width="70%" height={28} />
                    <Skeleton variant="text" width="50%" height={20} sx={{ mt: 1 }} />
                </Box>
                <Skeleton variant="rounded" width={80} height={32} />
            </Box>
            <Skeleton variant="text" width="100%" height={20} sx={{ mb: 1 }} />
            <Skeleton variant="text" width="60%" height={18} />
        </Box>
    );
};
const UnfinishedProblemsSkeleton = () => {
    const theme = useTheme();
    return (
        <>
            {[...Array(3)].map((_, i) => (
                <ProblemListItemSkeleton key={i} theme={theme} />
            ))}
        </>
    );
}
const ProblemListItemSkeleton = ({ theme }: { theme: Theme }) => {
    return (
        <>
            <ListItem>
                <ListItemIcon>
                    <Skeleton variant="circular" width={24} height={24} />
                </ListItemIcon>
                <ListItemText
                    primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Skeleton variant="text" width="40%" height={20} />
                            <Skeleton variant="rounded" width={40} height={20} />
                            <Skeleton variant="rounded" width={60} height={20} />
                        </Box>
                    }
                    secondary={<Skeleton variant="text" width="30%" height={16} sx={{ color: theme.palette.action.hover }} />}
                />
                <Skeleton variant="rounded" width={60} height={32} />
            </ListItem>
            <Divider variant="inset" component="li" />
        </>
    );
};