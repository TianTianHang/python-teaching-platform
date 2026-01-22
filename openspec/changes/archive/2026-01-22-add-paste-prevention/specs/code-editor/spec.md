## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: TypeScript Type Safety
The CodeEditor component SHALL provide complete TypeScript type definitions including the new disablePaste prop.

#### Scenario: Props interface with disablePaste
- **GIVEN** a developer uses the CodeEditor component
- **WHEN** they import the component
- **THEN** TypeScript provides autocomplete for all props including `disablePaste?: boolean`
- **AND** props are properly typed (`code`, `onChange`, `maxHeight`, `minHeight`, `readOnly`, `disablePaste`)
- **AND** type errors are caught at compile time
