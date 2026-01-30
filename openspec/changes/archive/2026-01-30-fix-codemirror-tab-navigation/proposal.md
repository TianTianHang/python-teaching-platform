# Proposal: Fix CodeMirror Tab Key Navigation

## Change ID
`fix-codemirror-tab-navigation`

## Summary
Fix the CodeMirror code editor component where pressing the Tab key causes focus to leave the editor instead of inserting a tab/indentation. This breaks the expected code editing workflow where Tab is used for code indentation.

## Problem Statement
**Current Behavior**: When users press the Tab key while editing code in the CodeEditor component (used in Playground and Algorithm Problem pages), the focus moves to the next focusable element on the page instead of inserting a tab character or indenting the current line.

**Expected Behavior**: Pressing Tab should insert indentation in the editor, and pressing Shift+Tab should reduce indentation. The editor should capture and handle these key events to provide a proper code editing experience.

**Impact**: This issue affects all users writing code in:
- Playground page (`/playground`)
- Algorithm problem pages (`/problems/:id`)

Users cannot use Tab for indentation, forcing them to manually type spaces, which significantly degrades the coding experience.

## Root Cause Analysis
The CodeEditor component ([CodeEditor.tsx](frontend/web-student/app/components/CodeEditor.tsx)) includes `defaultKeymap` from `@codemirror/commands` (line 88), which should contain the `insertTab` command. However, the browser's default Tab navigation behavior may not be properly prevented.

Key observations:
1. The editor configuration includes multiple keymaps: `closeBracketsKeymap`, `defaultKeymap`, `searchKeymap`, `historyKeymap`, `completionKeymap`, `lintKeymap`
2. The `defaultKeymap` should handle Tab key with `insertTab` command
3. The issue likely stems from missing explicit Tab key binding or priority issues in keymap handling

## Proposed Solution
Add explicit Tab key bindings to ensure the editor captures and handles Tab/Shift+Tab events before the browser's default navigation behavior takes effect.

### Implementation Approach
1. Import `indentWithTab` from `@codemirror/commands`
2. Add `indentWithTab` to the keymap configuration with higher priority
3. This ensures Tab and Shift+Tab are handled by the editor for indentation

### Code Changes
```typescript
// Add import
import { indentWithTab } from '@codemirror/commands';

// Update keymap configuration (line 86-93)
keymap.of([
  ...closeBracketsKeymap,
  indentWithTab,  // Add this before defaultKeymap for higher priority
  ...defaultKeymap,
  ...searchKeymap,
  ...historyKeymap,
  ...completionKeymap,
  ...lintKeymap,
]),
```

## Alternatives Considered
1. **Using custom key bindings**: Could create custom Tab handler, but `indentWithTab` is the recommended CodeMirror utility
2. **DOM event handling**: Could prevent default at DOM level, but CodeMirror's keymap system is the proper approach
3. **CSS tabindex manipulation**: Would not solve the root cause and could introduce other accessibility issues

## Affected Components
- [CodeEditor.tsx](frontend/web-student/app/components/CodeEditor.tsx)

## Related Specs
- `code-editor` - The fix addresses keyboard interaction requirements for the code editor

## Testing Plan
1. **Manual Testing**:
   - Open Playground page
   - Press Tab in editor - should insert indentation, not move focus
   - Press Shift+Tab - should reduce indentation
   - Test with multi-line selection - Tab should indent all selected lines
   - Verify paste prevention still works with Tab/Shift+Tab

2. **Affected Pages**:
   - `/playground` - CodeEditor with disablePaste toggle
   - `/problems/:id` - CodeEditor with disablePaste enabled

## Risks & Mitigations
- **Risk**: None expected. `indentWithTab` is a standard CodeMirror utility specifically designed for this purpose
- **Backward Compatibility**: This is a pure bug fix with no API changes
- **Performance**: Negligible impact - adding one key binding to existing keymap

## Success Criteria
- Tab key inserts indentation in the code editor
- Shift+Tab key reduces indentation
- Focus remains in the editor when using Tab/Shift+Tab
- All other editor functionality remains unchanged
- Paste prevention feature continues to work correctly
