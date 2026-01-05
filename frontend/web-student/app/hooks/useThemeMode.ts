import { useState, useEffect, useCallback } from 'react';
import { type ThemeMode } from '../theme';

const THEME_MODE_STORAGE_KEY = 'theme-mode';

/**
 * Custom hook to manage theme mode with localStorage persistence
 * and system preference detection
 */
export const useThemeMode = () => {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    // Initialize from localStorage or system preference
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(THEME_MODE_STORAGE_KEY);
      if (stored && (stored === 'light' || stored === 'dark')) {
        return stored as ThemeMode;
      }

      // Check system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    return 'light';
  });

  const [mounted, setMounted] = useState(false);

  // Set mounted state after first render
  useEffect(() => {
    setMounted(true);
  }, []);

  /**
   * Set theme mode and persist to localStorage
   */
  const setThemeMode = useCallback(
    (valueOrUpdater: ThemeMode | ((prev: ThemeMode) => ThemeMode)) => {
      setThemeModeState((prev) => {
        const newMode =
          typeof valueOrUpdater === 'function'
            ? valueOrUpdater(prev)
            : valueOrUpdater;
         
        // 同步到 localStorage 和 DOM
        if (typeof window !== 'undefined') {
          localStorage.setItem(THEME_MODE_STORAGE_KEY, newMode);
          document.documentElement.setAttribute('data-theme', newMode);
        }
        return newMode;
      });
    },
    []
  );

  /**
   * Toggle between light and dark mode
   */
  const toggleThemeMode = useCallback(() => {
    setThemeMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, [setThemeMode]);

  // Listen for system preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't set a preference
      if (!localStorage.getItem(THEME_MODE_STORAGE_KEY)) {
        setThemeModeState(e.matches ? 'dark' : 'light');
      }
    };

    // Add listener (modern browsers)
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Fallback for older browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  // Set initial data-theme attribute
  useEffect(() => {
    if (mounted && typeof window !== 'undefined') {
      document.documentElement.setAttribute('data-theme', themeMode);
    }
  }, [themeMode, mounted]);

  return {
    themeMode,
    setThemeMode,
    setThemeModeState,
    toggleThemeMode,
    mounted,
  };
};
