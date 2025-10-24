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
} from '@mui/material';
import type { ChoiceProblem } from '~/types/course';
export default function ChoiceProblemCmp({ problem }: { problem: ChoiceProblem,sx?: SxProps<Theme> }) {
  const isMultiple = problem.is_multiple_choice;

  // 状态：单选用 string，多选用 string[]
  const [selection, setSelection] = useState<string | string[]>(
    isMultiple ? [] : ''
  );
  const [submitted, setSubmitted] = useState(false);

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

  const handleSubmit = () => {
    setSubmitted(true);
  };

  const handleReset = () => {
    setSelection(isMultiple ? [] : '');
    setSubmitted(false);
  };

  // 判断是否答对（简单示例：假设 problem.answer 是正确选项 key 或 key 数组）
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
  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
      
        width: '100%',
      }}
    >
      <Typography variant="h5" gutterBottom>
        {problem.content}
      </Typography>

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
                  disabled={submitted}
                />
              ) : (
                <Radio
                  checked={selection === key}
                  value={key}
                  onChange={handleChange}
                  disabled={submitted}
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
              isMultiple
                ? (selection as string[]).length === 0
                : !selection
            }
          >
            提交答案
          </Button>
        ) : (
          <Button variant="outlined" onClick={handleReset}>
            重新答题
          </Button>
        )}
      </Box>
    </Paper>
  )
}