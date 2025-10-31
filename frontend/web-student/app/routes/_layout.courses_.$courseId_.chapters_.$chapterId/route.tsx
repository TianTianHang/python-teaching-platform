import {
  Box,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Drawer,
  Toolbar,
  Divider,
  useTheme,
  useMediaQuery,
  Grid,
  Button,
} from '@mui/material';
import type { Chapter, ChoiceProblem, Problem } from '~/types/course'; // 确保路径正确
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import { createHttp, createResponse } from '~/utils/http/index.server';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ProblemRenderer from '~/components/Problem'; // 确保 ProblemRenderer 的导入路径正确
import type { Page } from '~/types/page';
import ChoiceProblemCmp from '~/components/Problem/ChoiceProblemCmp';
import { useFetcher, useNavigate } from 'react-router';
import { useGolbalStore } from '~/stores/globalStore';
import { useEffect } from 'react';
import { showNotification } from '~/components/Notification';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.chapter.title || "Error" },
  ];
}
export async function action({ request, params }: Route.ActionArgs) {
  const http = createHttp(request);
  await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: true })
  return {message:"已完成"}
}
export async function loader({ params, request }: Route.LoaderArgs) {
  const http = createHttp(request);
  const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
  if (chapter.status == "not_started") {
    await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: false })
  }
  const problems = await http.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems`);
  const courseChapters = await http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`);
  return createResponse(request, { chapter, problems, courseChapters });
}

export default function ChapterDetail({ loaderData, params, actionData }: Route.ComponentProps) {
  const { chapter, problems, courseChapters } = loaderData;
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  if(actionData?.message){
    showNotification("success","",actionData.message)
  }
  const handleChapterSelect = (chapterId: number) => {
    navigate(`/courses/${params.courseId}/chapters/${chapterId}`);
  };

  const { markdownStyle } = useGolbalStore()
  const fetcher = useFetcher()
  const sidebarContent = (
    <>
      <Toolbar />
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          课程章节
        </Typography>
        <Divider sx={{ mb: 2 }} />
      </Box>
      <List>
        {courseChapters.results.map((ch) => (
          <ListItem
            key={ch.id}
            disablePadding
            sx={{
              backgroundColor: ch.id === chapter.id ? 'action.selected' : 'transparent',
              '&:hover': { backgroundColor: 'action.hover' }
            }}
          >
            <ListItemButton
              onClick={() => handleChapterSelect(ch.id)}
              selected={ch.id === chapter.id}
            >
              <ListItemText
                primary={ch.title}
                slotProps={{
                  primary: {
                    noWrap: true,
                    sx: {
                      fontWeight: ch.id === chapter.id ? 'bold' : 'normal',
                    }
                  }
                }}

              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );

  return (
    <Container maxWidth={false} sx={{ mt: 4, mb: 4, display: 'flex', maxWidth: '100%' }}>
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={true}
          onClose={() => { }}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8 },
          }}
        >
          {sidebarContent}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8, borderRight: '1px solid rgba(0, 0, 0, 0.12)' },
          }}
        >
          {sidebarContent}
        </Drawer>
      )}

      {/* 主内容区 */}
      <Box component="main" sx={{ flexGrow: 1, ml: isMobile ? 0 : 35, p: 2 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {chapter.title}
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            课程: {chapter.course_title}
          </Typography>
          {/* 使用 ReactMarkdown 渲染 chapter.content */}
          <Box sx={markdownStyle}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {chapter.content}
            </ReactMarkdown>
          </Box>
          {chapter.status !== 'completed' && (
            <Box sx={{ mt: 2 }}>
              <fetcher.Form method="post" action={`/courses/${params.courseId}/chapters/${params.chapterId}/`}>
                <input type="hidden" name="completed" value="true" />
                <Button
                  type="submit"
                  variant="contained"
                  color="success"
                  disabled={fetcher.state !== 'idle'}
                >
                  {fetcher.state !== 'idle' ? '提交中...' : '标记为已完成'}
                </Button>
              </fetcher.Form>
            </Box>
          )}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Typography variant="caption" color="text.disabled">
              创建于: {formatDateTime(chapter.created_at)}
            </Typography>
            <Typography variant="caption" color="text.disabled">
              最后更新: {formatDateTime(chapter.updated_at)}
            </Typography>
          </Box>
        </Paper>

        {/* 这里渲染题目列表，不使用 ProblemListRenderer */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 2 }}>
            相关题目
          </Typography>
          {problems && problems.results.length > 0 ? (
            <Box> {/* 使用 Box 而不是 List 来包含多个 ProblemRenderer */}
              {problems.results.map((problem, index) => {
                if (problem.type == 'choice') {
                  return (
                    <ChoiceProblemCmp problem={problem as ChoiceProblem} key={index} />
                  )
                } else {
                  return (
                    <Box key={problem.id} sx={{ mb: 3 }}> {/* 为每个 ProblemRenderer 添加一个外层 Box 并设置底部边距 */}
                      <ProblemRenderer problem={problem} key={index} />
                    </Box>
                  )
                }
              })}
            </Box>
          ) : (
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                本章节暂无相关题目。
              </Typography>
            </Paper>
          )}
        </Box>
      </Box>
    </Container>
  );
}
