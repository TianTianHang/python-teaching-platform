import { createTheme, type Theme, type ThemeOptions } from '@mui/material/styles';
import { useMemo } from 'react';

export type ThemeMode = 'light' | 'dark';

/**
 * Base theme configuration options shared between light and dark themes
 */
const baseThemeOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    fontSize: 14, // 基础字号
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.3,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      lineHeight: 1.4,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.5,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    // 语义化文本样式
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.75,
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.57,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.75,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      textTransform: 'none',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 1.66,
      color: 'text.secondary',
    },
    overline: {
      fontSize: '0.625rem',
      lineHeight: 2.5,
      fontWeight: 600,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          transition: 'background-color 0.3s ease, color 0.3s ease',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
};

/**
 * Light theme configuration
 */
const getLightTheme = (): Theme => {
  return createTheme({
    ...baseThemeOptions,
    palette: {
      mode: 'light',
      primary: {
        main: '#5B4DFF',
        light: '#8B7FFF',
        dark: '#3A2BD9',
        contrastText: '#FFFFFF',
      },
      secondary: {
        main: '#7C4DFF',
        light: '#B07CFF',
        dark: '#3D1B9E',
        contrastText: '#FFFFFF',
      },
      background: {
        default: '#FAFAFA',
        paper: '#FFFFFF',
      },
      text: {
        primary: 'rgba(0, 0, 0, 0.87)',
        secondary: 'rgba(0, 0, 0, 0.6)',
        disabled: 'rgba(0, 0, 0, 0.38)',
      },
      divider: 'rgba(0, 0, 0, 0.12)',
      success: {
        main: '#10B981',
        light: '#34D399',
        dark: '#059669',
        contrastText: '#FFFFFF',
      },
      warning: {
        main: '#F59E0B',
        light: '#FBBF24',
        dark: '#D97706',
        contrastText: '#FFFFFF',
      },
      error: {
        main: '#EF4444',
        light: '#F87171',
        dark: '#DC2626',
        contrastText: '#FFFFFF',
      },
      info: {
        main: '#3B82F6',
        light: '#60A5FA',
        dark: '#2563EB',
        contrastText: '#FFFFFF',
      },
      grey: {
        50: '#FAFAFA',
        100: '#F5F5F5',
        200: '#EEEEEE',
        300: '#E0E0E0',
        400: '#BDBDBD',
        500: '#9E9E9E',
        600: '#757575',
        700: '#616161',
        800: '#424242',
        900: '#212121',
      },
    },
    shadows: [
      'none',
      '0 2px 4px rgba(0,0,0,0.05)',
      '0 4px 8px rgba(0,0,0,0.08)',
      '0 6px 12px rgba(0,0,0,0.10)',
      '0 8px 16px rgba(0,0,0,0.12)',
      '0 12px 24px rgba(0,0,0,0.14)',
      '0 16px 32px rgba(0,0,0,0.16)',
      '0 20px 40px rgba(0,0,0,0.18)',
      '0 24px 48px rgba(0,0,0,0.20)',
      '0 28px 56px rgba(0,0,0,0.22)',
      '0 32px 64px rgba(0,0,0,0.24)',
      '0 36px 72px rgba(0,0,0,0.26)',
      '0 40px 80px rgba(0,0,0,0.28)',
      '0 44px 88px rgba(0,0,0,0.30)',
      '0 48px 96px rgba(0,0,0,0.32)',
      '0 52px 104px rgba(0,0,0,0.34)',
      '0 56px 112px rgba(0,0,0,0.36)',
      '0 60px 120px rgba(0,0,0,0.38)',
      '0 64px 128px rgba(0,0,0,0.40)',
      '0 68px 136px rgba(0,0,0,0.42)',
      '0 72px 144px rgba(0,0,0,0.44)',
      '0 76px 152px rgba(0,0,0,0.46)',
      '0 80px 160px rgba(0,0,0,0.48)',
      '0 84px 168px rgba(0,0,0,0.50)',
      '0 88px 176px rgba(0,0,0,0.52)',
    ],
  });
};

