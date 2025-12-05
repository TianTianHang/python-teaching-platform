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
} from '@mui/material';
import { useNavigate } from 'react-router';
import type { Course } from '~/types/course';
import { formatDateTime } from '~/utils/time';

export default function CourseList({ courses, page, onPageChange }: {
    courses: Course[],
    page: { currentPage: number, totalItems: number, totalPages: number },
    onPageChange?: (page: number) => void;
}) {
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
                                <CourseCard course={course} onClick={handleClick} />
                            </Grid>
                        ))}
                    </Grid>
                    {/* 分页组件 */}
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                        <Pagination
                            count={page.totalPages}
                            page={page.currentPage}
                            onChange={handlePaginationChange}
                            color="primary"
                            siblingCount={1}
                            boundaryCount={1}
                        />
                    </Box>
                </>

            )}

        </>

    );
}

const CourseCard = ({ course, onClick }: { course: Course, onClick: (id: number) => void }) => {
    const handleClick = () => {
        if (onClick) onClick(course.id);
    };

    return (
        <Card
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: 3,
                transition: 'transform 0.3s',
                '&:hover': { transform: 'translateY(-8px)' },
            }}
        >
            <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardHeader
                    title={
                        <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                            {course.title}
                        </Typography>
                    }
                    subheader={
                        <>
                            <Typography variant="caption" color="textSecondary">
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
                    <Typography variant="body2" color="text.secondary" sx={{ minHeight: 60 }}>
                        {course.description || '暂无描述'}
                    </Typography>
                </CardContent>
                <Box sx={{ px: 2, pb: 2, pt: 0 }}>
                    <Typography variant="caption" color="text.disabled">
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