# Proposal: Fix Dark Mode Display Issues in Problem Components

## Summary

Fix hardcoded background colors in problem display components that cause visual issues in dark mode. The `FillBlankProblemCmp` and `CaseDetail` components currently use hardcoded gray background colors (`grey.50` and `grey.100`) that do not adapt to dark theme, resulting in poor visual contrast and user experience.

## Motivation

### Current Problem
- **FillBlankProblemCmp.tsx**: Uses `bgcolor: 'grey.50'` for the fill-in-blank input area
- **CaseDetail.tsx**: Uses `bgcolor: 'grey.100'` for test case input/output display areas

These hardcoded light gray colors appear as bright boxes on dark backgrounds when dark mode is enabled, creating:
- Poor visual contrast
- Inconsistent design language
- Accessibility concerns

### Expected Behavior
Background colors should automatically adapt to the current theme mode (light/dark) using MUI's semantic color tokens.

## Proposed Solution

Replace hardcoded gray background colors with MUI semantic color tokens:
- `bgcolor: 'background.paper'` - for card/container backgrounds
- Alternatively: Use `theme.palette.background.paper` for dynamic theming

### Affected Files
1. `frontend/web-student/app/components/Problem/FillBlankProblemCmp.tsx`
2. `frontend/web-student/app/components/Problem/CaseDetail.tsx`

### Changes Required
1. **FillBlankProblemCmp.tsx** (line 159):
   - Change: `bgcolor: 'grey.50'`
   - To: `bgcolor: 'background.paper'`

2. **CaseDetail.tsx** (lines 16, 36):
   - Change: `bgcolor: 'grey.100'`
   - To: `bgcolor: 'background.paper'`

## Impact Scope

- **Components**: FillBlankProblemCmp, CaseDetail
- **Users**: All users viewing fill-in-blank problems or test case details in dark mode
- **Risk**: Low - simple CSS color replacement with semantic tokens

## Alternatives Considered

1. **Use `divider` token**: Could use for subtle separation, but `background.paper` provides better visual hierarchy for content containers
2. **Conditional theming**: `theme.palette.mode === 'dark' ? ... : ...` - unnecessary when semantic tokens exist
3. **Custom theme token**: Overkill for this simple fix

## Dependencies

None - this is a standalone styling fix.
