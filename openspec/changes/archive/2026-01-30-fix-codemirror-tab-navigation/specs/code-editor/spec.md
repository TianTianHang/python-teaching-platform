# code-editor Spec Delta

## MODIFIED Requirements

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

## Rationale
The `indentWithTab` utility from `@codemirror/commands` provides proper Tab key handling that:
1. Inserts indentation for Python code following Python language conventions
2. Handles Shift+Tab for dedentation
3. Works with multi-line selections
4. Prevents browser's default Tab navigation behavior
5. Integrates cleanly with existing keymap configuration

This is a bug fix to restore expected editor behavior that was inadvertently broken.
