import { Avatar, Box, Button, Card, CardActions, CardContent, Chip, Divider, Grid, List, ListItem, ListItemIcon, ListItemText, Skeleton, Stack, Typography } from "@mui/material";
import type { Route } from "./+types/_layout.home";
import React from "react";
import {
    Book as BookIcon,
    Code as CodeIcon,
    Quiz as QuizIcon,
    Forum as ForumIcon,
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
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
    const http = createHttp(request);
    const enrollments = http.get<Page<Enrollment>>('enrollments/');
    const unfinished_problems = http.get<Page<ProblemProgress>>('problem-progress/?status_not=solved');
    return { enrollments, unfinished_problems }
})


export default function Home({ params, loaderData }: Route.ComponentProps) {
  
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
                                errorElement={
                                    <ResolveError>
                                        <Grid size={12}>
                                            <Typography color="error">无法加载课程列表 😬</Typography>
                                        </Grid>
                                    </ResolveError>

                                }
                                children={(resolvedEnrolledCourses) => (
                                    resolvedEnrolledCourses.results.length > 0 ? (
                                        resolvedEnrolledCourses.results.map((course) => (
                                            <Grid size={{ xs: 12, md: 6 }} key={course.id}>
                                                <Box
                                                    sx={{
                                                        p: 2,
                                                        border: '1px solid',
                                                        borderColor: 'divider',
                                                        borderRadius: 1,
                                                        bgcolor: 'background.paper',
                                                    }}
                                                >
                                                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                                                        <Box>
                                                            <Typography variant="subtitle1">{course.course_title}</Typography>
                                                            <Typography variant="body2" color="textSecondary">
                                                                进度: {course.progress_percentage}%
                                                            </Typography>
                                                        </Box>
                                                        <Button
                                                            variant="contained"
                                                            size="small"
                                                            startIcon={<PlayArrowIcon />}
                                                            onClick={() =>
                                                                navigate(`/courses/${course.course}/chapters/${course.next_chapter?.id}`)
                                                            }
                                                            disabled={!course.next_chapter} // 防止 next_chapter 为 null 时出错
                                                        >
                                                            继续学习
                                                        </Button>
                                                    </Stack>
                                                    <Typography variant="body2" mt={1} color="textSecondary">
                                                        下一章：{course.next_chapter?.title || '暂无'}
                                                    </Typography>
                                                </Box>
                                            </Grid>
                                        ))
                                    ) : (
                                        <Grid size={12}>
                                            <Typography color="text.secondary">暂无已报名课程</Typography>
                                        </Grid>
                                    )
                                )}
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
                                        errorElement={
                                            <ResolveError>
                                                <ListItem>
                                                    <ListItemText primary="无法加载未完成题目 😬" slotProps={{primary:{color: "error" }}} />
                                                </ListItem>
                                            </ResolveError>

                                        }
                                        children={(resolvedProblems) => (
                                            resolvedProblems.results.length > 0 ? (
                                                resolvedProblems.results.map((prob) => (
                                                    <React.Fragment key={prob.id}>
                                                        <ListItem>
                                                            <ListItemIcon>
                                                                {getProblemStatusIcon(prob.status)}
                                                            </ListItemIcon>
                                                            <ListItemText
                                                                primary={
                                                                    <Stack direction="row" spacing={1} alignItems="center">
                                                                        <span>{prob.problem_title}</span>
                                                                        {getDifficultyLabel(prob.problem_difficulty)}
                                                                        <Chip
                                                                            label={prob.problem_type === 'algorithm' ? '算法题' : '选择题'}
                                                                            size="small"
                                                                            variant="outlined"
                                                                        />
                                                                    </Stack>
                                                                }
                                                                secondary={prob.problem_type === 'algorithm' ? '点击提交代码' : '点击作答'}
                                                            />
                                                            <Button
                                                                size="small"
                                                                variant="outlined"
                                                                startIcon={prob.problem_type === 'algorithm' ? <CodeIcon /> : <QuizIcon />}
                                                                onClick={() => navigate(`/problems/${prob.problem}`)}
                                                            >
                                                                {prob.status === 'solved' ? '查看' : '开始'}
                                                            </Button>
                                                        </ListItem>
                                                        <Divider variant="inset" component="li" />
                                                    </React.Fragment>
                                                ))
                                            ) : (
                                                <ListItem>
                                                    <ListItemText primary="暂无未完成题目" slotProps={{primary:{color: "text.secondary" }}}  />
                                                </ListItem>
                                            )
                                        )}
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
                <CourseCardSkeleton />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
                <CourseCardSkeleton />
            </Grid>
        </Grid>
    );
};

// 单个课程卡片骨架
const CourseCardSkeleton = () => {
    return (
        <Box
            sx={{
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: 'background.paper',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Box>
                    <Skeleton variant="text" width="70%" height={24} />
                    <Skeleton variant="text" width="50%" height={18} sx={{ mt: 0.5 }} />
                </Box>
                <Skeleton variant="rounded" width={90} height={32} />
            </Box>
            <Skeleton variant="text" width="60%" height={18} />
        </Box>
    );
};
const UnfinishedProblemsSkeleton = () => {
    return (
        <>
            {[...Array(3)].map((_, i) => (
                <ProblemListItemSkeleton key={i} />
            ))}
        </>
    );
}
const ProblemListItemSkeleton = () => {
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
                    secondary={<Skeleton variant="text" width="30%" height={16} />}
                />
                <Skeleton variant="rounded" width={60} height={32} />
            </ListItem>
            <Divider variant="inset" component="li" />
        </>
    );
};