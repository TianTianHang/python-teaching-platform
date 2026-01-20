import { createContext, useContext, type ReactNode } from 'react';
import { useThemeMode } from '../hooks/useThemeMode';
import type { ThemeMode } from '../theme';

interface ThemeModeContextValue {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  toggleThemeMode: () => void;
}

// Context 定义在独立模块中，避免 HMR 重建
const ThemeModeContext = createContext<ThemeModeContextValue | undefined>(
  undefined
);

/**
 * Hook to access theme mode context
 * Throws error if used outside ThemeModeProvider
 */
export const useThemeModeContext = (): ThemeModeContextValue => {
  const context = useContext(ThemeModeContext);
  if (!context) {
    throw new Error(
      'useThemeModeContext must be used within ThemeModeProvider'
    );
  }
  return context;
};

/**
 * Provider component that wraps the app with theme mode context
 */
export const ThemeModeProvider = ({ children }: { children: ReactNode }) => {
  const themeModeHook = useThemeMode();
  return (
    <ThemeModeContext.Provider value={themeModeHook}>
      {children}
    </ThemeModeContext.Provider>
  );
};
