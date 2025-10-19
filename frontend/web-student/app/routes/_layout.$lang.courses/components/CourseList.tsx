import {
    Box,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Container,
    CardActionArea,
} from '@mui/material';
import { useNavigate } from 'react-router';
import type { Course } from '~/types/course';
import { formatDateTime } from '~/utils/time';

export default function CourseList({ courses, lang }: { courses: Course[], lang:string }) {
    const navigate = useNavigate();
    const handleClick = (id: number) => {
        navigate(`/${lang}/courses/${id}/chapters`)
    }
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                课程列表
            </Typography>
            <Grid container spacing={3}>
                {courses.map((course) => (
                    <Grid key={course.id}>
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardActionArea onClick={() => handleClick(course.id)}>
                                <CardHeader
                                    title={course.title}
                                    subheader={`创建于: ${formatDateTime(course.created_at)}`}
                                    slotProps={{
                                        title: { variant: 'h6' },
                                        subheader: { variant: 'body2', color: 'text.secondary' }
                                    }}
                                />
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Typography variant="body1" color="text.secondary">
                                        {course.description}
                                    </Typography>
                                </CardContent>
                                <Box sx={{ p: 2, pt: 0 }}>
                                    <Typography variant="caption" color="text.disabled">
                                        最后更新: {formatDateTime(course.updated_at)}
                                    </Typography>
                                </Box>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>

        </Container>
    );
}