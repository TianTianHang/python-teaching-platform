# Implementation Tasks

## Checklist

- [x] **Remove iframe animation states and logic**
  - Remove `showTransition` and `isInitialLoad` states
  - Remove opacity animations from iframe styles
  - Remove `fadeIn` keyframes (unused after changes)
  - Simplify the loading useEffect logic

- [x] **Add loading mask for JupyterLite content**
  - Add `isLoading` state to track when mask should show
  - Add CircularProgress to the container
  - Set mask to cover entire container area
  - Mask should be visible during initial load and theme switches

- [x] **Implement content-ready detection**
  - Current `onLoad` only detects iframe start loading
  - Need to detect when JupyterLite is actually ready
  - May need to handle iframe content events
  - Update mask hide logic based on content readiness

- [ ] **Test theme switching without white flash**
  - Test light → dark mode switch
  - Test dark → light mode switch
  - Verify no white flash during transitions
  - Verify loading mask appears and disappears correctly

- [ ] **Test initial load behavior**
  - Verify initial load shows loading mask
  - Verify mask disappears when JupyterLite is ready
  - Test on slow network conditions

## Order of Work

1. ~~First, add CSS styles to `app.css`~~ (Previous task - not needed for this approach)
2. ~~Then, add className to `JupyterLiteCodeBlock.tsx`~~ (Previous task - not needed for this approach)
3. Remove animation states and simplify logic
4. Add loading mask with proper timing
5. Test thoroughly

## Dependencies

- Need to understand JupyterLite initialization signals
- May need to experiment with iframe content ready detection

## Validation Criteria

- No white flash when switching themes
- Loading mask appears during content loading
- Loading mask disappears when content is ready
- Transitions are immediate but smooth
- Loading indicator provides good UX feedback

## Implementation Notes

The key insight is that the white flash comes from the iframe content itself, not the container. By removing the fade animation and adding a loading mask, we can completely hide the white background during loading.

### Iframe Content Ready Detection:
The current `onLoad` event fires when the iframe starts loading, but JupyterLite needs additional time to initialize:
```tsx
onLoad={() => {
  // iframe started loading
  // but JupyterLite needs more time to render
}}
```

We might need to:
1. Set a minimum loading time (e.g., 500ms)
2. Listen for JupyterLite-specific events
3. Use a heuristic (e.g., when DOM content is stable)
