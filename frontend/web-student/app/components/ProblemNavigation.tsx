import React, { useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Stack,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import ViewListIcon from '@mui/icons-material/ViewList';
import { spacing, transitions } from '~/design-system/tokens';

interface ProblemNavigationProps {
  problemTitle?: string;
  hasNext: boolean;
  hasPrevious: boolean;
  onPrevious?: () => void;
  onNext?: () => void;
  onBackToList?: () => void;
  loading?: boolean;
  isFirstProblem?: boolean;
  isLastProblem?: boolean;
}

/**
 * 题目详情页面的底部导航栏组件
 *
 * 提供统一的题目导航体验，包括：
 * - 返回题目列表
 * - 上一题（如果存在）
 * - 下一题（如果存在）
 * - 边界情况处理（第一题/最后一题的特殊显示）
 */
export default function ProblemNavigation({
  problemTitle,
  hasNext,
  hasPrevious,
  onPrevious,
  onNext,
  onBackToList,
  loading = false,
  isFirstProblem = false,
  isLastProblem = false,
}: ProblemNavigationProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // 截断题目标题以显示在导航栏中
  const displayTitle = problemTitle
    ? problemTitle.length > 30
      ? `${problemTitle.substring(0, 30)}...`
      : problemTitle
    : '';

  // 计算当前显示的按钮状态
  const showPreviousButton = hasPrevious && onPrevious;
  const showNextButton = hasNext && onNext;
  const showBackToListButton = onBackToList;

  // 如果没有任何导航按钮可用，不显示导航栏
  if (!showPreviousButton && !showNextButton && !showBackToListButton) {
    return null;
  }

  // 添加键盘导航支持
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 防止在输入框中触发
      if ((event.target as HTMLElement).tagName === 'INPUT' ||
          (event.target as HTMLElement).tagName === 'TEXTAREA' ||
          (event.target as HTMLElement).isContentEditable) {
        return;
      }

      switch (event.key) {
        case 'ArrowLeft':
          if (hasPrevious && !loading) {
            event.preventDefault();
            onPrevious?.();
          }
          break;
        case 'ArrowRight':
          if (hasNext && !loading) {
            event.preventDefault();
            onNext?.();
          }
          break;
        case 'Escape':
          event.preventDefault();
          onBackToList?.();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [hasPrevious, hasNext, onPrevious, onNext, onBackToList, loading]);

  return (
    <Container maxWidth="md" sx={{ py: spacing.md }}>
      <Box
        sx={{
          position: 'sticky',
          bottom: 0,
          backgroundColor: 'background.paper',
          borderTop: '1px solid',
          borderColor: 'divider',
          boxShadow: '0 -2px 4px rgba(0, 0, 0, 0.1)',
          zIndex: 100,
          transition: transitions.themeSwitch,
        }}
      >
        <Stack
          direction={isMobile ? 'column' : 'row'}
          alignItems="center"
          justifyContent="space-between"
          spacing={2}
          sx={{ p: spacing.md }}
        >
          {/* 左侧：题目标题和边界提示 */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            {problemTitle && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  fontSize: isMobile ? '0.875rem' : '0.875rem',
                  maxWidth: isMobile ? '100%' : '300px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {displayTitle}
              </Typography>
            )}

            {/* 边界状态提示 */}
            {(isFirstProblem || isLastProblem) && (
              <Typography
                variant="caption"
                color={isFirstProblem ? 'warning.main' : 'info.main'}
                sx={{
                  fontSize: '0.75rem',
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  backgroundColor: isFirstProblem
                    ? 'warning.light'
                    : 'info.light',
                  display: 'inline-block',
                }}
              >
                {isFirstProblem ? '这是第一题' : '这是最后一题'}
              </Typography>
            )}
          </Box>

          {/* 右侧：导航按钮组 */}
          <Stack
            direction={isMobile ? 'column' : 'row'}
            alignItems="center"
            spacing={1}
            sx={{
              width: isMobile ? '100%' : 'auto',
              flexShrink: 0,
            }}
          >
            {/* 返回列表按钮 */}
            {showBackToListButton && (
              <Button
                variant="outlined"
                onClick={onBackToList}
                startIcon={<ViewListIcon />}
                size="small"
                aria-label="返回题目列表"
                title="返回题目列表 (Esc)"
                sx={{
                  minWidth: isMobile ? '100%' : 120,
                  fontSize: '0.875rem',
                  order: isMobile ? 1 : -1,
                }}
              >
                返回列表
              </Button>
            )}

            {/* 上一题按钮 */}
            {showPreviousButton && (
              <Button
                variant="outlined"
                onClick={onPrevious}
                startIcon={<ArrowBackIosIcon />}
                disabled={loading}
                size="small"
                aria-label="上一题"
                aria-disabled={loading}
                title="上一题 (←)"
                sx={{
                  minWidth: isMobile ? '100%' : 120,
                  fontSize: '0.875rem',
                  order: isMobile ? 0 : 0,
                }}
              >
                上一题
              </Button>
            )}

            {/* 下一题按钮 */}
            {showNextButton && (
              <Button
                variant="contained"
                onClick={onNext}
                endIcon={<ArrowForwardIosIcon />}
                disabled={loading}
                size="small"
                aria-label="下一题"
                aria-disabled={loading}
                title="下一题 (→)"
                sx={{
                  minWidth: isMobile ? '100%' : 120,
                  fontSize: '0.875rem',
                  order: isMobile ? 2 : 1,
                }}
              >
                下一题
              </Button>
            )}

            {/* 边界情况下的提示文本 */}
            {!showPreviousButton && (
              <Typography
                variant="caption"
                color="text.disabled"
                sx={{
                  fontSize: '0.75rem',
                  order: isMobile ? (showNextButton ? 3 : -1) : (showBackToListButton ? 0 : -1),
                  minWidth: isMobile ? '100%' : 120,
                  textAlign: 'center',
                  px: 1,
                }}
              >
                没有上一题
              </Typography>
            )}

            {!showNextButton && (
              <Typography
                variant="caption"
                color="text.disabled"
                sx={{
                  fontSize: '0.75rem',
                  order: isMobile ? (showNextButton ? 3 : -1) : (showBackToListButton ? 0 : -1),
                  minWidth: isMobile ? '100%' : 120,
                  textAlign: 'center',
                  px: 1,
                }}
              >
                没有下一题
              </Typography>
            )}
          </Stack>
        </Stack>
      </Box>
    </Container>
  );
}