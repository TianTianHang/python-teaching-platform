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
- **AND** the new code is automatically formatted before display
- **AND** cursor position is preserved if possible

#### Scenario: Ref access with formatting
- **GIVEN** a parent component needs direct access to editor functionality
- **WHEN** the parent attaches a ref to CodeEditor
- **THEN** the ref provides access to the EditorView instance
- **AND** the ref provides a `formatCode()` method for programmatic formatting

### Requirement: TypeScript Type Safety
The CodeEditor component SHALL provide complete TypeScript type definitions including formatting-related props and methods.

#### Scenario: Props interface with formatting options
- **GIVEN** a developer uses the CodeEditor component
- **WHEN** they import the component
- **THEN** TypeScript provides autocomplete for all props including `formatOnLoad?: boolean` and `formatOptions?: PrettierOptions`
- **AND** the ref type includes the `formatCode(): Promise<void>` method
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

### Requirement: Code Auto-Formatting on Load
The CodeEditor component SHALL automatically format Python code when initial code is loaded from the `code` prop.

#### Scenario: Format code template on initial load
- **GIVEN** the CodeEditor receives a `code` prop with malformed indentation
- **WHEN** the component initializes and creates the EditorState
- **THEN** the code is formatted using Prettier before being displayed
- **AND** the formatted code follows PEP 8 style guidelines

#### Scenario: Skip formatting for invalid Python code
- **GIVEN** the CodeEditor receives a `code` prop with syntax errors
- **WHEN** Prettier attempts to format the code
- **THEN** formatting is gracefully skipped
- **AND** the original code is displayed without modification

### Requirement: Manual Code Formatting
The CodeEditor component SHALL provide a way for users to manually trigger code formatting.

#### Scenario: Format code via keyboard shortcut
- **GIVEN** the user is editing code in the CodeEditor
- **WHEN** the user presses Shift+Alt+F (or platform equivalent)
- **THEN** the current code is formatted using Prettier
- **AND** the cursor position is preserved or appropriately adjusted

#### Scenario: Format code via API
- **GIVEN** a parent component has access to the CodeEditor ref
- **WHEN** the parent calls the `formatCode()` method
- **THEN** the current code is formatted
- **AND** the formatted code replaces the current editor content

### Requirement: Formatting Error Handling
The CodeEditor component SHALL handle formatting errors gracefully without breaking the editor.

#### Scenario: Handle Prettier parser errors
- **GIVEN** the code contains syntax that Prettier cannot parse
- **WHEN** formatting is attempted
- **THEN** the error is caught silently
- **AND** the original code remains in the editor
- **AND** no error is shown to the user

#### Scenario: Handle async formatting failure
- **GIVEN** Prettier formatting is running asynchronously
- **WHEN** an unexpected error occurs during formatting
- **THEN** the error is caught and logged
- **AND** the editor remains functional with original code

