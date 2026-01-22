## Context
The platform uses CodeMirror as the code editor for Python code execution in:
- Algorithm problem solving (`AlgorithmProblemPage.tsx`)
- Playground environment (`_layout.playground.tsx`)

Current implementation relies on `@uiw/react-codemirror` v4.25.2, which provides React bindings but adds:
- Extra dependency layer
- ~20KB additional bundle size
- Limited access to low-level CodeMirror APIs
- Dependency on another package for theme management (`@uiw/codemirror-theme-vscode`)

### Stakeholders
- Frontend developers: Need maintainable, well-typed editor component
- Students: Expect responsive, feature-rich code editing experience
- Platform maintainers: Prefer minimal dependencies and direct access to editor APIs

## Goals / Non-Goals
- Goals:
  - Remove `@uiw/react-codemirror` and `@uiw/codemirror-theme-vscode` dependencies completely
  - Use native CodeMirror 6 extension system directly
  - Maintain backward-compatible component API (props interface unchanged)
  - Preserve all existing editor features (line numbers, syntax highlighting, Python support, etc.)
  - Enable future customization (custom keybindings, advanced extensions)
  - Ensure full SSR compatibility with React Router v7
  - Use `@codemirror/theme-one-dark` as the default theme

- Non-Goals:
  - Adding new editor features (defer to future proposals)
  - Preserving any @uiw-specific extensions or features
  - Custom theme implementation (One Dark is sufficient)

## Decisions

### Decision 1: Use @codemirror/view for React Integration
**Rationale**: `@codemirror/view` provides official CodeMirror 6 React bindings via `EditorView` from React. This is the recommended approach for React integration.

**Alternatives considered**:
- Continue with `@uiw/react-codemirror`: Rejected due to unnecessary abstraction
- Manual DOM manipulation: Rejected due to complexity and React SSR incompatibility
- Other wrappers (react-codemirror, etc.): Rejected due to maintenance status

### Decision 2: Use One Dark Theme
**Decision**: Use `@codemirror/theme-one-dark` as the default editor theme.

**Rationale**: One Dark provides a VS Code-like dark theme that is visually similar to the current `@uiw/codemirror-theme-vscode`. It is a well-maintained, official CodeMirror theme that eliminates the need for any @uiw theme dependencies.

**Alternatives considered**:
- Keep `@uiw/codemirror-theme-vscode`: Rejected to fully remove @uiw dependencies
- Custom theme implementation: Rejected as One Dark provides sufficient visual similarity

### Decision 3: Extension Configuration Pattern
**Rationale**: Use `Compartment` pattern for dynamic extension reconfiguration (future-proofing for features like toggling read-only mode).

**Alternatives considered**:
- Static extensions only: Rejected due to limited flexibility
- Full re-creation on prop change: Rejected due to performance impact

### Package Dependencies
Add:
- `@codemirror/view` (core view component)
- `@codemirror/state` (editor state management)
- `@codemirror/commands` (default keybindings)
- `@codemirror/language` (language support foundation)
- `@codemirror/autocomplete` (completion functionality)
- `@codemirror/lint` (linting support)
- `@codemirror/search` (search functionality)
- `@codemirror/theme-one-dark` (VS Code-like dark theme)
- `@codemirror/lang-python` (already installed, keep)

Remove:
- `@uiw/react-codemirror`
- `@uiw/codemirror-theme-vscode`

## Risks / Trade-offs

### Risk 1: SSR Compatibility (CRITICAL)
**Risk**: CodeMirror requires browser APIs (DOM, clipboard) which will fail during SSR with React Router v7.

**Mitigation**: MUST implement client-side only initialization:
- Use `useEffect` to defer editor creation until after hydration
- Add SSR guard checks (`useEffect` with empty dependency array)
- Ensure proper hydration to avoid mismatch errors
- Test with SSR disabled and enabled to verify compatibility

### Risk 2: Bundle Size Regression
**Risk**: Multiple CodeMirror packages may increase total bundle size
**Mitigation**: CodeMirror uses tree-shaking; measure bundle size before/after with `pnpm build`

### Risk 3: Breaking Changes During Implementation
**Risk**: Component behavior may subtly differ (focus management, cursor position, etc.)
**Mitigation**: Comprehensive manual testing of editor interactions; preserve existing prop interface

### Risk 4: Theme Inconsistency
**Risk**: New theme may look different from current VS Code Dark theme
**Mitigation**: Use `@codemirror/theme-one-dark` which is visually similar; adjust CSS if needed

## Migration Plan

### Phase 1: Preparation
1. Install new CodeMirror packages
2. Verify all existing editor features work with new packages
3. Create feature comparison checklist

### Phase 2: Implementation
1. Create new `CodeEditor` implementation using native CodeMirror
2. Set up proper React ref management for `EditorView`
3. Configure all extensions (Python language, line numbers, bracket matching, etc.)
4. Add proper cleanup (view destruction on unmount)

### Phase 3: Integration
1. Replace import in `AlgorithmProblemPage.tsx`
2. Replace import in `_layout.playground.tsx`
3. Verify component props interface compatibility
4. Test all editor interactions (typing, selection, paste, etc.)

### Phase 4: Cleanup
1. Remove `@uiw/react-codemirror` from `package.json`
2. Remove `@uiw/codemirror-theme-vscode` from `package.json`
3. Run `pnpm install` to clean up
4. Build and verify no import errors

### Rollback
If critical issues arise:
1. Revert `CodeEditor.tsx` to previous implementation
2. Restore removed dependencies in `package.json`
3. Document issues for future retry

## Resolved Decisions

### Theme Selection
**Decision confirmed**: Use `@codemirror/theme-one-dark` as the default editor theme.

### @uiw Extensions
**Decision confirmed**: Do NOT preserve any @uiw-specific extensions or features. Use only native CodeMirror packages.

### SSR Compatibility
**Decision confirmed**: Full SSR compatibility with React Router v7 is REQUIRED. Implementation must:
- Initialize editor only on client-side using `useEffect`
- Handle hydration correctly to avoid mismatch errors
- Test with both SSR enabled and disabled
