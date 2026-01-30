# code-editor Specification

## Purpose
TBD - created by archiving change refactor-codemirror-to-native. Update Purpose after archive.
## Requirements
### Requirement: Python Code Editor Component
The frontend SHALL provide a CodeMirror-based code editor component for Python code editing with proper keyboard navigation handling.

#### Scenario: Handle Tab key for indentation
- **GIVEN** a user is editing code in the CodeEditor component
- **WHEN** the user presses the Tab key
- **THEN** the editor inserts indentation (spaces or tab character)
- **AND** the focus remains within the editor
- **AND** the browser's default Tab navigation is prevented

#### Scenario: Handle Shift+Tab key for dedentation
- **GIVEN** a user is editing code in the CodeEditor component
- **WHEN** the user presses Shift+Tab keys
- **THEN** the editor reduces indentation of the current line
- **AND** the focus remains within the editor
- **AND** the browser's default reverse Tab navigation is prevented

#### Scenario: Handle Tab key with multi-line selection
- **GIVEN** a user has multiple lines of code selected in the editor
- **WHEN** the user presses the Tab key
- **THEN** all selected lines are indented equally
- **AND** the selection is preserved or appropriately adjusted

#### Scenario: Handle Shift+Tab key with multi-line selection
- **GIVEN** a user has multiple lines of code selected in the editor
- **WHEN** the user presses Shift+Tab keys
- **THEN** all selected lines are dedented equally
- **AND** the selection is preserved or appropriately adjusted

#### Scenario: Tab key behavior with paste prevention enabled
- **GIVEN** the CodeEditor component has `disablePaste={true}` enabled
- **WHEN** the user presses Tab or Shift+Tab keys
- **THEN** the indentation/dedentation works normally
- **AND** paste prevention remains active for paste operations only

### Requirement: Editor Extensions Configuration
The CodeEditor component SHALL support configurable CodeMirror extensions for Python development.

#### Scenario: Python language support
- **GIVEN** the CodeEditor component is initialized
- **WHEN** Python language extension is configured
- **THEN** Python syntax highlighting is active
- **AND** Python-specific indentation rules apply
- **AND** Python keywords are properly highlighted

#### Scenario: Basic editor features
- **GIVEN** the CodeEditor component renders
- **THEN** line numbers are displayed in the gutter
- **AND** active line is highlighted
- **AND** selection matches are highlighted
- **AND** brackets are matched automatically
- **AND** closing brackets are inserted automatically
- **AND** code folding is available in the gutter

#### Scenario: Dark theme
- **GIVEN** the CodeEditor component renders
- **WHEN** the One Dark theme (or VS Code Dark equivalent) is applied
- **THEN** the editor uses dark color scheme
- **AND** syntax highlighting colors match the theme
- **AND** the editor appearance is consistent with platform design

### Requirement: React Integration
The CodeEditor component SHALL integrate properly with React component lifecycle and state management.

#### Scenario: Controlled component behavior
- **GIVEN** the CodeEditor receives a `code` prop
- **WHEN** the parent component updates the `code` prop
- **THEN** the editor content updates to reflect the new value
- **AND** cursor position is preserved if possible

#### Scenario: Unmount cleanup
- **GIVEN** the CodeEditor component is mounted
- **WHEN** the component unmounts
- **THEN** the CodeMirror EditorView is properly destroyed
- **AND** no memory leaks occur
- **AND** event listeners are removed

#### Scenario: Ref access (optional)
- **GIVEN** a parent component needs direct access to editor functionality
- **WHEN** the parent attaches a ref to CodeEditor
- **THEN** the ref provides access to the EditorView instance
- **AND** the parent can call editor methods directly (if needed in future)

### Requirement: TypeScript Type Safety
The CodeEditor component SHALL provide complete TypeScript type definitions including the new disablePaste prop.

#### Scenario: Props interface with disablePaste
- **GIVEN** a developer uses the CodeEditor component
- **WHEN** they import the component
- **THEN** TypeScript provides autocomplete for all props including `disablePaste?: boolean`
- **AND** props are properly typed (`code`, `onChange`, `maxHeight`, `minHeight`, `readOnly`, `disablePaste`)
- **AND** type errors are caught at compile time

### Requirement: Paste Prevention
The CodeEditor component SHALL support preventing paste operations when explicitly enabled.

#### Scenario: Prevent paste when disablePaste is true
- **GIVEN** the CodeEditor component receives `disablePaste={true}` prop
- **WHEN** the user attempts to paste content using keyboard shortcut (Ctrl+V / Cmd+V) or context menu
- **THEN** the paste operation is blocked
- **AND** the editor content remains unchanged
- **AND** a user-friendly toast/notification message informs that pasting is disabled

#### Scenario: Allow paste when disablePaste is false or not provided
- **GIVEN** the CodeEditor component receives `disablePaste={false}` or no disablePaste prop
- **WHEN** the user attempts to paste content
- **THEN** the paste operation succeeds
- **AND** the pasted content is inserted into the editor

#### Scenario: Paste prevention with other features
- **GIVEN** the CodeEditor component has `disablePaste={true}` enabled
- **WHEN** the user performs other editing operations (typing, backspace, cut, copy)
- **THEN** those operations work normally
- **AND** only paste operations are blocked

