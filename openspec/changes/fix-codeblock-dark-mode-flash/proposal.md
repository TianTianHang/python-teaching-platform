# Fix JupyterLite Code Block Dark Mode Flash - Revised

## Summary

Fix the white flash issue during theme switching in JupyterLite code blocks by removing the iframe opacity animations and adding a loading mask that covers the entire container until JupyterLite content is fully loaded.

## Problem Analysis

**Current Behavior:**
- When switching from light to dark mode, there's a brief flash of white background
- This occurs specifically in `JupyterLiteCodeBlock` component which uses an iframe
- Regular markdown code blocks (`<pre><code>`) are not affected

**Root Cause - Two-Phase Issue:**

1. **Container Level**: The outer Box uses `bgcolor: 'background.paper'` which is a MUI `sx` property that only applies after React hydration
2. **Iframe Level**: More importantly, the iframe itself shows white content while loading. The current implementation has opacity animations that:
   - Fade out the old iframe (300ms)
   - During this fade, the new iframe loads with default white JupyterLite background
   - User sees white through the fading animation
   - Then new iframe appears with dark theme

## Proposed Solution

### Phase 1: Remove Iframe Animations
- Remove `showTransition` state and opacity-based animations
- Switch between iframes immediately without fade effect
- This prevents visual exposure of white background during transition

### Phase 2: Add Loading Mask
- Add a loading mask that covers the entire container area
- The mask shows during both:
  - Initial iframe loading
  - Theme switching (when new iframe content is loading)
- Hide the mask only when JupyterLite is fully rendered
- This completely prevents any white background from being visible

## Changes Required

1. **frontend/web-student/app/components/JupyterLiteCodeBlock.tsx**
   - Remove `showTransition`, `isInitialLoad` states
   - Remove opacity animations from iframe styles
   - Add `isLoading` state for loading mask
   - Simplify the loading logic

2. **Track Content Readiness**
   - Current `onLoad` only indicates iframe started loading
   - Need to detect when JupyterLite is actually ready
   - May require waiting for JupyterLite initialization signals

## Alternative Approaches Considered

1. **CSS-only Solution**: Set iframe background via CSS
   - Limitation: Can't control iframe internal content
   - JupyterLite has its own theme system

2. **Pre-render Dark Theme**: Always load dark theme iframe
   - Limitation: Theme switching would still require iframe reload
   - Doesn't solve the initial white flash

3. **Increase Animation Speed**: Make fade much faster
   - Limitation: Still exposes white background, just briefly
   - Doesn't eliminate the root cause

## Benefits of Proposed Solution

- **Eliminates White Flash**: Loading mask completely hides any white content
- **Faster Transitions**: No waiting for 300ms fade animation
- **Clear Feedback**: Loading indicator shows when content is loading
- **Simpler Logic**: Less complex state management

## Related Capabilities

- **code-editor**: JupyterLite integration
- **theme**: Dark mode support
- **ux-loading**: Loading states and indicators
