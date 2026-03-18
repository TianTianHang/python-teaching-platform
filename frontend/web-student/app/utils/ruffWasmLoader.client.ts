// utils/ruffWasmLoader.ts
// Ruff WASM module loader for Python code formatting via CDN

// Type definitions for Ruff WASM module (types not available via CDN import)
export interface Diagnostic {
  // Add fields as needed based on actual usage
  code: string;
  message: string;
  location: {
    row: number;
    column: number;
  };
}

// Position encoding enum
export enum PositionEncoding {
  UTF8 = 0,
  UTF16 = 1,
  UTF32 = 2,
}

// Workspace class interface
export interface Workspace {
  check(code: string): Diagnostic[];
  format(code: string): string;
}

// Module interface matching the actual WASM exports
interface RuffWasmModule {
  initSync(): void;
  Workspace: new (
    settings: Record<string, unknown>,
    positionEncoding: PositionEncoding
  ) => Workspace;
  PositionEncoding: typeof PositionEncoding;
}

type LoadState =
  | { status: 'idle' }
  | { status: 'loading'; promise: Promise<RuffWasmModule> }
  | { status: 'loaded'; module: RuffWasmModule }
  | { status: 'error'; error: Error };

const RUFF_CDN_URL = 'https://cdn.jsdelivr.net/npm/@astral-sh/ruff-wasm-web@0.15.6/+esm';
const RUFF_WASM_URL = 'https://cdn.jsdelivr.net/npm/@astral-sh/ruff-wasm-web@0.15.6/ruff_wasm_bg.wasm';
const LOAD_TIMEOUT = 30000; // 30 seconds timeout

let loadState: LoadState = { status: 'idle' };

/**
 * Load the Ruff WASM module from CDN with lazy loading and timeout handling
 * Automatically initializes the WASM module
 * @returns Promise resolving to the initialized Ruff WASM module
 */
export async function loadRuffWasm(): Promise<RuffWasmModule> {
  // Return cached module if already loaded
  if (loadState.status === 'loaded') {
    return loadState.module;
  }

  // Return existing promise if already loading
  if (loadState.status === 'loading') {
    return loadState.promise;
  }

  // Return error if previously failed
  if (loadState.status === 'error') {
    throw loadState.error;
  }

  // Start loading
  const loadPromise = loadRuffWasmWithTimeout();
  loadState = { status: 'loading', promise: loadPromise };

  return loadPromise;
}

/**
 * Load Ruff WASM with timeout handling and initialization
 */
async function loadRuffWasmWithTimeout(): Promise<RuffWasmModule> {
  const timeoutPromise = new Promise<never>((_, reject) => {
    setTimeout(() => {
      reject(new Error(`Ruff WASM module loading timed out after ${LOAD_TIMEOUT}ms`));
    }, LOAD_TIMEOUT);
  });

  const loadPromise = loadRuffWasmFromCDN();

  try {
    const module = await Promise.race([loadPromise, timeoutPromise]);
    loadState = { status: 'loaded', module };
    return module;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    loadState = { status: 'error', error: err };
    throw err;
  }
}

/**
 * Dynamically import and initialize Ruff WASM from CDN
 */
async function loadRuffWasmFromCDN(): Promise<RuffWasmModule> {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    throw new Error('Ruff WASM can only be loaded in browser environment');
  }

  try {
    // Dynamic import from CDN to get the JS bindings
    const ruff = await import(/* @vite-ignore */ RUFF_CDN_URL);

    // The WASM module from CDN typically exports the module bindings
    const wasmModule = ruff;

    // Check for required exports
    if (!wasmModule.initSync || typeof wasmModule.initSync !== 'function') {
      throw new Error('Ruff WASM module does not export initSync function');
    }

    if (!wasmModule.Workspace) {
      throw new Error('Ruff WASM module does not export Workspace class');
    }

    // Try to initialize - if already initialized, initSync will return early
    try {
      // Check if already initialized by checking if Workspace is usable
      // initSync needs the WASM binary as ArrayBuffer
      // Fetch the WASM file
      const wasmResponse = await fetch(RUFF_WASM_URL);
      if (!wasmResponse.ok) {
        throw new Error(`Failed to fetch WASM: ${wasmResponse.status} ${wasmResponse.statusText}`);
      }

      const wasmBuffer = await wasmResponse.arrayBuffer();
      // Pass as object: { module: ArrayBuffer }
      wasmModule.initSync({ module: wasmBuffer });
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : String(e);
      // If already initialized, that's fine
      if (!errorMsg.includes('already initialized')) {
        console.warn('[Ruff WASM] initSync warning:', errorMsg);
      }
    }

    return {
      initSync: wasmModule.initSync,
      Workspace: wasmModule.Workspace,
      PositionEncoding: wasmModule.PositionEncoding ?? PositionEncoding,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to load Ruff WASM from CDN: ${message}`);
  }
}

/**
 * Create a Ruff Workspace instance for formatting
 * This is a convenience function that loads the WASM and creates a workspace
 */
export async function createRuffWorkspace(
  settings: Record<string, unknown> = {}
): Promise<Workspace> {
  const module = await loadRuffWasm();

  // Default settings for formatting
  const defaultSettings = {
    'line-length': 88,
    'indent-width': 4,
    format: {
      'indent-style': 'space',
      'quote-style': 'double',
    },
  };

  // Merge with user settings
  const mergedSettings = {
    ...defaultSettings,
    ...settings,
    format: {
      ...defaultSettings.format,
      ...(settings.format as Record<string, unknown> ?? {}),
    },
  };

  return new module.Workspace(mergedSettings, PositionEncoding.UTF16);
}

/**
 * Check if Ruff WASM is available (loaded and initialized successfully)
 */
export function isRuffWasmLoaded(): boolean {
  return loadState.status === 'loaded';
}

/**
 * Check if Ruff WASM is currently loading
 */
export function isRuffWasmLoading(): boolean {
  return loadState.status === 'loading';
}

/**
 * Get the current loading state for debugging
 */
export function getRuffLoadState(): LoadState['status'] {
  return loadState.status;
}

/**
 * Reset the loader state (useful for testing)
 */
export function resetRuffLoader(): void {
  loadState = { status: 'idle' };
}
