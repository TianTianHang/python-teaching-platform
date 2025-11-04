import { ListItem, ListItemAvatar, Avatar, ListItemText, Box, Typography, Chip, Divider } from "@mui/material";
import { grey, blue } from "@mui/material/colors";
import type { Thread } from "~/types/thread";
import { formatDateTime } from "~/utils/time";

interface ThreadItemProps {
    thread: Thread;
    onClick?: () => void; // 可选点击事件（用于跳转详情）
}
export default function ThreadItem({ thread, onClick }: ThreadItemProps) {
    const { author, title, reply_count, is_pinned, is_resolved, is_archived, created_at, last_activity_at } = thread;

    return (
        <ListItem
            onClick={onClick}
            alignItems="flex-start"
            sx={{
                py: 1.5,
                px: 2,
                opacity: is_archived ? 0.7 : 1,
                backgroundColor: is_archived ? grey[50] : 'inherit',
                '&:hover': {
                    backgroundColor: 'action.hover',
                },
            }}
        >
            {/* 置顶标识或头像 */}
            <ListItemAvatar>
                {is_pinned ? (
                    <Avatar
                        sx={{
                            width: 32,
                            height: 32,
                            bgcolor: blue[500],
                            fontSize: '0.9rem',
                        }}
                    >
                        📌
                    </Avatar>
                ) : (
                    <Avatar
                        // src={author.avatar_url}
                        alt={author.username}
                        sx={{ width: 32, height: 32, bgcolor: blue[500] }}
                    >
                        {author.username.charAt(0).toUpperCase()}
                    </Avatar>
                )}
            </ListItemAvatar>

            <ListItemText
                primary={
                    <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
                        <Typography
                            variant="subtitle1"
                            fontWeight={is_pinned ? 'bold' : 'medium'}
                            sx={{ wordBreak: 'break-word', flex: 1 }}
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
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                            {is_archived && (
                                <Chip
                                    label="归档"
                                    size="small"
                                    color="default"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                            )}
                        </Box>
                    </Box>
                }
                secondary={
                    <Box display="flex" alignItems="center" gap={1.5} mt={0.5}>
                        <Typography variant="body2" color="textSecondary">
                            by {author.username}
                        </Typography>
                        <Divider orientation="vertical" flexItem />
                        <Typography variant="body2" color="textSecondary">
                            {formatDateTime(created_at)}
                        </Typography>
                        <Divider orientation="vertical" flexItem />
                        <Typography variant="body2" color="textSecondary">
                            {reply_count} 条回复
                        </Typography>
                        <Divider orientation="vertical" flexItem />
                        <Typography variant="body2" color="textSecondary">
                            上次回复 {formatDateTime(last_activity_at)}
                        </Typography>
                    </Box>
                }
            />
        </ListItem>
    );
}