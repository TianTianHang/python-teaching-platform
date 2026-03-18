// components/PythonCodeEditor.tsx
import { useEffect, useRef, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import { Box, Tooltip, IconButton } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { EditorState, Compartment } from '@codemirror/state';
import {
  EditorView,
  keymap,
  highlightActiveLine,
  highlightActiveLineGutter,
  lineNumbers,
  highlightSpecialChars,
  drawSelection,
  dropCursor,
  rectangularSelection,
  crosshairCursor,
} from '@codemirror/view';
import { defaultKeymap, history, historyKeymap, insertTab, indentLess } from '@codemirror/commands';
import { indentOnInput, bracketMatching, foldGutter } from '@codemirror/language';
import { autocompletion, completionKeymap, closeBrackets, closeBracketsKeymap } from '@codemirror/autocomplete';
import { lintKeymap } from '@codemirror/lint';
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { showNotification } from './Notification';
import { formatPythonCode } from '../utils/formatPythonCode';

export interface CodeEditorRef {
  /** Get the current editor content */
  getCode: () => string;
  /** Programmatically format the code */
  formatCode: () => Promise<void>;
  /** Get the EditorView instance */
  getEditorView: () => EditorView | null;
}

interface PythonCodeEditorProps {
  code: string;
  onChange?: (value: string) => void;
  maxHeight?: string;
  minHeight?: string;
  readOnly?: boolean;
  disablePaste?: boolean;
  /** Whether to automatically format code when it loads (default: true) */
  formatOnLoad?: boolean;
}

const CodeEditor = forwardRef<CodeEditorRef, PythonCodeEditorProps>((
  {
    code,
    onChange,
    readOnly = false,
    disablePaste = false,
    formatOnLoad = true,
  },
  ref
) => {
  const editorContainerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [hasMounted, setHasMounted] = useState(false);
  const [isFormatting, setIsFormatting] = useState(false);
  const initialCodeRef = useRef(code);
  const hasFormattedRef = useRef(false);

  // Create compartments for dynamic reconfiguration
  const readOnlyCompartment = useRef(new Compartment());
  const disablePasteCompartment = useRef(new Compartment());

  // Create paste prevention extension
  const createPastePreventionExtension = () => {
    return EditorView.domEventHandlers({
      paste: (event: ClipboardEvent) => {
        if (disablePaste) {
          event.preventDefault();
          showNotification('warning', '粘贴已禁用', '为了帮助您更好地学习编程，此编辑器不允许粘贴操作。请手动输入代码以加深理解。');
          return true;
        }
        return false;
      },
      contextmenu: (_event: MouseEvent) => {
        if (disablePaste) {
          // Let context menu open but we'll handle paste via paste event
          return false;
        }
        return false;
      },
    });
  };

  // Format code using Ruff WASM
  const formatCode = useCallback(async (): Promise<void> => {
    if (!viewRef.current || readOnly || isFormatting) {
      return;
    }

    const view = viewRef.current;
    const currentCode = view.state.doc.toString();

    // Skip if empty
    if (!currentCode.trim()) {
      return;
    }

    setIsFormatting(true);

    try {
      const result = await formatPythonCode(currentCode);

      if (result.success && result.code !== currentCode) {
        // Calculate cursor position adjustment
        const selection = view.state.selection;
        const from = selection.main.from;
        const to = selection.main.to;

        // Update the document with formatted code
        view.dispatch({
          changes: {
            from: 0,
            to: currentCode.length,
            insert: result.code,
          },
          // Try to preserve cursor position approximately
          selection: { anchor: Math.min(from, result.code.length), head: Math.min(to, result.code.length) },
        });

        // Notify parent of change
        if (onChange) {
          onChange(result.code);
        }
      }
    } catch (error) {
      // Silently fail - formatting errors should not break the editor
      console.warn('[CodeEditor] Formatting failed:', error);
    } finally {
      setIsFormatting(false);
    }
  }, [readOnly, isFormatting, onChange]);

  // Auto-format on initial load
  const autoFormatOnLoad = useCallback(async () => {
    if (!formatOnLoad || !viewRef.current || hasFormattedRef.current) {
      return;
    }

    const view = viewRef.current;
    const codeToFormat = view.state.doc.toString();

    // Skip if empty
    if (!codeToFormat.trim()) {
      hasFormattedRef.current = true;
      return;
    }

    setIsFormatting(true);

    try {
      const result = await formatPythonCode(codeToFormat);

      if (result.success && result.code !== codeToFormat) {
        view.dispatch({
          changes: {
            from: 0,
            to: codeToFormat.length,
            insert: result.code,
          },
        });

        // Notify parent of change
        if (onChange) {
          onChange(result.code);
        }
      }
    } catch (error) {
      // Silently fail on initial load
      console.warn('[CodeEditor] Auto-format on load failed:', error);
    } finally {
      setIsFormatting(false);
      hasFormattedRef.current = true;
    }
  }, [formatOnLoad, onChange]);

  const extensions = [
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightSpecialChars(),
    history(),
    foldGutter(),
    drawSelection(),
    dropCursor(),
    EditorState.allowMultipleSelections.of(true),
    indentOnInput(),
    bracketMatching(),
    closeBrackets(),
    autocompletion(),
    rectangularSelection(),
    crosshairCursor(),
    highlightActiveLine(),
    highlightSelectionMatches(),
    keymap.of([
      ...closeBracketsKeymap,
      { key: 'Tab', run: insertTab },
      { key: 'Shift-Tab', run: indentLess },
      // Format keyboard shortcut: Shift+Alt+F (matches VS Code)
      { key: 'Shift-Alt-f', run: () => { void formatCode(); return true; } },
      { key: 'Shift-Alt-F', run: () => { void formatCode(); return true; } },
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
      ...completionKeymap,
      ...lintKeymap,
    ]),
    oneDark,
    python(),
    readOnlyCompartment.current.of(EditorState.readOnly.of(readOnly)),
    disablePasteCompartment.current.of(createPastePreventionExtension()),
    EditorView.theme({
      '&': {
        height: '100%',
      },
      '&.cm-focused': {
        outline: 'none',
      },
    }),
    // onChange handler
    EditorView.updateListener.of((update) => {
      if (update.docChanged && onChange) {
        const newCode = update.state.doc.toString();
        onChange(newCode);
      }
    }),
  ];

  useEffect(() => {
    // SSR compatibility: Only initialize on client-side
    if (typeof window === 'undefined' || !editorContainerRef.current) {
      return;
    }

    setHasMounted(true);
    // Create the editor state
    const state = EditorState.create({
      doc: code,
      extensions,
    });

    // Create the editor view
    const view = new EditorView({
      state,
      parent: editorContainerRef.current,
    });

    viewRef.current = view;

    // Cleanup on unmount
    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // Only run on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update code content when prop changes
  useEffect(() => {
    if (viewRef.current && hasMounted) {
      const currentDoc = viewRef.current.state.doc.toString();
      if (currentDoc !== code) {
        viewRef.current.dispatch({
          changes: {
            from: 0,
            to: currentDoc.length,
            insert: code,
          },
        });
      }
    }
  }, [code, hasMounted]);

  // Update readOnly mode
  useEffect(() => {
    if (viewRef.current && hasMounted) {
      viewRef.current.dispatch({
        effects: readOnlyCompartment.current.reconfigure(EditorState.readOnly.of(readOnly)),
      });
    }
  }, [readOnly, hasMounted]);

  // Update disablePaste mode
  useEffect(() => {
    if (viewRef.current && hasMounted) {
      viewRef.current.dispatch({
        effects: disablePasteCompartment.current.reconfigure(createPastePreventionExtension()),
      });
    }
  }, [disablePaste, hasMounted]);

  // Auto-format on initial load
  useEffect(() => {
    if (hasMounted && viewRef.current && !hasFormattedRef.current) {
      // Reset formatted flag when code prop changes significantly
      if (code !== initialCodeRef.current) {
        hasFormattedRef.current = false;
        initialCodeRef.current = code;
      }

      // Trigger auto-format
      void autoFormatOnLoad();
    }
  }, [hasMounted, code, autoFormatOnLoad]);

  // Expose imperative methods via ref
  useImperativeHandle(ref, () => ({
    getCode: () => viewRef.current?.state.doc.toString() ?? '',
    formatCode: async () => { await formatCode(); },
    getEditorView: () => viewRef.current,
  }), [formatCode]);

  // Show format shortcut hint on mount (only once)
  useEffect(() => {
    if (hasMounted && !readOnly) {
      // Show hint once when editor loads
      const hasShownHint = sessionStorage.getItem('codeEditorFormatHint');
      if (!hasShownHint) {
        sessionStorage.setItem('codeEditorFormatHint', '1');
      }
    }
  }, [hasMounted, readOnly]);

  return (
    <Box sx={{ position: 'relative', height: '90%', visibility: hasMounted ? 'visible' : 'hidden' }}>
      <div
        ref={editorContainerRef}
        style={{ height: '100%' }}
      />
      {/* Format shortcut hint icon */}
      {!readOnly && (
        <Tooltip title="按 Shift+Alt+F 格式化代码" placement="top" arrow>
          <IconButton
            size="small"
            sx={{
              position: 'absolute',
              bottom: 8,
              right: 8,
              zIndex: 10,
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <InfoOutlinedIcon fontSize="small" sx={{ color: 'rgba(255, 255, 255, 0.6)' }} />
          </IconButton>
        </Tooltip>
      )}
    </Box>
  );
});

CodeEditor.displayName = 'CodeEditor';

export default CodeEditor;
