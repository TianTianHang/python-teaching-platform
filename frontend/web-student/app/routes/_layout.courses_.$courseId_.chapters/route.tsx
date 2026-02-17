import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Grid,
  Button,
  Chip,
  IconButton,
  Tooltip,
  type ChipProps,
} from '@mui/material';
import type { Chapter, Course } from "~/types/course";
import type { Route } from "./+types/route"
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { useNavigate } from 'react-router';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import { Lock as LockIcon, Info as InfoIcon } from '@mui/icons-material';
import { formatTitle, PAGE_TITLES } from '~/config/meta';

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
  //console.log("Chapters:", chapters);
  const title = loaderData.course.title
  const navigate = useNavigate();
  const pageTitle = title ? PAGE_TITLES.chapters(title) : '章节列表';
  const handleClick = (id: number, isLocked: boolean) => {
    if (isLocked) {
      navigate(`/courses/${params.courseId}/chapters/${id}/locked`);
    } else {
      navigate(`/courses/${params.courseId}/chapters/${id}`);
    }
  };

  // Filter unlocked and locked chapters
  const unlockedChapters = chapters.filter(chapter => !chapter.is_locked);
  const lockedChapters = chapters.filter(chapter => chapter.is_locked);

  if (!chapters || chapters.length === 0) {
    return (
      <>
        <title>{formatTitle(pageTitle)}</title>
        <PageContainer maxWidth="sm">
          <SectionContainer spacing="md" variant="card">
            <Typography variant="h6" color="text.secondary" align="center" sx={{ py: spacing.lg }}>
              暂无章节
            </Typography>
            <Typography variant="body2" color="text.disabled" align="center">
              请稍后回来查看，或联系管理员。
            </Typography>
          </SectionContainer>
        </PageContainer>
      </>
    );
  }
  return (
    <>
      <title>{formatTitle(pageTitle)}</title>
      <PageContainer maxWidth="lg">
        <PageHeader
          title="章节列表"
          subtitle={`课程: ${title}`}
        />
      <SectionContainer spacing="md" variant="card">
        <Box sx={{ p: { xs: 2, sm: 3 }, borderBottom: 1, borderColor: 'divider' }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid>
              <Button
                variant="outlined"
                onClick={() => navigate(`/courses/${params.courseId}`)}
                                sx={{
                  color: 'text.primary',
                  borderColor: 'divider',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                返回课程主页
              </Button>
            </Grid>
          </Grid>
        </Box>
        <List>
          {/* Unlocked chapters */}
          {unlockedChapters.map((chapter) => (
            <ListItem
              key={chapter.id}
              disablePadding
              onClick={() => handleClick(chapter.id, chapter.is_locked)}
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

          {/* Locked chapters */}
          {lockedChapters.map((chapter) => {
            const prerequisiteCount = chapter.prerequisite_progress?.total || 0;
            return (
              <ListItem
                key={`locked-${chapter.id}`}
                disablePadding
                sx={{
                  '&:not(:last-child)': {
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                  },
                  opacity: 0.7,
                  cursor: 'default',
                  py: 1,
                  px: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                  <LockIcon
                    color="disabled"
                    fontSize="small"
                  />
                  <ListItemText
                    primary={
                      <Typography variant="body1" color="text.secondary">
                        {chapter.title}
                      </Typography>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" component="span" color="text.disabled">
                          {chapter.course_title}
                        </Typography>
                        {prerequisiteCount > 0 && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={`完成 ${prerequisiteCount} 个前置章节`}
                              size="small"
                              color="default"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        )}
                      </Box>
                    }
                  />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, opacity: 1 }}>
                  <Chip
                    label="已锁定"
                    size="small"
                    color="default"
                    variant="outlined"
                  />
                  <Tooltip title="查看解锁条件">
                    <IconButton
                      size="small"
                      color="info"
                      sx={{ p: 0.5 }}
                      edge="end"
                      onClick={() => handleClick(chapter.id, chapter.is_locked)}
                    >
                      <InfoIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItem>
            );
          })}
        </List>
      </SectionContainer>
    </PageContainer>
    </>
  );


}