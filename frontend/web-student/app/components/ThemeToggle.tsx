import { IconButton, Tooltip } from '@mui/material';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import { useThemeModeContext } from '~/contexts/ThemeModeContext';

/**
 * Theme toggle button component
 * Switches between light and dark mode
 */
export default function ThemeToggle() {
  const { themeMode, toggleThemeMode } = useThemeModeContext();
  return (
    <Tooltip
      title={themeMode === 'light' ? '切换到深色模式' : '切换到浅色模式'}
      arrow
    >
      <IconButton
        onClick={(toggleThemeMode)}
        sx={{
          color: 'text.secondary',
          transition: 'all 0.2s ease',
          '&:hover': {
            color: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
        aria-label={themeMode === 'light' ? '切换到深色模式' : '切换到浅色模式'}
      >
        {themeMode === 'light' ? (
          <LightModeIcon sx={{ fontSize: '1.25rem' }} />
        ) : (
          <DarkModeIcon sx={{ fontSize: '1.25rem' }} />
        )}
      </IconButton>
    </Tooltip>
  );
}
