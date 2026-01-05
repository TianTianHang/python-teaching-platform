import {
    Box,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Typography,
    CardActionArea,
    Stack,
    Pagination,
    Skeleton,
    Button,
    Chip,
    useTheme,
} from '@mui/material';
import { useNavigate } from 'react-router';
import type { Course } from '~/types/course';
import { formatDateTime } from '~/utils/time';

export default function CourseList({ courses, page, onPageChange }: {
    courses: Course[],
    page: { currentPage: number, totalItems: number, totalPages: number },
    onPageChange?: (page: number) => void;
}) {
    const theme = useTheme();
    const navigate = useNavigate();
    const handleClick = (id: number) => {
        navigate(`/courses/${id}`)
    }
    const handlePaginationChange = (_event: React.ChangeEvent<unknown>, value: number) => {
        onPageChange?.(value); // 安全调用（如果传入了）
    };
    return (

        <>
            {courses.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Typography variant="h6" color="textSecondary">
                        暂无可用课程
                    </Typography>
                    <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
                        请稍后再来查看，或联系管理员添加课程
                    </Typography>
                </Box>
            ) : (
                <>
                    <Grid container spacing={3}>
                        {courses.map((course) => (
                            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={course.id}>
                                <CourseCard course={course} onClick={handleClick} theme={theme} />
                            </Grid>
                        ))}
                    </Grid>
                    {/* 分页组件 */}
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6, mb: 2 }}>
                        <Pagination
                            count={page.totalPages}
                            page={page.currentPage}
                            onChange={handlePaginationChange}
                            color="primary"
                            size="large"
                            shape="rounded"
                            showFirstButton
                            showLastButton
                            siblingCount={1}
                            boundaryCount={1}
                            sx={{
                                '& .MuiPaginationItem-root': {
                                    borderRadius: 1,
                                    margin: '0 2px',
                                },
                                '& .MuiButtonBase-root': {
                                    fontSize: '1rem',
                                    fontWeight: 500,
                                },
                            }}
                        />
                    </Box>
                </>

            )}

        </>

    );
}

const CourseCard = ({ course, onClick, theme }: { course: Course, onClick: (id: number) => void, theme?: any }) => {
    const handleClick = () => {
        if (onClick) onClick(course.id);
    };

    return (
        <Card
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: theme?.shadows[4] || '0 4px 8px rgba(0,0,0,0.12)',
                borderRadius: 2,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                border: `1px solid ${theme?.palette.divider || 'rgba(0,0,0,0.1)'}`,
                '&:hover': {
                    boxShadow: theme?.shadows[8] || '0 8px 16px rgba(0,0,0,0.16)',
                    transform: 'translateY(-4px)',
                },
                '&:hover::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    background: `linear-gradient(90deg, ${theme?.palette.primary.main || '#5B4DFF'}, ${theme?.palette.primary.dark || '#3A2BD9'})`,
                },
            }}
        >
            <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column', position: 'relative' }}>
                <CardHeader
                    title={
                        <Typography
                            variant="h6"
                            component="h3"
                            sx={{
                                fontWeight: 700,
                                color: theme?.palette.text.primary || 'inherit',
                                fontSize: '1.125rem',
                                lineHeight: 1.4,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                            }}
                        >
                            {course.title}
                        </Typography>
                    }
                    subheader={
                        <>
                            <Typography
                                variant="caption"
                                color={theme?.palette.text.secondary || 'textSecondary'}
                                sx={{ display: 'block', mb: 1 }}
                            >
                                创建于: {formatDateTime(course.created_at)}
                            </Typography>
                            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                                {/* 可选：动态渲染标签，例如 course.tags.map(...) */}
                                {/* <Chip label="Python" size="small" variant="outlined" color="primary" /> */}
                            </Stack>
                        </>
                    }
                    sx={{ pb: 1 }}
                />
                <CardContent sx={{ flexGrow: 1, pt: 0 }}>
                    <Typography
                        variant="body2"
                        color={theme?.palette.text.secondary || 'text.secondary'}
                        sx={{
                            minHeight: 80,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 4,
                            WebkitBoxOrient: 'vertical',
                            lineHeight: 1.5,
                        }}
                    >
                        {course.description || '暂无描述'}
                    </Typography>
                </CardContent>
                <Box sx={{ px: 2, pb: 2, pt: 0 }}>
                    <Typography
                        variant="caption"
                        color={theme?.palette.text.disabled || 'text.disabled'}
                        sx={{ display: 'block' }}
                    >
                        最后更新: {formatDateTime(course.updated_at)}
                    </Typography>
                </Box>
            </CardActionArea>
        </Card>
    );
};

export function CourseListkeleton() {
    return (
        <Grid container spacing={3}>
            {[...Array(3)].map((_, index) => (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
                    <Skeleton variant="rounded">
                        <CourseCard course={{ id: 0, title: "t", description: "", recent_threads: [], created_at: "", updated_at: "" }} onClick={function (): void {
                            throw new Error('Function not implemented.');
                        }} />
                    </Skeleton>
                </Grid>
            ))}
        </Grid>

    )
}