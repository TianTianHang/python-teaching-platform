import { Box, Button, CircularProgress, Divider, Grid, List, TextField, useTheme } from "@mui/material";
import type { Thread } from "~/types/thread";
import ThreadItem from "./ThreadItem";
import { useFetcher, useNavigate } from "react-router";
import { useEffect, useState } from "react";


import { MdEditor } from 'md-editor-rt';
import 'md-editor-rt/lib/style.css';
import { handleUpload } from "~/utils/image";
import { transitions, spacing } from "~/design-system/tokens";



export default function DiscussionForum({
  threads: initialThreads,
  problemId,
  chapterId,
  courseId,
}: {
  threads: Thread[];
  problemId?: number;
  chapterId?: number;
  courseId?: number;
}) {
  const threadFetcher = useFetcher<{
    data: Thread[];
    currentPage: number;
    totalItems: number;
    actualPageSize: number;
  }>();

  // 本地状态管理已加载的线程和分页信息
  const [loadedThreads, setLoadedThreads] = useState<Thread[]>(initialThreads);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [totalItems, setTotalItems] = useState<number>(initialThreads.length); // 跟踪总数，用于调试和未来功能
  const [hasMore, setHasMore] = useState<boolean>(initialThreads.length >= 10); // 如果初始数据少于页大小，说明没有更多数据

  const [title, setTitle] = useState<string>("");
  const [content, setContent] = useState<string>("");
  const theme = useTheme();
  // 首次加载后更新 totalItems 和 hasMore
  useEffect(() => {
    if (threadFetcher.state === "idle" && threadFetcher.data) {
      const { data, totalItems: fetchedTotal } = threadFetcher.data;
      // 使用 prev 模式避免闭包陷阱，正确计算 hasMore
      setLoadedThreads((prev) => {
        const existingIds = new Set(prev.map(item => item.id)); // 替换 `item.id` 为你实际的唯一字段名

        // 过滤掉已存在的项
        const uniqueNewData = data.filter(item => !existingIds.has(item.id));
        const updatedThreads= [...prev, ...uniqueNewData];
        const newLength = updatedThreads.length;
      
        setHasMore(newLength < fetchedTotal);
        return updatedThreads;
      });
      setTotalItems(fetchedTotal);
    }
  }, [threadFetcher.state, threadFetcher.data]);


  const handleLoadMore = () => {
    // 根据已加载的数据长度计算当前页码，避免使用过期的 currentPage
    const itemsPerPage = 10;
    const currentPage = Math.floor(loadedThreads.length / itemsPerPage);
    const nextPage = currentPage + 1;
    const queryParams = new URLSearchParams();
    queryParams.set("page", nextPage.toString());
    queryParams.set("page_size", itemsPerPage.toString()); // 固定或可配置
    if (problemId) queryParams.set("problem", problemId.toString());
    if (chapterId) queryParams.set("chapter", chapterId.toString());
    if (courseId) queryParams.set("course", courseId.toString());

    threadFetcher.load(`/threads/?${queryParams.toString()}`);
  };

  const isLoading = threadFetcher.state !== "idle";
  const navigate = useNavigate()
  const publishFetcher = useFetcher<Thread>();
  function handlePublish(): void {
    publishFetcher.submit({
      title, content,
      ...(problemId && { problemId }),
      ...(chapterId && { chapterId }),
      ...(courseId && { courseId })
    },
      { method: "POST", action: "/threads/" })
  }
  useEffect(() => {
    if (publishFetcher.state === "idle" && publishFetcher.data) {

      setLoadedThreads(prev => {
        const newData = publishFetcher.data;
        if (!newData) return prev; // 防御性编程
        // 新增帖子后，总数应该增加
        setTotalItems(total => total + 1);
        // 如果之前认为没有更多数据，需要重新评估
        setHasMore(true);
        return [newData, ...prev];
      });
    }
  }, [publishFetcher.state, publishFetcher.data]);
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {/* 评论输入框 */}
      {/* 标题 + 发布按钮同行 */}
      <Grid container spacing={spacing.sm} mb={spacing.md}>
        <Grid size={{ xs: 12, md: 10 }} >
          <TextField
            fullWidth
            label="标题"
            variant="standard"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="请输入标题"
          />
        </Grid>
        <Grid size="grow" />
        <Grid size={{ xs: 1, md: 2 }}>
          <Button
            fullWidth
            variant="contained"
            color="primary"
            onClick={handlePublish}
            size="large"
            loading={publishFetcher.state !== "idle"}
          >
            发布
          </Button>
        </Grid>
      </Grid>
      {/* Markdown 编辑器 */}
      <Box mt={0}>
        <MdEditor
          value={content}
          onChange={(value) => setContent(value)}
          toolbars={['italic', 'underline', 'bold', "code", "image", "=", "preview"]}
          preview={false}
          onUploadImg={handleUpload}
          previewTheme={'github'}
          theme={theme.palette.mode === 'dark' ? 'dark' : 'light'}
          style={{transition:transitions.themeSwitch}}
        />
      </Box>

      <Divider />
      {/* 主题贴列表 */}
      <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {loadedThreads.map((thread) => (
          <div key={`thread-${thread.id}`}>
          <ThreadItem thread={thread} onClick={() => navigate(`/threads/${thread.id}`)}/>
          <Divider variant="inset" component="div"/>
          </div>

        ))}
      </List>

      {/* 加载更多按钮 —— 仅在还有数据且未加载完时显示 */}
      {hasMore && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: spacing.sm }}>
          <Button
            variant="outlined"
            onClick={handleLoadMore}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? '加载中...' : '加载更多'}
          </Button>
        </Box>
      )}
    </Box>
  );
}