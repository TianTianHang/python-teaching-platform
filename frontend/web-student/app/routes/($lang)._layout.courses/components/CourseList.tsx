import {
    Box,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Container,
    CardActionArea,
    Chip,
    Stack,
} from '@mui/material';
import { useNavigate } from 'react-router';
import type { Course } from '~/types/course';
import { formatDateTime } from '~/utils/time';

export default function CourseList({ courses, lang }: { courses: Course[], lang: string }) {
    const navigate = useNavigate();
    const handleClick = (id: number) => {
        navigate(`/${lang}/courses/${id}`)
    }
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                课程列表
            </Typography>
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
                <Grid container spacing={3}>
                    {courses.map((course) => (
                        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={course.id}>
                            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', boxShadow: 3, transition: 'transform 0.3s', '&:hover': { transform: 'translateY(-8px)' } }}>
                                <CardActionArea onClick={() => handleClick(course.id)} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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
                        </Grid>
                    ))}
                </Grid>
            )}
        </Container>
    );
}