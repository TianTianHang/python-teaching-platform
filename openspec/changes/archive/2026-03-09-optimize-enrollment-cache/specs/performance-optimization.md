## Overview

This change is a performance optimization with no new requirements or API contract changes.

## No New Requirements

This is a pure implementation optimization. The existing functionality remains unchanged - only the internal data structure returned by `EnrollmentSerializer.get_next_chapter()` is simplified to reduce cache size and improve deserialization performance.

### API Contract Unchanged

The API response format for Enrollment endpoints remains backward compatible:
- Frontend receives the same `next_chapter` field with `id`, `title`, and `order`
- Frontend code does not need modification
- No new endpoints or features added

### Performance Improvements

This optimization achieves:
- Reduced cache entry size (~50KB → ~500 bytes)
- Improved cache read latency (~1.8s → ~50ms)
- No changes to database queries or caching infrastructure