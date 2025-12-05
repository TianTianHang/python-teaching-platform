import { Avatar, Box, Button, Card, CardContent, CardHeader, Chip, CircularProgress, Divider, Grid, TextField, Typography } from "@mui/material";
import { blue, grey } from "@mui/material/colors";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Reply, Thread } from "~/types/thread";
import { formatDateTime } from "~/utils/time";
import MarkdownRenderer from "../MarkdownRenderer";
import { useEffect, useState } from "react";
import { MdEditor } from "md-editor-rt";
import { useFetcher } from "react-router";
import { handleUpload } from "~/utils/image";
import 'md-editor-rt/lib/style.css';
import { showNotification } from "../Notification";


export default function MainThread({ thread }: { thread: Thread }) {
  const {
    id,
    author,
    title,
    content,
    replies,
    is_pinned,
    is_resolved,
    is_archived,
    created_at,
    updated_at,
  } = thread;
  const [loadedReplies, setLoadedReplies] = useState<Reply[]>(replies);
  const [replyTitle, setReplyTitle] = useState("");
  const [replyContent, setReplyContent] = useState("");
  const [currentPage, setCurrentPage] = useState<number>(0);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [totalItems, setTotalItems] = useState<number>(replies.length);
  const [hasMore, setHasMore] = useState<boolean>(true); // 是否还有更多数据

  const replyFetcher = useFetcher<{
    data: Reply[];
    currentPage: number;
    totalItems: number;
    actualPageSize: number;
  }>();
  const isLoading = replyFetcher.state !== "idle";
  // 首次加载后更新 totalItems 和 hasMore
  useEffect(() => {
    if (replyFetcher.state === "idle" && replyFetcher.data) {
      const { data, currentPage: fetchedPage, totalItems: fetchedTotal } = replyFetcher.data;
      // TODO 加载合并
      setLoadedReplies((prev) => [...prev, ...data]);
      setCurrentPage(fetchedPage);
      setTotalItems(fetchedTotal);

      // 判断是否还有更多数据
      const loadedCount = loadedReplies.length + data.length;
      setHasMore(loadedCount < fetchedTotal);
    }
  }, [replyFetcher.state, replyFetcher.data]);

 

  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    const queryParams = new URLSearchParams();
    queryParams.set("page", nextPage.toString());
    queryParams.set("page_size", "10"); // 固定或可配置
    replyFetcher.load(`/threads/${id}/replies/?${queryParams.toString()}`);
  };

  const publishFetcher = useFetcher<Reply>();
  function handlePublish(): void {
    publishFetcher.submit({
      title: replyTitle, content: replyContent,
    },
      { method: "POST", action: `/threads/${id}/replies` })
    showNotification("success", "发布成功", "评论发布成功")
  }
  useEffect(() => {
    if (publishFetcher.state === "idle" && publishFetcher.data) {
      setLoadedReplies(prev => {
        const newData = publishFetcher.data;
        if (!newData) return prev; // 防御性编程
        return [newData, ...prev];
      });

    }
  }, [publishFetcher.state, publishFetcher.data]);
  return (
    <Card
      sx={{
        maxWidth: 800,
        mx: 'auto',
        my: 2,
        borderLeft: is_pinned ? `4px solid ${blue[500]}` : 'none',
        opacity: is_archived ? 0.7 : 1,
        backgroundColor: is_archived ? grey[50] : 'background.paper',
      }}
    >
      {/* 头部：作者 + 标题 + 状态标签 */}
      <CardHeader
        avatar={
          <Avatar
            src={thread.author.avatar || ""}
            alt={author.username}
            sx={{ bgcolor: blue[500] }}
          >
            {author.username.charAt(0).toUpperCase()}
          </Avatar>
        }
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h6">{title}</Typography>
            {is_pinned && (
              <Chip label="置顶" size="small" color="primary" variant="outlined" />
            )}
            {is_resolved && (
              <Chip label="已解决" size="small" color="success" variant="outlined" />
            )}
            {is_archived && (
              <Chip label="已归档" size="small" color="default" variant="outlined" />
            )}
          </Box>
        }
        subheader={
          <Typography variant="body2" color="textSecondary">
            由 {author.username} 发布于 {formatDateTime(created_at)}
            {updated_at !== created_at && ` • 更新于 ${formatDateTime(updated_at)}`}
          </Typography>
        }
      />

      <CardContent>
        {/* 主内容（Markdown） */}
        <MarkdownRenderer markdownContent={content} />
      </CardContent>

      <Divider />

      {/* 回复列表 */}
      <Box p={2}>
        <Typography variant="subtitle1" gutterBottom>
          回复 ({loadedReplies.length})
        </Typography>

        {loadedReplies.length === 0 ? (
          <Typography color="textSecondary">暂无回复</Typography>
        ) : (
          loadedReplies.map((reply) => (
            <Box key={reply.id} mb={3}>
              <Box display="flex" alignItems="center" mb={1}>
                <Avatar
                  src={reply.author.avatar || ""}
                  alt={reply.author.username}
                  sx={{ width: 24, height: 24, mr: 1 }}
                >
                  {reply.author.username.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="body2" fontWeight="bold">
                  {reply.author.username}
                </Typography>
                <Typography variant="caption" color="textSecondary" ml={1}>
                  {formatDateTime(reply.created_at)}
                </Typography>
              </Box>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {reply.content}
              </ReactMarkdown>
              {reply.mentioned_users.length > 0 && (
                <Box mt={0.5}>
                  {reply.mentioned_users.map((user) => (
                    <Chip
                      key={user.id}
                      label={`@${user.username}`}
                      size="small"
                      sx={{ mr: 0.5, fontSize: '0.75rem' }}
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
              <Divider sx={{ mt: 2 }} />
            </Box>
          ))
        )}
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
      <Divider />
      <Box sx={{ m: 4 }}>
        <Grid container spacing={2} mb={2}>
          <Grid size={{ xs: 6, md: 8 }} >
            <TextField
              fullWidth
              label="标题"
              variant="standard"
              value={replyTitle}
              onChange={(e) => setReplyTitle(e.target.value)}
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
            value={replyContent}
            onChange={(value) => setReplyContent(value)}
            toolbars={['italic', 'underline', 'bold', "code", "image", "=", "preview"]}
            preview={false}
            onUploadImg={handleUpload}
            previewTheme={'github'}
          />
        </Box>
      </Box>

    </Card>
  );
}   