import { Box, Button, CircularProgress, Divider, Grid, List, TextField } from "@mui/material";
import type { Thread } from "~/types/thread";
import ThreadItem from "./ThreadItem";
import { useFetcher, useNavigate } from "react-router";
import { useEffect, useState } from "react";


import { MdEditor } from 'md-editor-rt';
import 'md-editor-rt/lib/style.css';
import { handleUpload } from "~/utils/image";



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
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [totalItems, setTotalItems] = useState<number>(initialThreads.length); // 初始假设只有一页
  const [hasMore, setHasMore] = useState<boolean>(true); // 是否还有更多数据

  const [title, setTitle] = useState<string>("");
  const [content, setContent] = useState<string>("");
  // 首次加载后更新 totalItems 和 hasMore
  useEffect(() => {
    if (threadFetcher.state === "idle" && threadFetcher.data) {
      const { data, currentPage: fetchedPage, totalItems: fetchedTotal, actualPageSize } = threadFetcher.data;
      // TODO 加载合并
      setLoadedThreads((prev) => [...prev, ...data]);
      setCurrentPage(fetchedPage);
      setTotalItems(fetchedTotal);

      // 判断是否还有更多数据
      const loadedCount = loadedThreads.length + data.length;
      setHasMore(loadedCount < fetchedTotal);
    }
  }, [threadFetcher.state, threadFetcher.data]);


  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    const queryParams = new URLSearchParams();
    queryParams.set("page", nextPage.toString());
    queryParams.set("page_size", "10"); // 固定或可配置
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
        return [newData, ...prev];
      });
    }
  }, [publishFetcher.state, publishFetcher.data]);
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {/* 评论输入框 */}
      {/* 标题 + 发布按钮同行 */}
      <Grid container spacing={2} mb={2}>
        <Grid size={{ xs: 6, md: 8 }} >
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
        />
      </Box>

      <Divider />
      {/* 主题贴列表 */}
      <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {loadedThreads.map((thread) => (<>
          <ThreadItem key={thread.id} thread={thread} onClick={() => navigate(`/threads/${thread.id}`)} />
          <Divider variant="inset" component="li" />
        </>

        ))}
      </List>

      {/* 加载更多按钮 —— 仅在还有数据且未加载完时显示 */}
      {hasMore && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
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