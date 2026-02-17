# JupyterLite Code Block Dark Mode Flash Fix - Technical Design (Revised)

## Problem Analysis

The white flash occurs because:

1. **Iframe Content White Background**: When JupyterLite loads, it shows white background before applying the theme
2. **Fade Animation Exposure**: The current implementation fades out the old iframe while the new one loads, exposing the white background through the animation
3. **No Loading Feedback**: Users don't know content is loading, so the white flash is jarring

## Solution Architecture

### 1. Remove Animations
- Remove all opacity-based fade animations
- Switch between iframes immediately
- This eliminates the visual exposure of white background during transition

### 2. Loading Mask
- Add a full-coverage loading mask
- Shows during initial load and theme switches
- Hidden only when JupyterLite is fully ready
- Provides visual feedback during loading

### 3. Content Readiness Detection
Current `onLoad` is insufficient - we need to detect when JupyterLite is actually ready to be shown.

## Implementation Details

### File: `frontend/web-student/app/components/JupyterLiteCodeBlock.tsx`

#### Simplified State Management
```tsx
// Remove these states:
// const [showTransition, setShowTransition] = useState(false);
// const [isInitialLoad, setIsInitialLoad] = useState(true);

// Keep these:
const [pendingSrc, setPendingSrc] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(true);
```

#### Simplified useEffect Logic
```tsx
useEffect(() => {
  if (currentSrc !== iframeSrc) {
    // Theme switching
    setIsLoading(true);
    setPendingSrc(iframeSrc);
  }
}, [iframeSrc]);
```

#### Loading Mask Implementation
```tsx
// Add loading mask that covers entire container
{isLoading && (
  <Box
    sx={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      bgcolor: 'background.paper',
      zIndex: 100,
    }}
  >
    <CircularProgress />
  </Box>
)}
```

#### Immediate Iframe Switching
```tsx
// Remove opacity animations
<iframe
  src={currentSrc}
  style={{
    width: '100%',
    height: '100%',
    border: 'none',
    position: 'absolute',
    top: 0,
    left: 0,
  }}
  onLoad={handleIframeLoad}
/>
```

### Content Ready Detection Strategies

#### Strategy 1: Minimum Loading Time
```tsx
const handleIframeLoad = () => {
  // Set minimum loading time to ensure JupyterLite is ready
  setTimeout(() => {
    setIsLoading(false);
    if (pendingSrc) {
      setCurrentSrc(pendingSrc);
      setPendingSrc(null);
    }
  }, 500); // Adjust based on testing
};
```

#### Strategy 2: Event Listeners (More Complex)
```tsx
// Inside iframe
const iframe = iframeRef.current;
iframe?.contentWindow?.addEventListener('jupyterReady', () => {
  setIsLoading(false);
});
```

## Loading State Flow

1. **Initial Load**
   - `isLoading = true`
   - Loading mask shows
   - iframe loads
   - After minimum time, mask hides

2. **Theme Switch**
   - User changes theme
   - `isLoading = true`
   - Loading mask shows
   - New iframe loads
   - After minimum time, mask hides
   - `pendingSrc` nullifies

## Why This Works

1. **No White Flash**: Loading mask completely hides iframe content during loading
2. **Immediate Feedback**: Loading indicator shows immediately when content is loading
3. **Simpler Logic**: No complex animation timing or state management
4. **Better Performance**: Less DOM manipulation without opacity transitions

## Trade-offs

**Pros:**
- Eliminates white flash completely
- Provides clear loading feedback
- Faster theme transitions
- Simpler code structure

**Cons:**
- Loading mask might feel like an extra step
- Need to tune minimum loading time
- Might mask slow performance issues

## Testing Strategy

1. **Theme Switching**: Test light ↔ dark transitions multiple times
2. **Network Conditions**: Test on slow 3G network
3. **Multiple Blocks**: Test page with multiple JupyterLite blocks
4. **Performance**: Measure loading times
5. **User Experience**: Check if loading mask feels natural

## Alternative Implementation

If the minimum loading time approach is not precise enough, we could:

1. **Poll Iframe Content**: Check if JupyterLite elements exist
2. **Listen for Notebook Ready**: Use JupyterLab events if available
3. **Intersection Observer**: Use when iframe is visible

However, the minimum loading time is likely sufficient since:
- JupyterLite initialization is fairly consistent
- 500ms provides a good buffer
- Loading mask improves UX even if content is ready sooner
