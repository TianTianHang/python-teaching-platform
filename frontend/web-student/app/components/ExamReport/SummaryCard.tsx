import { Box, Typography, useTheme, type SxProps, type Theme } from '@mui/material';
import React from 'react';

interface SummaryCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
  subtitle?: string;
  align?: 'left' | 'center';
  sx?: SxProps<Theme>;
}

/**
 * SummaryCard - Elegant metric card for exam summary
 * Inspired by academic report card aesthetics
 */
export default function SummaryCard({
  title,
  value,
  icon,
  color = 'primary',
  subtitle,
  align = 'left',
  sx = {},
}: SummaryCardProps) {
  const theme = useTheme();

  const colorMap = {
    primary: theme.palette.primary.main,
    success: theme.palette.success.main,
    warning: theme.palette.warning?.main,
    error: theme.palette.error.main,
    neutral: theme.palette.text.secondary,
  };

  const bgColorMap = {
    primary: `${colorMap.primary}08`,
    success: `${colorMap.success}08`,
    warning: `${colorMap.warning}08`,
    error: `${colorMap.error}08`,
    neutral: `${colorMap.neutral}08`,
  };

  const borderColorMap = {
    primary: colorMap.primary,
    success: colorMap.success,
    warning: colorMap.warning,
    error: colorMap.error,
    neutral: 'transparent',
  };

  const baseSx: SxProps<Theme> = {
    backgroundColor: bgColorMap[color],
    borderRadius: 2,
    padding: 2,
    border: `2px solid ${borderColorMap[color]}`,
    transition: 'all 0.3s ease',
    ...(align === 'center' ? {
      textAlign: 'center',
      width: '100%',
    } : {}),
    ...sx,
  };

  return (
    <Box sx={baseSx}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: align === 'center' ? 'center' : 'flex-start',
          gap: 1.5,
          mb: 1,
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            backgroundColor: colorMap[color],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography
            variant="caption"
            sx={{
              color: theme.palette.text.secondary,
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: 0.5,
            }}
          >
            {title}
          </Typography>
        </Box>
      </Box>

      <Typography
        variant="h5"
        sx={{
          fontWeight: 700,
          color: colorMap[color],
          lineHeight: 1.2,
        }}
      >
        {value}
      </Typography>

      {subtitle && (
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            mt: 0.5,
          }}
        >
          {subtitle}
        </Typography>
      )}
    </Box>
  );
}
