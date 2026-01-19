/**
 * useEditorLayout Hook
 *
 * Manages the resizable editor layout state with localStorage persistence.
 * Handles horizontal split (problem vs editor) and vertical split (editor vs test results).
 */

import { useState, useEffect } from 'react';

/**
 * Layout configuration interface
 */
export interface EditorLayoutConfig {
  // Horizontal split: percentage for problem panel (0-100)
  horizontalSplit: number;
  // Vertical split: percentage for editor in right panel (0-100)
  editorSize: number;
  // Panel collapsed states
  problemPanelCollapsed: boolean;
  testPanelCollapsed: boolean;
  // Layout mode presets
  layoutMode: 'balanced' | 'editor-focused' | 'problem-focused';
}

/**
 * Default layout configuration
 */
const DEFAULT_LAYOUT: EditorLayoutConfig = {
  horizontalSplit: 45, // Problem panel gets 45% of space
  editorSize: 55,      // Editor gets 55% of right panel
  problemPanelCollapsed: false,
  testPanelCollapsed: false,
  layoutMode: 'balanced',
};

/**
 * Layout presets for different modes
 */
const LAYOUT_PRESETS: Record<EditorLayoutConfig['layoutMode'], Pick<EditorLayoutConfig, 'horizontalSplit' | 'editorSize'>> = {
  balanced: { horizontalSplit: 45, editorSize: 55 },
  'editor-focused': { horizontalSplit: 20, editorSize: 70 },
  'problem-focused': { horizontalSplit: 60, editorSize: 40 },
};

/**
 * Local storage key
 */
const STORAGE_KEY = 'problem-page-layout';

/**
 * Load layout from localStorage
 */
function loadLayoutFromStorage(): EditorLayoutConfig {
  if (typeof window === 'undefined') {
    return DEFAULT_LAYOUT;
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return DEFAULT_LAYOUT;
    }

    const parsed = JSON.parse(stored) as Partial<EditorLayoutConfig>;

    // Validate and merge with defaults
    return {
      horizontalSplit: validateNumber(parsed.horizontalSplit, DEFAULT_LAYOUT.horizontalSplit, 10, 90),
      editorSize: validateNumber(parsed.editorSize, DEFAULT_LAYOUT.editorSize, 20, 90),
      problemPanelCollapsed: parsed.problemPanelCollapsed ?? DEFAULT_LAYOUT.problemPanelCollapsed,
      testPanelCollapsed: parsed.testPanelCollapsed ?? DEFAULT_LAYOUT.testPanelCollapsed,
      layoutMode: parsed.layoutMode ?? DEFAULT_LAYOUT.layoutMode,
    };
  } catch (error) {
    console.error('Failed to load layout from storage:', error);
    return DEFAULT_LAYOUT;
  }
}

/**
 * Validate and clamp a number between min and max
 */
function validateNumber(value: unknown, defaultValue: number, min: number, max: number): number {
  if (typeof value !== 'number' || isNaN(value)) {
    return defaultValue;
  }
  return Math.max(min, Math.min(max, value));
}

/**
 * Save layout to localStorage
 */
function saveLayoutToStorage(layout: EditorLayoutConfig): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
  } catch (error) {
    console.error('Failed to save layout to storage:', error);
  }
}

/**
 * Custom hook for managing editor layout state
 *
 * @returns Layout state and updater functions
 *
 * @example
 * ```tsx
 * const { layout, updateHorizontalSplit, updateEditorSize, setLayoutMode } = useEditorLayout();
 *
 * return (
 *   <PanelGroup direction="horizontal">
 *     <Panel defaultSize={layout.horizontalSplit}>...</Panel>
 *     <PanelResizeHandle />
 *     <Panel defaultSize={100 - layout.horizontalSplit}>...</Panel>
 *   </PanelGroup>
 * );
 * ```
 */
export function useEditorLayout() {
  const [layout, setLayout] = useState<EditorLayoutConfig>(loadLayoutFromStorage);

  // Save to localStorage whenever layout changes
  useEffect(() => {
    saveLayoutToStorage(layout);
  }, [layout]);

  /**
   * Update horizontal split percentage
   * @param size - New percentage (0-100)
   */
  const updateHorizontalSplit = (size: number) => {
    setLayout((prev) => ({
      ...prev,
      horizontalSplit: validateNumber(size, prev.horizontalSplit, 10, 90),
    }));
  };

  /**
   * Update editor size percentage
   * @param size - New percentage (0-100)
   */
  const updateEditorSize = (size: number) => {
    setLayout((prev) => ({
      ...prev,
      editorSize: validateNumber(size, prev.editorSize, 20, 90),
    }));
  };

  /**
   * Toggle problem panel collapsed state
   */
  const toggleProblemPanel = () => {
    setLayout((prev) => ({
      ...prev,
      problemPanelCollapsed: !prev.problemPanelCollapsed,
    }));
  };

  /**
   * Toggle test results panel collapsed state
   */
  const toggleTestPanel = () => {
    setLayout((prev) => ({
      ...prev,
      testPanelCollapsed: !prev.testPanelCollapsed,
    }));
  };

  /**
   * Set layout mode preset
   * @param mode - Layout mode to apply
   */
  const setLayoutMode = (mode: EditorLayoutConfig['layoutMode']) => {
    const preset = LAYOUT_PRESETS[mode];
    setLayout((prev) => ({
      ...prev,
      layoutMode: mode,
      ...preset,
    }));
  };

  /**
   * Reset layout to defaults
   */
  const resetLayout = () => {
    setLayout(DEFAULT_LAYOUT);
  };

  return {
    layout,
    updateHorizontalSplit,
    updateEditorSize,
    toggleProblemPanel,
    toggleTestPanel,
    setLayoutMode,
    resetLayout,
  };
}
