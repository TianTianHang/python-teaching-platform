// components/ProblemStatusChip.jsx
import React from 'react';
import Chip, { type ChipProps } from '@mui/material/Chip';
import CheckIcon from '@mui/icons-material/Check';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import CloseIcon from '@mui/icons-material/Close';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import type { ProblemStatus } from '~/types/course';

const statusConfig:Record<ProblemStatus, {label:string;
    color:ChipProps['color'];
    icon:React.ReactElement
}>= {
  not_started: {
    label: '未开始',
    color: 'default', // 或 'grey'
    icon: <PlayArrowIcon />,
  },
  in_progress: {
    label: '进行中',
    color: 'info',
    icon: <HourglassEmptyIcon />,
  },
  solved: {
    label: '已解决',
    color: 'success',
    icon: <CheckIcon />,
  },
  failed: {
    label: '失败',
    color: 'error',
    icon: <CloseIcon />,
  },
};

export default function ProblemStatusChip({ status }:{status:ProblemStatus}) {
  const config = statusConfig[status] || statusConfig.not_started;

  return (
    <Chip
      icon={config.icon}
      label={config.label}
      color={config.color}
      size="small"
      variant="outlined"
      sx={{
        fontWeight: 'medium',
        '& .MuiChip-icon': {
          color: 'inherit',
        },
      }}
    />
  );
}