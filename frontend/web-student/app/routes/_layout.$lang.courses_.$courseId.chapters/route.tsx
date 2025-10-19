import {
  Box,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';
import type { Chapter } from "~/types/course";
import type { Route } from "./+types/route"
import http from "~/utils/http";
import type { Page } from "~/types/page";
import { useState } from 'react';
import { useNavigate } from 'react-router';


export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const chapters = await http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`);
  return chapters;
}
export default function ChapterPage({ loaderData, params }: Route.ComponentProps) {
  
  const chapters = loaderData.results;
  const title = chapters[0].course_title;
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
    <Container maxWidth="sm" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3}>
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h5" component="h2">
            {title}
          </Typography>
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