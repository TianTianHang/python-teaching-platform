## ADDED Requirements

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

## MODIFIED Requirements

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
