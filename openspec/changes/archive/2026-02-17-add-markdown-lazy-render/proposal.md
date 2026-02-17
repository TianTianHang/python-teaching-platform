# Add Markdown Lazy Rendering for Performance Optimization

## Summary

Add lazy rendering capability to Markdown components to improve initial page load performance. Heavy components (JupyterLite code blocks, foldable blocks) will only render when they enter the viewport, reducing Time to Interactive (TTI) and improving perceived performance.

## Motivation

### Current State

The `MarkdownRenderer` component currently renders all markdown content immediately, including:
- **JupyterLiteCodeBlock**: Heavy iframe-based Python execution environments
- **FoldableBlock**: Collapsible content sections (even when collapsed)
- Regular markdown content

For pages with 1-3 screens of content containing multiple code blocks or foldable sections, this causes:
- Slow initial page load (all components render simultaneously)
- Blocked main thread during iframe initialization
- Unnecessary rendering of off-screen content

### Benefits

1. **Faster First Content Paint**: Only visible content renders initially
2. **Improved TTI**: Heavy components load asynchronously when needed
3. **Better Scroll Performance**: Content loads progressively as user scrolls
4. **Reduced Memory Usage**: Off-screen iframes don't initialize until needed
5. **No Breaking Changes**: Existing markdown syntax and behavior preserved

### User Impact

- **Students**: Chapter pages load faster, especially those with multiple code examples
- **Instructors**: Content with many foldable hints/answers doesn't slow down page load
- **Exam Pages**: Questions with code blocks render more quickly

## Proposed Changes

### 1. Create LazyRender Component

Create a new `LazyRender` component (`app/components/LazyRender.tsx`) that:
- Uses Intersection Observer API for viewport detection
- Defers rendering children until element enters viewport
- Provides fallback content placeholder
- Configurable root margin for pre-loading
- SSR compatible (no hydration mismatches)

**API**:
```tsx
<LazyRender fallback={<Skeleton />} rootMargin="100px">
  <HeavyComponent />
</LazyRender>
```

### 2. Wrap Heavy Components

Update `MarkdownRenderer.tsx` to wrap heavy components:

**JupyterLiteCodeBlock** (always lazy):
```tsx
<LazyRender fallback={<CodeBlockSkeleton />}>
  <JupyterLiteCodeBlock code={code} />
</LazyRender>
```

**FoldableBlock** (lazy when collapsed):
```tsx
<LazyRender fallback={null} skip={isExpanded}>
  <FoldableBlock type={type} title={title}>
    {children}
  </FoldableBlock>
</LazyRender>
```

### 3. Add Loading Placeholders

Create skeleton components for loading states:
- `CodeBlockSkeleton`: Placeholder for JupyterLite iframes
- Reuse MUI's Skeleton component for consistent styling

## Scope

### In Scope

- `MarkdownRenderer` component optimization
- `JupyterLiteCodeBlock` lazy loading
- `FoldableBlock` lazy loading (collapsed state only)
- New `LazyRender` utility component
- Skeleton loading placeholders

### Out of Scope

- Virtual scrolling (not needed for 1-3 screen content)
- Image lazy loading (browser native lazy loading handles this)
- Route-level code splitting (separate concern)
- Backend/API changes

## Design Decisions

### Why Intersection Observer?

- **Performance**: More efficient than scroll event listeners
- **Browser Support**: Widely supported (94%+), with polyfill available
- **Simple API**: Declarative usage, no complex state management

### Why Pre-load Margin (100px)?

- Loads content slightly before it becomes visible
- Eliminates perceived "flash" when scrolling
- Balances performance vs. resource usage

### Why Skip Lazy for Expanded Foldable Blocks?

- Expanded content is likely already visible
- Avoids hydration mismatches
- User explicitly chose to see this content

### SSR Strategy

- `LazyRender` always renders fallback on server
- Hydrates with correct client-side behavior
- No layout shift (placeholder reserves space)

## Success Criteria

1. First Content Paint (FCP) reduced by 30-50% for pages with 3+ code blocks
2. No visual regressions (layout shifts, flickering)
3. All existing markdown features work unchanged
4. No hydration errors in browser console
5. Progressive loading visible when scrolling

## Performance Targets

| Metric | Before | After Target |
|--------|--------|--------------|
| Time to First Byte | ~200ms | Unchanged |
| First Content Paint | ~800ms | ~400ms |
| Time to Interactive | ~1.5s | ~800ms |
| Cumulative Layout Shift | 0.05 | <0.1 |

## Dependencies

- React Router v7 SSR (already in use)
- MUI Skeleton component (already available)
- `@mui/material` (already installed)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Intersection Observer not supported | Include polyfill or add detection |
| Layout shift during load | Use proper placeholder sizing |
| Hydration mismatches | Consistent server/client rendering |
| Too aggressive pre-loading | Configurable root margin |
| Complex markdown rendering still slow | Future: virtual scrolling for very long content |

## Related Specifications

- Extends `markdown-foldable-blocks` specification
- Complements existing `MarkdownRenderer` component
- Future work: Consider `add-markdown-virtual-scroll` for very long documents (>10 screens)

## Alternatives Considered

### Virtual Scrolling (react-window/virtuoso)

**Rejected because**:
- Overkill for 1-3 screen content
- Complex to implement with dynamic markdown content
- Breaks native scroll behavior
- Harder to maintain

### Code Splitting per Markdown Block

**Rejected because**:
- Too many small chunks
- Network overhead
- Doesn't address iframe initialization cost

### RequestIdleCallback Scheduling

**Rejected because**:
- Not well supported across browsers
- Less predictable than Intersection Observer
- Doesn't account for viewport visibility

## Testing Strategy

### Manual Testing

1. Load chapter page with 3+ code blocks
2. Verify only first screen renders initially
3. Scroll down and observe progressive loading
4. Check browser console for hydration errors
5. Test on mobile and desktop

### Performance Testing

1. Measure FCP/T TI with Chrome DevTools
2. Compare before/after metrics
3. Test on slow 3G network throttling
4. Verify no regressions on fast connections

## Timeline Estimate

| Task | Time |
|------|------|
| Create LazyRender component | 1 hour |
| Create skeleton components | 30 min |
| Wrap JupyterLiteCodeBlock | 30 min |
| Update MarkdownRenderer | 30 min |
| Testing and refinement | 1 hour |
| **Total** | **3.5 hours** |
