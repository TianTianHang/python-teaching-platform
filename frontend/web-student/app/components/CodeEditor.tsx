// components/PythonCodeEditor.tsx
import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { vscodeDark } from '@uiw/codemirror-theme-vscode';
import { Box } from '@mui/material';

interface PythonCodeEditorProps {
  code: string;
  onChange?: (value: string) => void;
  maxHeight?: string;
  minHeight?: string;
  readOnly?: boolean;
}

const CodeEditor: React.FC<PythonCodeEditorProps> = ({
  code,
  onChange,
  maxHeight = '400px',
  minHeight ='400px',
  readOnly = false,
}) => {
  return (
   
       <CodeMirror
      value={code}
      maxHeight={maxHeight}
      minHeight={minHeight}
      extensions={[
        python(), // 启用 Python 语法支持
      ]}
      theme={vscodeDark} // 使用 VS Code 暗色主题（可选）
      onChange={onChange}
      basicSetup={{
        lineNumbers: true,
        highlightActiveLine: true,
        highlightSelectionMatches: true,
        bracketMatching: true,
        autocompletion: true,
        closeBrackets: true,
        foldGutter: true,
        indentOnInput: true,
        syntaxHighlighting: true,
      }}
      readOnly={readOnly}
    />
   
   
  );
};

export default CodeEditor;