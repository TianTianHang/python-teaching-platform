/**
 * SaveStatusIndicator Component
 *
 * Displays the last save time and status in the AppBar.
 * Shows relative time and save type (manual/auto).
 * Click to trigger immediate manual save.
 */

import React, { useState, useEffect } from 'react';
import Tooltip from '@mui/material/Tooltip';
import { useDebounceFn } from 'ahooks';
import SaveIcon from '@mui/icons-material/Save';
import CircularProgress from '@mui/material/CircularProgress';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

/**
 * Props for SaveStatusIndicator component
 */
export interface SaveStatusIndicatorProps {
  lastSavedAt: Date | null;
  saveType: 'auto_save' | 'manual_save' | 'submission' | null;
  isLoading: boolean;
  onManualSave?: () => void;
}

/**
 * Save types with labels
 */
const SAVE_TYPE_LABELS = {
  auto_save: '自动保存',
  manual_save: '手动保存',
  submission: '提交保存',
} as const;

/**
 * Component to display save status
 */
export const SaveStatusIndicator: React.FC<SaveStatusIndicatorProps> = ({
  lastSavedAt,
  saveType,
  isLoading,
  onManualSave,
}) => {
  const [isHovering, setIsHovering] = useState(false);
  const [isClickTriggered, setIsClickTriggered] = useState(false);
  const [relativeTime, setRelativeTime] = useState<string>('');

  // Format relative time
  const formatRelativeTime = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 30) return '刚刚';
    if (diffSeconds < 60) return `${diffSeconds}秒前`;
    if (diffMinutes < 60) return `${diffMinutes}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;

    return date.toLocaleDateString();
  };

  // Update relative time when lastSavedAt changes
  useEffect(() => {
    if (!lastSavedAt) {
      setRelativeTime('');
      return;
    }

    // Initial update
    setRelativeTime(formatRelativeTime(lastSavedAt));

    // Update every 5 seconds for recent saves
    const diffMs = new Date().getTime() - lastSavedAt.getTime();
    const updateInterval = diffMs < 300000 ? 5000 : 30000; // 5 min: 5s, > 5 min: 30s

    const interval = setInterval(() => {
      setRelativeTime(formatRelativeTime(lastSavedAt));
    }, updateInterval);

    return () => clearInterval(interval);
  }, [lastSavedAt]);

  // Debounced manual save on click
  const { run: debouncedManualSave } = useDebounceFn(
    () => {
      onManualSave?.();
    },
    { wait: 300 }
  );

  // Handle click to save
  const handleClick = () => {
    if (!isLoading && !isClickTriggered) {
      setIsClickTriggered(true);
      debouncedManualSave();

      // Reset click trigger after animation
      setTimeout(() => setIsClickTriggered(false), 1500);
    }
  };

  // Determine status for styling
  const getSaveStatus = () => {
    if (isLoading) return 'saving';
    if (isClickTriggered) return 'success';
    if (lastSavedAt) return 'success';
    return 'idle';
  };

  // Get status icon
  const getStatusIcon = () => {
    const status = getSaveStatus();

    switch (status) {
      case 'saving':
        return (
          <CircularProgress
            size={16}
            thickness={2}
            sx={{
              color: 'rgba(91, 77, 255, 0.9)',
            }}
          />
        );

      case 'success':
        return (
          <CheckCircleIcon
            fontSize="small"
            sx={{
              color: 'rgba(16, 185, 129, 0.9)',
              animation: 'checkPop 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          />
        );

      default:
        return null;
    }
  };

  // Get status class names
  const getStatusClassNames = () => {
    const status = getSaveStatus();
    const classes = ['saveStatusIndicator'];

    if (status === 'saving') {
      classes.push('saveStatusIndicatorSaving');
    } else if (status === 'success') {
      classes.push('saveStatusIndicatorSuccess');
    }

    return classes.join(' ');
  };

  // Get save type label
  const getSaveTypeLabel = () => {
    if (!saveType || saveType === 'submission') return '';
    return `(${SAVE_TYPE_LABELS[saveType]})`;
  };

  // Build tooltip content
  const getTooltipContent = () => {
    if (!lastSavedAt) {
      return '点击保存代码';
    }

    const status = getSaveStatus();
    const timestamp = lastSavedAt.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    if (status === 'saving') {
      return `正在保存...`;
    }

    return `最后保存: ${timestamp} ${getSaveTypeLabel()}\n点击立即保存`;
  };

  // Render content
  const renderContent = () => {
    const status = getSaveStatus();
    const showTime = relativeTime;
    const showType = saveType && saveType !== 'submission';

    return (
      <div
        className={getStatusClassNames()}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          cursor: isLoading ? 'default' : 'pointer',
          userSelect: 'none',
        }}
        onClick={handleClick}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {/* Icon */}
        {status === 'saving' ? (
          getStatusIcon()
        ) : (
          <SaveIcon
            fontSize="small"
            sx={{
              fontSize: '16px',
              opacity: 0.8,
              transition: 'all 150ms cubic-bezier(0.4, 0, 0.2, 1)',
              ...(status === 'idle' && {
                '&:hover': {
                  transform: 'scale(1.1)',
                  opacity: 1,
                },
              }),
            }}
          />
        )}

        {/* Time */}
        {showTime && (
          <span className="saveStatusText">
            {relativeTime}
            {showType && ` ${getSaveTypeLabel()}`}
          </span>
        )}
      </div>
    );
  };

  return (
    <Tooltip
      title={getTooltipContent()}
      placement="bottom"
      arrow
      disableInteractive={!isHovering}
      slotProps={{
        tooltip: {
          sx: {
            backgroundColor: 'rgba(30, 30, 30, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            fontSize: '0.875rem',
            lineHeight: 1.4,
            whiteSpace: 'pre-line',
          },
        },
        arrow: {
          sx: {
            color: 'rgba(30, 30, 30, 0.95)',
          },
        },
      }}
    >
      {renderContent()}
    </Tooltip>
  );
};

export default SaveStatusIndicator;
