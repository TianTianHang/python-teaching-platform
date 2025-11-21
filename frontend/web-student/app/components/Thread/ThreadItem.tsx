import { ListItem, ListItemAvatar, Avatar, ListItemText, Box, Typography, Chip } from "@mui/material";
import { grey, blue } from "@mui/material/colors";
import type { Thread } from "~/types/thread";
import { truncateText } from "~/utils/text";
import { formatDateTime } from "~/utils/time";

interface ThreadItemProps {
  thread: Thread;
  onClick?: () => void;

}



export default function ThreadItem({ thread, onClick }: ThreadItemProps) {
  const {
    author,
    title,
    content, // ← 新增：使用 content 字段
    reply_count,
    is_pinned,
    is_resolved,
    is_archived,
    created_at,
    last_activity_at,
  } = thread;

  return (
    <ListItem
      onClick={onClick}
      alignItems="flex-start"
      sx={{
        py: 1,
        px: 2,
        minHeight: 0,
        opacity: is_archived ? 0.7 : 1,
        backgroundColor: is_archived ? grey[50] : 'inherit',
        '&:hover': {
          backgroundColor: 'action.hover',
        },
        cursor: onClick ? 'pointer' : 'default',
      }}
    >
      {/* 头像或置顶图标 */}
      <ListItemAvatar sx={{ mt: 0.5 }}>
        {is_pinned ? (
          <Avatar
            sx={{
              width: 28,
              height: 28,
              bgcolor: blue[500],
              fontSize: '0.75rem',
            }}
            src={thread.author.avatar || ""}
          >
            📌
          </Avatar>
        ) : (
          <Avatar
            alt={author.username}
            sx={{ width: 28, height: 28, bgcolor: blue[500], fontSize: '0.875rem' }}
          >
            {author.username.charAt(0).toUpperCase()}
          </Avatar>
        )}
      </ListItemAvatar>

      <ListItemText
        disableTypography
        primary={
          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
            <Typography
              variant="subtitle2"
              fontWeight={is_pinned ? 'bold' : 'medium'}
              sx={{ wordBreak: 'break-word', flex: 1, lineHeight: 1.3 }}
            >
              {title}
            </Typography>
            <Box display="flex" gap={0.5} flexShrink={0}>
              {is_resolved && (
                <Chip
                  label="已解决"
                  size="small"
                  color="success"
                  variant="outlined"
                  sx={{ height: 18, fontSize: '0.65rem', px: 0.5 }}
                />
              )}
              {is_archived && (
                <Chip
                  label="归档"
                  size="small"
                  color="default"
                  variant="outlined"
                  sx={{ height: 18, fontSize: '0.65rem', px: 0.5 }}
                />
              )}
            </Box>
          </Box>
        }
        secondary={
          <Box sx={{ mt: 0.5, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            {/* 内容预览 */}
            {content && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  wordBreak: 'break-word',
                  lineHeight: 1.4,
                  fontSize: '0.85rem',
                }}
              >
                {truncateText(content, 100)}
              </Typography>
            )}

            {/* 元信息：作者、时间、回复数等 */}
            <Typography
              variant="caption"
              color="textSecondary"
              sx={{ lineHeight: 1.4 }}
            >
              by {author.username} • {formatDateTime(created_at)} •{' '}
              {reply_count} 条回复 • 上次活动 {formatDateTime(last_activity_at)}
            </Typography>
          </Box>
        }
        sx={{ my: 0 }}
      />
    </ListItem>
  );
}