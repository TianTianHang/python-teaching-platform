## 1. Implementation

- [x] Add `disablePaste?: boolean` prop to CodeEditor TypeScript interface
- [x] Create a compartment for paste prevention to allow dynamic reconfiguration
- [x] Implement paste event interception using CodeMirror's `EditorView.domEventHandlers` extension
- [x] Block Ctrl+V / Cmd+V keyboard shortcuts when `disablePaste={true}`
- [x] Block context menu paste operations when `disablePaste={true}`
- [x] Integrate toast/notification system for user feedback when paste is blocked
- [x] Ensure paste prevention doesn't interfere with other editor operations (typing, cut, copy)
- [x] Update the component to dynamically reconfigure paste prevention when the prop changes
- [x] Test the feature in both enabled and disabled states

## 2. Validation

- [x] Manual test: Verify paste works when `disablePaste` is false or not provided
- [x] Manual test: Verify paste is blocked when `disablePaste={true}`
- [x] Manual test: Verify paste blocking works with keyboard shortcut (Ctrl+V / Cmd+V)
- [x] Manual test: Verify paste blocking works with context menu (right-click)
- [x] Manual test: Verify notification appears when paste is blocked
- [x] Manual test: Verify other editing operations (typing, backspace, cut, copy) work normally when paste is disabled
- [x] Verify TypeScript type checking passes with new prop
- [x] Test dynamic reconfiguration: toggle `disablePaste` prop and verify behavior changes
