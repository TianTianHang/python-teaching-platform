# Change: Refactor CodeMirror to Native Implementation

## Why
The platform currently uses `@uiw/react-codemirror`, which is a React wrapper around CodeMirror 6. This introduces an unnecessary abstraction layer, adds dependency maintenance burden, and limits direct access to CodeMirror's native APIs for advanced customization. Migrating to native CodeMirror 6 will reduce bundle size, improve performance, and enable deeper editor customization capabilities.

## What Changes
- Replace `@uiw/react-codemirror` with native `@codemirror/view` and `@codemirror/state` packages
- Replace `@uiw/codemirror-theme-vscode` with `@codemirror/theme-one-dark`
- Update `CodeEditor` component to use native CodeMirror extension system
- Ensure full SSR compatibility with React Router v7 (client-side only initialization)
- Remove all `@uiw/*` CodeMirror-related dependencies
- **BREAKING**: Component API will remain compatible, but internal implementation changes completely

## Impact
- Affected specs:
  - `code-editor` (new spec for code editor capability)
- Affected code:
  - `frontend/web-student/app/components/CodeEditor.tsx` (primary changes)
  - `frontend/web-student/app/routes/_layout.playground.tsx` (usage verification)
  - `frontend/web-student/app/routes/problems.$problemId/AlgorithmProblemPage.tsx` (usage verification)
  - `frontend/web-student/package.json` (dependency updates)