/**
 * Dark theme configuration
 */
const getDarkTheme = (): Theme => {
  return createTheme({
    ...baseThemeOptions,
    palette: {
      mode: 'dark',
      primary: {
        main: '#7B6DFF',
        light: '#9B8FFF',
        dark: '#5B4DFF',
        contrastText: '#FFFFFF',
      },
      secondary: {
        main: '#9C7DFF',
        light: '#C0ADFF',
        dark: '#6D4DD9',
        contrastText: '#FFFFFF',
      },
      background: {
        default: '#121212',
        paper: '#1E1E1E',
      },
      text: {
        primary: 'rgba(255, 255, 255, 0.87)',
        secondary: 'rgba(255, 255, 255, 0.6)',
        disabled: 'rgba(255, 255, 255, 0.38)',
      },
      divider: 'rgba(255, 255, 255, 0.12)',
      success: {
        main: '#34D399',
        light: '#6EE7B7',
        dark: '#10B981',
        contrastText: '#FFFFFF',
      },
      warning: {
        main: '#FBBF24',
        light: '#FCD34D',
        dark: '#F59E0B',
        contrastText: '#FFFFFF',
      },
      error: {
        main: '#F87171',
        light: '#FCA5A5',
        dark: '#EF4444',
        contrastText: '#FFFFFF',
      },
      info: {
        main: '#60A5FA',
        light: '#93C5FD',
        dark: '#3B82F6',
        contrastText: '#FFFFFF',
      },
      grey: {
        50: '#FAFAFA',
        100: '#F5F5F5',
        200: '#EEEEEE',
        300: '#E0E0E0',
        400: '#BDBDBD',
        500: '#9E9E9E',
        600: '#757575',
        700: '#616161',
        800: '#424242',
        900: '#212121',
        A100: '#D4D4D4',
        A200: '#A0A0A0',
        A400: '#6B6B6B',
        A700: '#404040',
      },
    },
    shadows: [
      'none',
      '0 2px 4px rgba(0,0,0,0.4)',
      '0 4px 8px rgba(0,0,0,0.5)',
      '0 6px 12px rgba(0,0,0,0.6)',
      '0 8px 16px rgba(0,0,0,0.7)',
      '0 12px 24px rgba(0,0,0,0.8)',
      '0 16px 32px rgba(0,0,0,0.9)',
      '0 20px 40px rgba(0,0,0,0.10)',
      '0 24px 48px rgba(0,0,0,0.11)',
      '0 28px 56px rgba(0,0,0,0.12)',
      '0 32px 64px rgba(0,0,0,0.13)',
      '0 36px 72px rgba(0,0,0,0.14)',
      '0 40px 80px rgba(0,0,0,0.15)',
      '0 44px 88px rgba(0,0,0,0.16)',
      '0 48px 96px rgba(0,0,0,0.17)',
      '0 52px 104px rgba(0,0,0,0.18)',
      '0 56px 112px rgba(0,0,0,0.19)',
      '0 60px 120px rgba(0,0,0,0.20)',
      '0 64px 128px rgba(0,0,0,0.21)',
      '0 68px 136px rgba(0,0,0,0.22)',
      '0 72px 144px rgba(0,0,0,0.23)',
      '0 76px 152px rgba(0,0,0,0.24)',
      '0 80px 160px rgba(0,0,0,0.25)',
      '0 84px 168px rgba(0,0,0,0.26)',
      '0 88px 176px rgba(0,0,0,0.27)',
    ],
  });
};

/**
 * Custom hook to get theme based on mode
 * Memoized to prevent recreation on every render
 */
export const useTheme = (mode: ThemeMode): Theme => {
  return useMemo(() => {
    return mode === 'dark' ? getDarkTheme() : getLightTheme();
  }, [mode]);
};

/**
 * Get theme by mode (for non-component usage)
 */
export const getTheme = (mode: ThemeMode): Theme => {
  return mode === 'dark' ? getDarkTheme() : getLightTheme();
};

export { getLightTheme, getDarkTheme };
