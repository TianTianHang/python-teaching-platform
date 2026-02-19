import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Toolbar,
  CircularProgress,
} from '@mui/material';
import type { Chapter } from '~/types/course';
import type { Page } from '~/types/page';
import { useInfiniteScroll } from '~/hooks/useInfiniteScroll';

interface ChapterSidebarProps {
  initialData: Page<Chapter>;
  courseId: string;
  currentChapterId: number;
  onChapterSelect: (chapterId: number) => void;
}

export function ChapterSidebar({
  initialData,
  courseId,
  currentChapterId,
  onChapterSelect,
}: ChapterSidebarProps) {
  // Initialize infinite scroll
  const infiniteScroll = useInfiniteScroll<Chapter>({
    initialData,
    extractData: (data) => data.chapters,
    getNextPageUrl: (page, pageSize) =>
      `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
  });

  return (
    <>
      <Toolbar />
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          课程章节
        </Typography>
        <Divider sx={{ mb: 2 }} />
      </Box>
      <List sx={{ flex: 1, overflow: 'auto' }}>
        {infiniteScroll.items.map((chapter) => (
          <ListItem
            key={chapter.id}
            disablePadding
            sx={{
              backgroundColor: chapter.id === currentChapterId ? 'action.selected' : 'transparent',
              '&:hover': { backgroundColor: 'action.hover' }
            }}
          >
            <ListItemButton
              onClick={() => onChapterSelect(chapter.id)}
              selected={chapter.id === currentChapterId}
            >
              <ListItemText
                primary={chapter.title}
                slotProps={{
                  primary: {
                    noWrap: true,
                    sx: {
                      fontWeight: chapter.id === currentChapterId ? 'bold' : 'normal',
                    }
                  }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}

        {/* Sentinel for infinite scroll */}
        <Box ref={infiniteScroll.sentinelRef} />

        {infiniteScroll.loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 1 }}>
            <CircularProgress size={20} />
          </Box>
        )}

        {infiniteScroll.error && (
          <Box sx={{ textAlign: 'center', py: 1 }}>
            <Typography variant="body2" color="error" sx={{ mb: 0.5 }}>
              加载失败
            </Typography>
            <Typography
              variant="body2"
              color="primary"
              sx={{ cursor: 'pointer', textDecoration: 'underline' }}
              onClick={infiniteScroll.retry}
            >
              重试
            </Typography>
          </Box>
        )}

        {!infiniteScroll.hasMore && infiniteScroll.items.length > 0 && (
          <Box sx={{ py: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
              已加载全部 {infiniteScroll.items.length} 个章节
            </Typography>
          </Box>
        )}
      </List>
    </>
  );
}
