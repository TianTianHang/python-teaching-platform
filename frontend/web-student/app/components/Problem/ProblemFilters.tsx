import React from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';
import { spacing } from '~/design-system/tokens';

export interface FilterState {
  type: string | null;
  difficulty: string | null;
  ordering: string;
}

interface ProblemFiltersProps {
  currentType: string | null;
  currentDifficulty: string | null;
  currentOrdering: string | null;
  onFilterChange: (filters: FilterState) => void;
}

const ProblemFilters: React.FC<ProblemFiltersProps> = ({
  currentType,
  currentDifficulty,
  currentOrdering,
  onFilterChange,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleTypeChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value === 'all' ? null : event.target.value;
    onFilterChange({
      type: value,
      difficulty: currentDifficulty,
      ordering: currentOrdering || '',
    });
  };

  const handleDifficultyChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value === 'all' ? null : event.target.value;
    onFilterChange({
      type: currentType,
      difficulty: value,
      ordering: currentOrdering || '',
    });
  };

  const handleOrderingChange = (event: SelectChangeEvent<string>) => {
    onFilterChange({
      type: currentType,
      difficulty: currentDifficulty,
      ordering: event.target.value,
    });
  };

  const handleClearFilters = () => {
    onFilterChange({
      type: null,
      difficulty: null,
      ordering: '',
    });
  };

  const hasActiveFilters = currentType || currentDifficulty || currentOrdering;

  return (
    <Box>
      <Stack
        direction={isMobile ? 'column' : 'row'}
        spacing={spacing.md}
        useFlexGap
        sx={{
          flexWrap: 'wrap',
          alignItems: isMobile ? 'stretch' : 'center',
        }}
      >
        {/* Type Filter */}
        <FormControl sx={{ minWidth: isMobile ? '100%' : 180 }} size="small">
          <InputLabel id="type-filter-label">题目类型</InputLabel>
          <Select
            labelId="type-filter-label"
            value={currentType || 'all'}
            label="题目类型"
            onChange={handleTypeChange}
          >
            <MenuItem value="all">全部</MenuItem>
            <MenuItem value="algorithm">编程题</MenuItem>
            <MenuItem value="choice">选择题</MenuItem>
            <MenuItem value="fillblank">填空题</MenuItem>
          </Select>
        </FormControl>

        {/* Difficulty Filter */}
        <FormControl sx={{ minWidth: isMobile ? '100%' : 180 }} size="small">
          <InputLabel id="difficulty-filter-label">难度</InputLabel>
          <Select
            labelId="difficulty-filter-label"
            value={currentDifficulty || 'all'}
            label="难度"
            onChange={handleDifficultyChange}
          >
            <MenuItem value="all">全部</MenuItem>
            <MenuItem value="1">简单</MenuItem>
            <MenuItem value="2">中等</MenuItem>
            <MenuItem value="3">困难</MenuItem>
          </Select>
        </FormControl>

        {/* Sort Options */}
        <FormControl sx={{ minWidth: isMobile ? '100%' : 200 }} size="small">
          <InputLabel id="ordering-filter-label">排序</InputLabel>
          <Select
            labelId="ordering-filter-label"
            value={currentOrdering || ''}
            label="排序"
            onChange={handleOrderingChange}
          >
            <MenuItem value="">默认</MenuItem>
            <MenuItem value="difficulty">难度 (低到高)</MenuItem>
            <MenuItem value="-difficulty">难度 (高到低)</MenuItem>
            <MenuItem value="-created_at">最新创建</MenuItem>
            <MenuItem value="created_at">最早创建</MenuItem>
            <MenuItem value="title">标题 (A-Z)</MenuItem>
            <MenuItem value="-title">标题 (Z-A)</MenuItem>
          </Select>
        </FormControl>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            variant="outlined"
            size="small"
            onClick={handleClearFilters}
            sx={{
              height: isMobile ? 'auto' : 40,
              alignSelf: isMobile ? 'stretch' : 'auto',
            }}
          >
            清除筛选
          </Button>
        )}
      </Stack>
    </Box>
  );
};

export default ProblemFilters;
