// utils/formatPythonCode.ts
// Python code formatting utility using Ruff WASM

import { createRuffWorkspace, isRuffWasmLoaded, type Workspace } from './ruffWasmLoader.client';

export interface FormatOptions {
  /** Line length for formatting (default: 88, same as Black) */
  lineLength?: number;
  /** Indent width (default: 4) */
  indentWidth?: number;
  /** Indent style: 'space' or 'tab' (default: 'space') */
  indentStyle?: 'space' | 'tab';
  /** Quote style: 'single' or 'double' (default: 'double') */
  quoteStyle?: 'single' | 'double';
}

export interface FormatResult {
  /** Formatted code, or original code if formatting failed */
  code: string;
  /** Whether formatting was successful */
  success: boolean;
  /** Error message if formatting failed */
  error?: string;
}

// Cache the workspace instance to avoid recreating it
let cachedWorkspace: Workspace | null = null;

/**
 * Get or create a cached Workspace instance for formatting
 */
async function getFormattingWorkspace(options: FormatOptions = {}): Promise<Workspace> {
  if (cachedWorkspace) {
    return cachedWorkspace;
  }

  const settings: Record<string, unknown> = {
    'line-length': options.lineLength ?? 88,
    'indent-width': options.indentWidth ?? 4,
    format: {
      'indent-style': options.indentStyle ?? 'space',
      'quote-style': options.quoteStyle ?? 'double',
    },
  };

  cachedWorkspace = await createRuffWorkspace(settings);
  return cachedWorkspace;
}

/**
 * Format Python code using Ruff WASM
 * @param code - The Python code to format
 * @param options - Formatting options
 * @returns Promise resolving to format result with code and success status
 *
 * This function handles:
 * - Lazy loading of Ruff WASM module
 * - Empty code handling (returns empty string without error)
 * - Syntax error handling (returns original code on failure)
 * - Graceful degradation if WASM loading fails
 */
export async function formatPythonCode(
  code: string,
  options: FormatOptions = {}
): Promise<FormatResult> {
  // Handle empty code gracefully
  if (!code || code.trim().length === 0) {
    return { code: code || '', success: true };
  }

  try {
    // Get or create workspace (handles WASM loading internally)
    const workspace = await getFormattingWorkspace(options);

    // Format the code using workspace.format()
    const formatted = workspace.format(code);

    return {
      code: formatted,
      success: true,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);

    // Log error for debugging but don't throw
    console.warn('[formatPythonCode] Formatting failed, using original code:', errorMessage);

    // Return original code on failure (graceful degradation)
    return {
      code,
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Check if Python code can be formatted (Ruff WASM is available)
 * @returns true if formatter is ready to use
 */
export function canFormatPython(): boolean {
  return isRuffWasmLoaded();
}

/**
 * Clear the cached workspace (useful when changing settings)
 */
export function clearFormatCache(): void {
  cachedWorkspace = null;
}

/**
 * Synchronous check if code needs formatting
 * This is a heuristic check - actual formatting requires async call
 * @param code - Code to check
 * @returns true if code appears to need formatting
 */
export function needsFormatting(code: string): boolean {
  if (!code || code.trim().length === 0) {
    return false;
  }

  // Check for common formatting issues:
  // - Mixed tabs and spaces
  // - Trailing whitespace
  // - Multiple consecutive blank lines

  const lines = code.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check for tabs
    if (line.includes('\t')) {
      return true;
    }

    // Check for trailing whitespace
    if (line !== line.trimEnd()) {
      return true;
    }

    // Check for multiple consecutive blank lines (more than 2)
    if (i > 0 && lines[i - 1] === '' && line === '' && i + 1 < lines.length && lines[i + 1] === '') {
      return true;
    }
  }

  return false;
}
