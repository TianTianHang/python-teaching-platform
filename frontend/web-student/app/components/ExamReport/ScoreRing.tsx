import { Box, Typography, useTheme } from '@mui/material';
import React, { useMemo } from 'react';

interface ScoreRingProps {
  score: number;
  maxScore: number;
  size?: number;
  strokeWidth?: number;
  showPercentage?: boolean;
  showScore?: boolean;
  showLabel?: boolean;
}

/**
 * ScoreRing - Animated circular score visualization
 * Inspired by academic report card aesthetics
 */
export default function ScoreRing({
  score,
  maxScore,
  size = 120,
  strokeWidth = 12,
  showPercentage = true,
  showScore = true,
  showLabel = true,
}: ScoreRingProps) {
  const theme = useTheme();

  const circumference = useMemo(() => {
    return 2 * Math.PI * (size / 2);
  }, [size]);

  const percentage = useMemo(() => {
    if (maxScore === 0) return 0;
    return Math.min(100, Math.round((score / maxScore) * 100));
  }, [score, maxScore]);

  // Determine color based on score range
  const getColor = () => {
    if (percentage >= 90) return theme.palette.success.main; // Excellent - use amber
    if (percentage >= 75) return theme.palette.primary.main; // Good - use blue
    if (percentage >= 60) return theme.palette.primary.main; // Pass
    if (percentage >= 50) return theme.palette.warning.main; // Borderline
    return theme.palette.error.main; // Fail
  };

  const color = getColor();
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* SVG Ring */}
      <Box
        sx={{
          width: size,
          height: size,
          position: 'relative',
        }}
      >
        {/* Background Circle */}
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          style={{ transform: 'rotate(-90deg)' }}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={size / 2 - strokeWidth / 2}
            fill="none"
            stroke={theme.palette.divider}
            strokeWidth={strokeWidth}
          />
          {/* Progress Circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={size / 2 - strokeWidth / 2}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{
              transition: 'stroke-dashoffset 1.5s ease-out',
            }}
          />
        </svg>

        {/* Center Content */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {showScore && (
            <Typography
              variant="h3"
              sx={{
                fontWeight: 700,
                color: color,
                lineHeight: 1,
              }}
            >
              {score}
            </Typography>
          )}

          {showPercentage && (
            <Typography
              variant="caption"
              sx={{
                color: theme.palette.text.secondary,
                mt: 0.5,
              }}
            >
              {percentage}%
            </Typography>
          )}
        </Box>
      </Box>

      {showLabel && (
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            mt: 2,
            fontWeight: 500,
          }}
        >
          得分
        </Typography>
      )}
    </Box>
  );
}
