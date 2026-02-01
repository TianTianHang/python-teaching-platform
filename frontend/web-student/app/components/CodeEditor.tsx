// components/PythonCodeEditor.tsx
import React, { useEffect, useRef, useState } from 'react';
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

interface PythonCodeEditorProps {
  code: string;
  onChange?: (value: string) => void;
  maxHeight?: string;
  minHeight?: string;
  readOnly?: boolean;
  disablePaste?: boolean;
}

const CodeEditor: React.FC<PythonCodeEditorProps> = ({
  code,
  onChange,
  readOnly = false,
  disablePaste = false,
}) => {
  const editorContainerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [hasMounted, setHasMounted] = useState(false);

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

  return (
  <div
    ref={editorContainerRef}
    // 可选：在 mounted 前隐藏，或者显示 loading 占位符
    style={{ visibility: hasMounted ? 'visible' : 'hidden', height: '90%' }}
  />
);
};

export default CodeEditor;
