import { Cancel, CheckCircle } from '@mui/icons-material';
import {
  Box,
  Typography,
  useTheme,
  Chip,

} from '@mui/material';
import type { ExamAnswerCorrect } from '~/types/course';

interface AnswerReviewCardProps {
  problemType: 'choice' | 'fillblank';
  userAnswer: any;
  correctAnswer: ExamAnswerCorrect;
  score?: string | number;
  correctPercentage?: number;
  maxScore?: number;
}

/**
 * AnswerReviewCard - Elegant answer review component
 * Displays user's answer vs correct answer with visual feedback
 */
export default function AnswerReviewCard({
  problemType,
  userAnswer,
  correctAnswer,
  score,
  correctPercentage,
  maxScore,
}: AnswerReviewCardProps) {
 
  const theme = useTheme();

  const numericScore = typeof score === 'string' ? parseFloat(score) : score;

  const getScoreColor = () => {
    if (score === undefined || score === null) return 'neutral';
    if (maxScore && numericScore! >= maxScore) return 'success';
    if (maxScore && numericScore! >= maxScore * 0.6) return 'warning';
    return 'error';
  };

  const scoreColor = getScoreColor();
  // console.log(maxScore)
  const colorMap = {
    success: theme.palette.success.main,
    warning: theme.palette.warning?.main,
    error: theme.palette.error.main,
    neutral: theme.palette.text.secondary,
  };

  const bgColorMap = {
    success: 'success.08',
    warning: 'warning.08',
    error: 'error.08',
    neutral: 'action.hover',
  };

  // Choice Answer Display
  if (problemType === 'choice') {
    const userAnswers = Array.isArray(userAnswer) ? userAnswer : [userAnswer];
    const correctAnswers = correctAnswer.correct_answer || [];
    const allOptions = correctAnswer.all_options || {};

    return (
      <Box
        sx={{
          p: 2.5,
          borderRadius: 2,
          border: `1px solid ${theme.palette.divider}`,
          bgcolor: bgColorMap[scoreColor],
          borderLeft: `4px solid ${colorMap[scoreColor]}`,
        }}
      >
        {/* Score Header */}
        {score !== undefined && score !== null && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            {scoreColor === 'success' ? (
              <CheckCircle sx={{ color: colorMap.success, fontSize: 20 }} />
            ) : (
              <Cancel sx={{ color: colorMap.error, fontSize: 20 }} />
            )}
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              得分: {score} {maxScore && `/ ${maxScore}`}
            </Typography>
            {problemType!='choice' && correctPercentage !== undefined && (
              <Chip
                label={`${correctPercentage.toFixed(0)}%`}
                size="small"
                sx={{
                  bgcolor: colorMap[scoreColor],
                  color: 'white',
                  fontWeight: 600,
                  height: 20,
                }}
              />
            )}
          </Box>
        )}

        {/* Options */}
        <Box>
          {Object.entries(allOptions).map(([key, value]) => {
            const isSelected = userAnswers.includes(key);
            const isCorrect = correctAnswers.includes(key);
            const isUserWrong = isSelected && !isCorrect;
            const isMissedCorrect = !isSelected && isCorrect;

            const getOptionStyle = () => {
              if (isUserWrong) {
                return {
                  borderColor: colorMap.error,
                  bgcolor: 'error.08',
                  icon: <Cancel sx={{ color: colorMap.error, fontSize: 16 }} />,
                };
              }
              if (isSelected && isCorrect) {
                return {
                  borderColor: colorMap.success,
                  bgcolor: 'success.08',
                  icon: <CheckCircle sx={{ color: colorMap.success, fontSize: 16 }} />,
                };
              }
              if (isMissedCorrect) {
                return {
                  borderColor: colorMap.warning,
                  bgcolor: 'warning.08',
                  icon: (
                    <Typography variant="caption" sx={{ color: colorMap.warning }}>
                      正确答案
                    </Typography>
                  ),
                };
              }
              return {
                borderColor: 'divider',
                bgcolor: 'transparent',
                icon: null,
              };
            };

            const style = getOptionStyle();

            return (
              <Box
                key={key}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1,
                  px: 1.5,
                  mb: 1,
                  border: `1px solid ${style.borderColor}`,
                  borderRadius: 1.5,
                  bgcolor: style.bgcolor,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                    minWidth: 28,
                  }}
                >
                  {key}.
                </Typography>
                <Typography variant="body2" sx={{ flex: 1 }}>
                  {value}
                </Typography>
                {style.icon}
              </Box>
            );
          })}
        </Box>
      </Box>
    );
  }

  // Fill-in-blank Answer Display
  if (problemType === 'fillblank') {
    const blankKeys = Object.keys(userAnswer || {}).sort();
    const blanksList = correctAnswer.blanks_list || [];

    return (
      <Box
        sx={{
          p: 2.5,
          borderRadius: 2,
          border: `1px solid ${theme.palette.divider}`,
          bgcolor: bgColorMap[scoreColor],
          borderLeft: `4px solid ${colorMap[scoreColor]}`,
        }}
      >
        {/* Score Header */}
        {score !== undefined && score !== null && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            {scoreColor === 'success' ? (
              <CheckCircle sx={{ color: colorMap.success, fontSize: 20 }} />
            ) : scoreColor === 'warning' ? (
              <Chip label="部分正确" size="small" color="warning" />
            ) : (
              <Cancel sx={{ color: colorMap.error, fontSize: 20 }} />
            )}
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              得分: {score} {maxScore && `/ ${maxScore}`}
            </Typography>
            {correctPercentage !== undefined && (
              <Chip
                label={`${correctPercentage.toFixed(0)}%`}
                size="small"
                sx={{
                  bgcolor: colorMap[scoreColor],
                  color: 'white',
                  fontWeight: 600,
                  height: 20,
                }}
              />
            )}
          </Box>
        )}

        {/* Blanks */}
        <Box>
          {blankKeys.map((key, index) => {
            const userVal = userAnswer?.[key] || '';
            const blankInfo = blanksList[index];
            const correctVals = blankInfo?.answers || [];
            const caseSensitive = blankInfo?.case_sensitive || false;

            const isCorrect = caseSensitive
              ? correctVals.includes(userVal)
              : correctVals.some((v) => v.toLowerCase() === userVal.toLowerCase());

            return (
              <Box
                key={key}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1,
                  px: 1.5,
                  mb: 1,
                  border: `1px solid ${isCorrect ? colorMap.success : colorMap.error}`,
                  borderRadius: 1.5,
                  bgcolor: isCorrect ? 'success.08' : 'error.08',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                    minWidth: 80,
                  }}
                >
                  {key}:
                </Typography>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" sx={{ display: 'inline', mr: 1 }}>
                    <Typography component="span" sx={{ color: theme.palette.text.secondary }}>
                      你的答案:
                    </Typography>{' '}
                    <Typography
                      component="span"
                      sx={{
                        fontWeight: 500,
                        color: isCorrect ? colorMap.success : colorMap.error,
                        textDecoration: !isCorrect && userVal ? 'line-through' : 'none',
                      }}
                    >
                      {userVal || '(未填)'}
                    </Typography>
                  </Typography>
                  {!isCorrect && (
                    <>
                      <Typography variant="body2" sx={{ color: theme.palette.text.secondary, ml: 2, display: 'inline' }}>
                        正确答案:{' '}
                        <Typography
                          component="span"
                          sx={{ color: colorMap.success, fontWeight: 500 }}
                        >
                          {correctVals.join(' 或 ')}
                        </Typography>
                      </Typography>
                    </>
                  )}
                </Box>
                {isCorrect ? (
                  <CheckCircle sx={{ color: colorMap.success, fontSize: 18, ml: 1 }} />
                ) : (
                  <Cancel sx={{ color: colorMap.error, fontSize: 18, ml: 1 }} />
                )}
              </Box>
            );
          })}
        </Box>
      </Box>
    );
  }

  return null;
}
