import { Chip } from '@mui/material';

export const getDifficultyLabel = (level: number) => {
  const labels = ['简单', '中等', '困难'] as const;
  const colors = ['success', 'warning', 'error'] as const;

  // 确保 level 在有效范围内（1, 2, 3）
  if (level < 1 || level > labels.length) {
    return <Chip label="未知" size="small" color="default" />;
  }

  return (
    <Chip
      label={labels[level - 1]}
      size="small"
      color={colors[level - 1]} // ✅ 现在 TS 知道这是 'success' | 'warning' | 'error'
    />
  );
};