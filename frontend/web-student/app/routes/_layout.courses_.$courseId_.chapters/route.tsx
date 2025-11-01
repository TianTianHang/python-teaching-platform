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
  Chip,
  type ChipProps,
} from '@mui/material';
import type { Chapter, Course } from "~/types/course";
import type { Route } from "./+types/route"
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { useNavigate } from 'react-router';
import { withAuth } from '~/utils/loaderWrapper';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.course.title || "Error" },
  ];
}
export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const course = await http.get<Course>(`/courses/${params.courseId}`);
  const chapters = await http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`);
  return { chapters, course };
})

// 状态映射（可选：美化显示文本）
const statusLabels = {
  not_started: '未开始',
  in_progress: '进行中',
  completed: '已完成',
};

// 状态颜色：显式指定类型，确保值是合法的 color 值
const statusColors: Record<string, ChipProps['color']> = {
  not_started: 'default',
  in_progress: 'warning',
  completed: 'success',
};
export default function ChapterPage({ loaderData, params }: Route.ComponentProps) {

  const chapters = loaderData.chapters.results;
  const title = loaderData.course.title
  const navigate = useNavigate();
  const handleClick = (id: number) => {
    navigate(`/courses/${params.courseId}/chapters/${id}`)
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
                onClick={() => navigate(`/courses/${params.courseId}`)}
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
                <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
                  <Chip
                    label={statusLabels[chapter.status]}
                    size="small"
                    color={statusColors[chapter.status]}
                    variant="outlined"
                  />
                </Box>
              </ListItemButton>

            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );


}