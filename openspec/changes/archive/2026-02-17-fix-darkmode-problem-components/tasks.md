# Tasks: Fix Dark Mode Display Issues

## Implementation Tasks

### 1. Fix FillBlankProblemCmp.tsx background color
- [x] Update `bgcolor: 'grey.50'` to `bgcolor: 'background.paper'` in Paper component (line ~159)
- [x] Verify visual appearance in both light and dark modes
- [x] Test with sample fill-in-blank problem

### 2. Fix CaseDetail.tsx background colors
- [x] Update `bgcolor: 'grey.100'` to `bgcolor: 'background.paper'` for input Paper (line ~16)
- [x] Update `bgcolor: 'grey.100'` to `bgcolor: 'background.paper'` for output Paper (line ~36)
- [x] Verify visual appearance in both light and dark modes
- [x] Test with sample problem showing test cases

### 3. Validation
- [x] Manual testing: Switch between light/dark modes and verify correct appearance
- [x] Check that no other Problem components have similar hardcoded background colors
- [x] Verify text contrast remains adequate in both modes

## Task Ordering

Tasks 1 and 2 can be done in parallel. Task 3 depends on completion of 1 and 2.

## Definition of Done

- [x] Both components use `background.paper` semantic token
- [x] Visual appearance is consistent in both light and dark modes
- [x] No hardcoded gray background colors remain in Problem components
- [x] Manual testing confirms the fix works correctly
