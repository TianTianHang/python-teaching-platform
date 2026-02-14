/**
 * FoldableBlock component for rendering collapsible markdown content.
 * Supports four types: fold, answer, warning, tip with unified modern styling.
 *
 * Features:
 * - SSR compatible (no browser-only APIs)
 * - Type-specific icons with unified styling
 * - Configurable default expanded state
 * - Nested markdown content support
 * - Smooth animations and modern aesthetics
 */

'use client';

import { Accordion, AccordionDetails, AccordionSummary, Typography, useTheme, Box } from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Warning,
  TipsAndUpdates,
} from '@mui/icons-material';

export type FoldableBlockType = 'fold' | 'answer' | 'warning' | 'tip';

export interface FoldableBlockProps {
  type: FoldableBlockType;
  title?: string;
  defaultExpanded?: boolean;
  children: React.ReactNode;
}

/**
 * Default titles for each block type when not specified
 */
const DEFAULT_TITLES: Record<FoldableBlockType, string> = {
  fold: 'Details',
  answer: 'Answer',
  warning: 'Warning',
  tip: 'Tip',
};

/**
 * Icon configuration for each block type
 */
const TYPE_ICONS: Record<FoldableBlockType, React.ComponentType<{ className?: string }>> = {
  fold: ExpandMore,
  answer: CheckCircle,
  warning: Warning,
  tip: TipsAndUpdates,
};

/**
 * Get default expanded state for a given block type
 */
function getDefaultExpanded(type: FoldableBlockType): boolean {
  switch (type) {
    case 'fold':
      return false;
    case 'answer':
      return false;
    case 'warning':
      return true;
    case 'tip':
      return true;
  }
}

/**
 * FoldableBlock component renders collapsible content using Material-UI Accordion.
 * Features unified modern styling with type-specific iconography.
 */
export default function FoldableBlock({ type, title, defaultExpanded, children }: FoldableBlockProps) {
  const theme = useTheme();

  const isDefaultExpanded = defaultExpanded ?? getDefaultExpanded(type);
  const displayTitle = title ?? DEFAULT_TITLES[type];
  const TypeIcon = TYPE_ICONS[type];

  return (
    <Box
      sx={{
        my: 2.5,
        position: 'relative',
        borderRadius: 2,
        overflow: 'hidden',
        background: theme.palette.background.paper,
        border: '1px solid',
        borderColor: 'divider',
        transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          borderColor: 'primary.main',
          boxShadow: `0 2px 8px ${theme.palette.primary.main}10`,
        },
        '& .MuiAccordion-root': {
          boxShadow: 'none',
          borderRadius: 0,
          '&:before': {
            display: 'none',
          },
          '&.Mui-expanded': {
            margin: 0,
          },
          '&.Mui-expanded + .MuiCollapse-root': {
            mt: 0,
          },
        },
        '& .MuiAccordionSummary-root': {
          px: 2,
          py: 1.5,
          minHeight: 'auto',
          display: 'flex',
          alignItems: 'center',
          cursor: 'pointer',
          transition: 'background-color 0.2s ease',
          '&:hover': {
            backgroundColor: theme.palette.action.hover,
          },
          '&.Mui-expanded': {
            minHeight: 'auto',
            backgroundColor: theme.palette.action.hover,
          },
        },
        '& .MuiAccordionSummary-content': {
          margin: 0,
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
        },
        '& .MuiAccordionSummary-expandIconWrapper': {
          transform: 'rotate(0deg)',
          transition: 'transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          '&.Mui-expanded': {
            transform: 'rotate(180deg)',
          },
        },
        '& .MuiAccordionDetails-root': {
          px: 2,
          pb: 2,
          pt: 0,
          backgroundColor: 'transparent',
          '& > *:first-child': {
            mt: 0.5,
          },
        },
      }}
    >
      <Accordion defaultExpanded={isDefaultExpanded} sx={{ boxShadow: 'none' }}>
        <AccordionSummary
          expandIcon={
            <ExpandMore
              sx={{
                color: 'text.secondary',
                fontSize: 22,
              }}
            />
          }
        >
          {/* Type-specific icon */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 32,
              height: 32,
              borderRadius: 1.5,
              bgcolor: type === 'fold'
                ? 'action.selected'
                : type === 'answer'
                ? 'primary.100'
                : type === 'warning'
                ? 'warning.100'
                : 'success.100',
              color: type === 'fold'
                ? 'text.primary'
                : type === 'answer'
                ? 'primary.700'
                : type === 'warning'
                ? 'warning.700'
                : 'success.700',
              transition: 'all 0.2s ease',
              fontSize: 18,
            }}
          >
            <TypeIcon />
          </Box>

          {/* Title */}
          <Typography
            variant="body1"
            sx={{
              fontWeight: 600,
              color: 'text.primary',
              fontSize: '0.95rem',
              letterSpacing: '-0.01em',
            }}
          >
            {displayTitle}
          </Typography>
        </AccordionSummary>

        <AccordionDetails>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              lineHeight: 1.7,
              fontSize: '0.9rem',
            }}
          >
            {children}
          </Typography>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
