import { Box, useTheme } from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import JupyterLiteCodeBlock from "./JupyterLiteCodeBlock";
export default function MarkdownRenderer({ markdownContent }:{markdownContent:string}) {
    const theme = useTheme();
    const markdownSx = {
        // 容器样式（可选，例如设置最大宽度和内边距）
        p: 2, // padding: theme.spacing(2)
        maxWidth: 'lg',
        mx: 'auto', // margin-left & margin-right: auto (居中)
        mt:0,
        // --- 标题样式 ---
        '& h1': {
            ...theme.typography.h3, // 使用 MUI 的 h3 变体样式
            mt: 4, // margin-top: theme.spacing(4)
            mb: 2, // margin-bottom: theme.spacing(2)
            borderBottom: `1px solid ${theme.palette.divider}`,
            pb: 1, // padding-bottom: theme.spacing(1)
        },
        '& h2': {
            ...theme.typography.h4, // 使用 MUI 的 h4 变体样式
            mt: 3,
            mb: 2,
            borderBottom: `1px dashed ${theme.palette.divider}`,
            pb: 0.5,
        },
        '& h3': {
            ...theme.typography.h5,
            mt: 3,
            mb: 1.5,
        },
        '& h4': {
            ...theme.typography.h6,
            mt: 2,
            mb: 1,
        },
        '& h5': {
            ...theme.typography.subtitle1,
            mt: 1.5,
            mb: 1,
        },
        '& h6': {
            ...theme.typography.subtitle2,
            mt: 1,
            mb: 0.5,
        },

        // --- 段落和文本样式 ---
        '& p': {
            ...theme.typography.body1, // 使用 MUI 的 body1 变体样式
            mb: 2,
            lineHeight: 1.7,
        },
        '& strong, & b': {
            fontWeight: theme.typography.fontWeightBold,
        },
        '& em, & i': {
            fontStyle: 'italic',
        },

        // --- 链接样式 ---
        '& a': {
            color: theme.palette.primary.main,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        },

        // --- 列表样式 ---
        '& ul, & ol': {
            mb: 2,
            pl: 4, // padding-left
        },
        '& ul': {
            listStyleType: 'disc',
        },
        '& ol': {
            listStyleType: 'decimal',
        },
        '& li': {
            mb: 0.5,
            '& p': { // 列表项中的段落
                mb: 0.5,
                display: 'inline', // 避免列表项中的段落导致额外的换行
            }
        },

        // --- 引用块样式 (Blockquote) ---
        '& blockquote': {
            mx: 0, // margin-left & margin-right: 0
            my: 3, // margin-top & margin-bottom
            pl: 2, // padding-left
            borderLeft: `4px solid ${theme.palette.grey[400]}`,
            color: theme.palette.text.secondary,
            '& p': {
                ...theme.typography.body2,
                fontStyle: 'italic',
                mb: 1,
            }
        },

        // --- 代码块样式 (Code Block) ---
        '& pre': {
            backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[900] : theme.palette.grey[100],
            p: 2,
            my: 3,
            borderRadius: theme.shape.borderRadius,
            overflowX: 'auto', // 确保代码块能横向滚动
            '& code': {
                ...theme.typography.body2,
                fontFamily: 'monospace',
                // 如果使用 Prism 或其他高亮库，可能还需要进一步调整
            },
        },

        // --- 行内代码样式 (Inline Code) ---
        '& code': {
            backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[700] : theme.palette.grey[200],
            p: '2px 4px', // padding
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '0.9em',
            color: theme.palette.text.primary,
        },

        // --- 分割线样式 ---
        '& hr': {
            border: 'none',
            borderBottom: `1px dashed ${theme.palette.divider}`,
            my: 4, // margin-top & margin-bottom
        },

        // --- 表格样式 ---
        '& table': {
            width: '100%',
            my: 3,
            borderCollapse: 'collapse',
            // 基础表格边框，通常建议使用 MUI 的 Table 组件来替代原生 table 标签
            border: `1px solid ${theme.palette.divider}`,
            '& th': {
                ...theme.typography.subtitle2,
                backgroundColor: theme.palette.action.hover,
                border: `1px solid ${theme.palette.divider}`,
                p: 1.5,
                textAlign: 'left',
            },
            '& td': {
                ...theme.typography.body2,
                border: `1px solid ${theme.palette.divider}`,
                p: 1.5,
            },
        },
    };

    return (
        <Box sx={markdownSx}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    code(props) {
                        const { children, className } = props;
                        const match = /language-([\w-]+)/.exec(className || '');
                        const language = match ? match[1] : '';

                        // 检测是否为 python-exec 标记
                        if (language === 'python-exec') {
                            return (
                                <Box
                                    sx={{
                                        my: 3,  // 与普通代码块保持一致的垂直间距
                                    }}
                                >
                                    <JupyterLiteCodeBlock
                                        code={String(children).replace(/\n$/, '')}
                                        height={200}
                                    />
                                </Box>
                            );
                        }

                        // 默认代码块渲染
                        return (
                            <code className={className} {...props}>
                                {children}
                            </code>
                        );
                    },
                }}
            >
                {markdownContent}
            </ReactMarkdown>
        </Box>
    );
}