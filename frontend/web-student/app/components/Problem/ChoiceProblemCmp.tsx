import React, { useState } from 'react';
import {
  Box,
  Typography,
  Radio,
  Checkbox,
  FormControlLabel,
  FormControl,
  Button,
  Paper,
  Alert,
  type SxProps,
  type Theme,
  Chip,
} from '@mui/material';
import type { ChoiceProblem } from '~/types/course';
import ProblemStatusChip from './ProblemStatusChip';
import { useFetcher } from 'react-router';

export default function ChoiceProblemCmp({
  problem,
  sx,
}: {
  problem: ChoiceProblem;
  sx?: SxProps<Theme>;
}) {
  const isMultiple = problem.is_multiple_choice;

  const [selection, setSelection] = useState<string | string[]>(
    isMultiple ? [] : ''
  );
  const [submitted, setSubmitted] = useState(false);
  const fetcher = useFetcher();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = event.target;

    if (isMultiple) {
      const current = selection as string[];
      if (checked) {
        setSelection([...current, value]);
      } else {
        setSelection(current.filter((v) => v !== value));
      }
    } else {
      setSelection(value);
    }
  };

  // 判断是否答对
  const isCorrect = () => {
    if (isMultiple) {
      const userAns = selection as string[];
      const correctAns = problem.correct_answer as string[];
      return (
        userAns.length === correctAns.length &&
        correctAns.every((ans) => userAns.includes(ans)) &&
        userAns.every((ans) => correctAns.includes(ans))
      );
    } else {
      return selection === problem.correct_answer;
    }
  };

  const handleSubmit = () => {
    const solved = isCorrect();

    // 使用 fetcher 提交结果
    fetcher.submit(
      { solved: String(solved) }, // 表单数据：solved="true" 或 "false"
      {
        method: 'post',
        action: `/problems/${problem.id}/mark_as_solved`,
        encType: 'application/x-www-form-urlencoded', // 默认，可省略
      }
    );

    setSubmitted(true);
  };

  const handleReset = () => {
    setSelection(isMultiple ? [] : '');
    setSubmitted(false);
  };

  // 防止重复提交（可选）
  const isSubmitting = fetcher.state === 'submitting';

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        width: '100%',
        ...sx,
      }}
    >
      <Typography variant="h5" gutterBottom>
        {problem.content}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <ProblemStatusChip status={problem.status} />
        <Chip
          label={problem.type.charAt(0).toUpperCase() + problem.type.slice(1)}
          color="primary"
          size="small"
        />
        <Chip
          label={`Difficulty: ${problem.difficulty}`}
          color="secondary"
          size="small"
        />
        {problem.chapter_title && (
          <Chip
            label={`Chapter: ${problem.chapter_title}`}
            variant="outlined"
            size="small"
          />
        )}
      </Box>

      <FormControl component="fieldset" sx={{ mt: 2 }}>
        {Object.entries(problem.options).map(([key, text]) => (
          <FormControlLabel
            key={key}
            control={
              isMultiple ? (
                <Checkbox
                  checked={(selection as string[]).includes(key)}
                  value={key}
                  onChange={handleChange}
                  disabled={submitted || isSubmitting}
                />
              ) : (
                <Radio
                  checked={selection === key}
                  value={key}
                  onChange={handleChange}
                  disabled={submitted || isSubmitting}
                />
              )
            }
            label={`${key}. ${text}`}
          />
        ))}
      </FormControl>

      {submitted && (
        <Box sx={{ mt: 2 }}>
          {isCorrect() ? (
            <Alert severity="success">回答正确！</Alert>
          ) : (
            <Alert severity="error">
              回答错误！
              {isMultiple
                ? `正确答案是：${(problem.correct_answer as string[]).join(', ')}`
                : `正确答案是：${problem.correct_answer}`}
            </Alert>
          )}
        </Box>
      )}

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        {!submitted ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={
              isSubmitting ||
              (isMultiple
                ? (selection as string[]).length === 0
                : !selection)
            }
          >
            {isSubmitting ? '提交中...' : '提交答案'}
          </Button>
        ) : (
          <Button variant="outlined" onClick={handleReset} disabled={isSubmitting}>
            重新答题
          </Button>
        )}
      </Box>
    </Paper>
  );
}