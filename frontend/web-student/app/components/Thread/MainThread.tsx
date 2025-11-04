import { Avatar, Box, Card, CardContent, CardHeader, Chip, Divider, Typography } from "@mui/material";
import { blue, grey } from "@mui/material/colors";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Thread } from "~/types/thread";
import { formatDateTime } from "~/utils/time";
import MarkdownRenderer from "../MarkdownRenderer";



export default function MainThread({thread}:{thread:Thread}){
    const {
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
            // src={author.avatar_url}
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
        <MarkdownRenderer markdownContent={content}/>
      </CardContent>

      <Divider />

      {/* 回复列表 */}
      <Box p={2}>
        <Typography variant="subtitle1" gutterBottom>
          回复 ({replies.length})
        </Typography>

        {replies.length === 0 ? (
          <Typography color="textSecondary">暂无回复</Typography>
        ) : (
          replies.map((reply) => (
            <Box key={reply.id} mb={3}>
              <Box display="flex" alignItems="center" mb={1}>
                <Avatar
                //   src={reply.author.avatar_url}
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
      </Box>
    </Card>
  );
}   