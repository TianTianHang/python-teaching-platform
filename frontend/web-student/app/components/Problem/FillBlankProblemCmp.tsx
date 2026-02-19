import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  Chip,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import type { FillBlankProblem, CheckFillBlankResponse, FillBlankResult } from '~/types/course';
import ProblemStatusChip from './ProblemStatusChip';
import { useFetcher } from 'react-router';
import { getDifficultyLabel } from '~/utils/chips';
import MarkdownRenderer from '../MarkdownRenderer';

export default function FillBlankProblemCmp({
  problem,
}: {
  problem: FillBlankProblem;
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [submitResults, setSubmitResults] = useState<CheckFillBlankResponse | null>(null);
  const fetcher = useFetcher<CheckFillBlankResponse>();

  // Parse content_with_blanks to extract blank markers
  const parseContentWithBlanks = () => {
    const textParts = problem.content_with_blanks.split(/(\[blank\d+\])/);
    const blanks: string[] = [];

    textParts.forEach(part => {
      const match = part.match(/^\[blank(\d+)]$/);
      if (match) {
        blanks.push(`blank${match[1]}`);
      }
    });

    // Initialize answer states for all blanks
    const initialState: Record<string, string> = {};
    blanks.forEach(blankId => {
      initialState[blankId] = answers[blankId] || '';
    });
    if (Object.keys(answers).length === 0) {
      setAnswers(initialState);
    }

    return { textParts, blanks };
  };

  const { textParts, blanks } = parseContentWithBlanks();

  const handleAnswerChange = (blankId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [blankId]: value,
    }));
  };

  const handleSubmit = async () => {
    const answerData: Record<string, string> = {};
    blanks.forEach(blankId => {
      answerData[blankId] = answers[blankId] || '';
    });
   
    fetcher.submit(
      { answers: JSON.stringify(answerData) },
      {
        method: 'post',
        action: `/problems/${problem.id}/check/?type=fill_blank`,
        encType: 'application/x-www-form-urlencoded',
      }
    );

    // Note: We'll handle the response in useEffect when fetcher.data is updated
  };

  const handleReset = () => {
    const newAnswers: Record<string, string> = {};
    blanks.forEach(blankId => {
      newAnswers[blankId] = '';
    });
    setAnswers(newAnswers);
    setSubmitted(false);
    setSubmitResults(null);
  };

  // Handle fetcher response
  React.useEffect(() => {
    if (fetcher.data) {
      setSubmitResults(fetcher.data);
      setSubmitted(true);
    }
  }, [fetcher.data]);

  // Check if all blanks are answered
  const allAnswered = blanks.length > 0 && blanks.every(blankId => answers[blankId]?.trim().length > 0);
  const isSubmitting = fetcher.state === 'submitting';

  // Check if all answers are correct from results
  const allCorrect = submitResults?.all_correct;

  const renderContent = () => {
    return (
      <div>
        {textParts.map((part, index) => {
          const blankMatch = part.match(/^\[blank(\d+)]$/);
          if (blankMatch) {
            const blankId = `blank${blankMatch[1]}`;
            return (
              <TextField
                key={index}
                value={answers[blankId] || ''}
                onChange={(e) => handleAnswerChange(blankId, e.target.value)}
                variant="outlined"
                size="small"
                placeholder={`空白 ${blankMatch[1]}`}
                disabled={submitted || isSubmitting}
                sx={{
                  mx: 0.5,
                    maxWidth: 200,
                    '& .MuiOutlinedInput-input': {
                      textAlign: 'center',
                    },
                  }}
              />
            );
          }
          return part;
        })}
      </div>
    );
  };

  return (
    <Card>
      <CardContent>
        <MarkdownRenderer markdownContent={problem.content} />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <ProblemStatusChip status={problem.status} />
          <Chip
            label={problem.type.charAt(0).toUpperCase() + problem.type.slice(1)}
            color="primary"
            size="small"
          />
          {getDifficultyLabel(problem.difficulty)}
          {problem.chapter_title && (
            <Chip
              label={`Chapter: ${problem.chapter_title}`}
              variant="outlined"
              size="small"
            />
          )}
        </Box>

        <Paper sx={{ p: 3, mt: 2, bgcolor: 'background.paper' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            请填写下面的空白：
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
            {renderContent()}
          </Box>
        </Paper>

        {submitResults && (
          <Box sx={{ mt: 2 }}>
            {allCorrect ? (
              <Alert severity="success">
                回答全部正确！恭喜你完成了这道题！
              </Alert>
            ) : (
              <Alert severity="error">
                回答有误，请检查并重新填写。
                {submitResults.results && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" component="div">
                      详细结果：
                    </Typography>
                    {Object.entries(submitResults.results).map(([blankId, result]: [string, FillBlankResult]) => (
                      <Box key={blankId} sx={{ mt: 0.5, fontSize: '0.875rem' }}>
                        <Typography variant="body2" component="span">
                          {blankId}: 你的答案 &quot;{result.user_answer}&quot;{' '}
                          {result.is_correct ? (
                            <Typography color="success">✓ 正确</Typography>
                          ) : (
                            <Typography color="error">
                              ✗ 正确答案: {result.correct_answers.join(', ')}
                            </Typography>
                          )}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </Alert>
            )}
          </Box>
        )}
      </CardContent>
      <CardActions>
        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          {!submitted ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={!allAnswered || isSubmitting}
            >
              {isSubmitting ? '提交中...' : '提交答案'}
            </Button>
          ) : (
            <Button variant="outlined" onClick={handleReset} disabled={isSubmitting}>
              重新答题
            </Button>
          )}
        </Box>
      </CardActions>
    </Card>
  );
}