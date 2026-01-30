# Tasks: Fix CodeMirror Tab Key Navigation

## Task List

### 1. Update CodeEditor component imports
- [x] Add `indentWithTab` to the import statement from `@codemirror/commands`
- [x] Location: `frontend/web-student/app/components/CodeEditor.tsx` (line 16)

### 2. Configure Tab key handling in keymap
- [x] Add `indentWithTab` to the `keymap.of()` array before `defaultKeymap`
- [x] Location: `frontend/web-student/app/components/CodeEditor.tsx` (lines 86-93)
- [x] Verify keymap order ensures proper priority

### 3. Verify TypeScript compilation
- [x] Run `pnpm run typecheck` to ensure no type errors
- [x] Location: `frontend/web-student/`

### 4. Manual testing - Playground page
- [ ] Navigate to `/playground`
- [ ] Click in the code editor to focus
- [ ] Press Tab key - should insert indentation (4 spaces or 1 tab based on Python mode)
- [ ] Press Shift+Tab key - should reduce indentation
- [ ] Select multiple lines and press Tab - all lines should indent
- [ ] Verify focus stays in the editor

### 5. Manual testing - Algorithm Problem page
- [ ] Navigate to any algorithm problem page (`/problems/:id`)
- [ ] Click in the code editor to focus
- [ ] Press Tab key - should insert indentation
- [ ] Press Shift+Tab key - should reduce indentation
- [ ] Verify focus stays in the editor

### 6. Verify paste prevention still works
- [ ] Test with `disablePaste={true}` enabled
- [ ] Verify Tab/Shift+Tab still works when paste is disabled
- [ ] Verify paste is still blocked (Ctrl+V should show notification)

### 7. Regression testing
- [ ] Test all other editor shortcuts (Ctrl+Z, Ctrl+Y, Ctrl+F, etc.)
- [ ] Verify autocompletion still works (Ctrl+Space)
- [ ] Verify bracket matching and auto-closing brackets still work
- [ ] Verify code folding still works
- [ ] Check console for any errors or warnings

## Notes
- No backend changes required
- No database migrations required
- Changes are isolated to the frontend CodeEditor component
- This is a pure bug fix with minimal risk
