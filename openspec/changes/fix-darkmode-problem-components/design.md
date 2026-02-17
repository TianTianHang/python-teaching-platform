# Design: Fix Dark Mode Display Issues

## Technical Approach

### Problem Analysis

The issue stems from using hardcoded MUI color palette values that reference specific numeric shades:
- `grey.50` - A very light gray (#FAFAFA in light mode)
- `grey.100` - A light gray (#F5F5F5 in light mode)

These values do not automatically adapt to dark mode because they reference absolute color values rather than semantic tokens.

### Solution Strategy

MUI provides semantic color tokens that automatically adapt to theme mode:

| Semantic Token | Light Mode | Dark Mode |
|----------------|------------|-----------|
| `background.default` | ~#fff | ~#121212 |
| `background.paper` | ~#fff | ~#1e1e1e |

For content containers like Paper components, `background.paper` is the appropriate choice as it provides:
- Proper contrast in both light and dark modes
- Consistent elevation hierarchy
- Automatic theme adaptation

### Implementation Pattern

**Before (hardcoded):**
```tsx
<Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
```

**After (semantic):**
```tsx
<Paper sx={{ p: 3, bgcolor: 'background.paper' }}>
```

### Related Components

After fixing the identified issues, we should verify no other components have similar problems. A quick grep search revealed that `CaseDetail.tsx` has the same pattern, so it's included in this fix.

## Considerations

1. **Backward Compatibility**: This change only affects styling, not functionality. No API changes.
2. **Accessibility**: Semantic tokens maintain WCAG contrast ratios in both modes.
3. **Future-proofing**: Using semantic tokens ensures compatibility with any future theme changes.
