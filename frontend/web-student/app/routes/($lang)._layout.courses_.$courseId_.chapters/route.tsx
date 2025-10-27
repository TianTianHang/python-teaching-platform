import {
  Box,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Grid,
  Button,
} from '@mui/material';
import type { Chapter, Course } from "~/types/course";
import type { Route } from "./+types/route"
import  { createHttp, createResponse } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { useNavigate } from 'react-router';

export function meta({loaderData}: Route.MetaArgs) {
  return [
    { title: loaderData?.course.title||"Error" },
  ];
}
export async function loader({ params,request }: Route.LoaderArgs) {
  const http = createHttp(request);
  const course = await http.get<Course>(`/courses/${params.courseId}`);
  const chapters = await http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`);
  return createResponse(request,{chapters,course});
}
export default function ChapterPage({ loaderData, params }: Route.ComponentProps) {
  
  const chapters = loaderData.chapters.results;
  const title = loaderData.course.title
  const navigate = useNavigate();
    const handleClick = (id: number) => {
        navigate(`/${params.lang}/courses/${params.courseId}/chapters/${id}`)
    }
  
  if (!chapters || chapters.length === 0) {
    return (
      <Container maxWidth="sm" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            暂无章节
          </Typography>
          <Typography variant="body2" color="text.disabled">
            请稍后回来查看，或联系管理员。
          </Typography>
        </Paper>
      </Container>
    );
  }
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3}>
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid>
              <Typography variant="h5" component="h2">
                {title}
              </Typography>
            </Grid>
            <Grid>
              <Button 
                variant="outlined" 
                onClick={() => navigate(`/${params.lang}/courses/${params.courseId}`)}
              >
                返回课程主页
              </Button>
            </Grid>
          </Grid>
        </Box>
        <List>
          {chapters.map((chapter) => (
            <ListItem
              key={chapter.id}
              disablePadding
              onClick={
                 () => handleClick(chapter.id) 
              }
              sx={{
                '&:not(:last-child)': {
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                },
              }}
            >
              <ListItemButton>
                <ListItemText
                  primary={chapter.title}
                  secondary={chapter.course_title}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );


}