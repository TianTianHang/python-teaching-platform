# Cache Invalidation Best Practices

This guide explains how to properly invalidate cache in the Python Teaching Platform, especially for user-isolated ViewSets.

## Overview

The platform uses `CacheInvalidator` class to provide a unified API for cache invalidation. When invalidating cache, it's important to consider whether the cache is **user-isolated** or **global**.

## User-Isolated vs Global Cache

### User-Isolated Cache
User-isolated cache means that each user has their own cached data. This is typically used when:
- The ViewSet's `get_queryset()` filters by `request.user`
- Examples: `EnrollmentViewSet`, `ChapterProgressViewSet`, `ProblemProgressViewSet`

**Cache key format:** `{prefix}:{view_name}:user_id={user_id}:...`

### Global Cache
Global cache is shared across all users. This is used for:
- Course catalogs, chapter listings, etc.
- Data that's the same for all users

**Cache key format:** `{prefix}:{view_name}:...` (no user_id)

## When to Pass `user_id` Parameter

### ✅ PASS `user_id` when:
- The ViewSet uses user-isolated caching (filters by user in `get_queryset()`)
- You want to invalidate cache for a **specific user only**
- The cache key includes `user_id`

**Example:**
```python
from common.utils.cache import CacheInvalidator

# Invalidate enrollment cache for a specific user
CacheInvalidator.invalidate_viewset_list(
    prefix=EnrollmentViewSet.cache_prefix,
    view_name=EnrollmentViewSet.__name__,
    user_id=user.id
)
```

### ❌ DON'T PASS `user_id` when:
- The ViewSet uses global caching (no user filtering)
- You want to invalidate cache for **all users**
- The cache key does NOT include `user_id`

**Example:**
```python
# Invalidate course catalog cache for all users
CacheInvalidator.invalidate_viewset_list(
    prefix=CourseViewSet.cache_prefix,
    view_name=CourseViewSet.__name__
)
```

## Common Scenarios

### 1. Enrollment Creation

When a user enrolls in a course, invalidate **that user's** enrollment list cache:

```python
@receiver(post_save, sender=Enrollment)
def invalidate_enrollment_cache_on_create(sender, instance, created, **kwargs):
    if created:
        # Only invalidate the enrolling user's cache
        CacheInvalidator.invalidate_viewset_list(
            prefix=EnrollmentViewSet.cache_prefix,
            view_name=EnrollmentViewSet.__name__,
            user_id=instance.user.id  # ✓ Correct: user-isolated
        )
```

### 2. Progress Updates

When a user's progress changes, invalidate **that user's** progress cache:

```python
# Invalidate specific user's chapter progress cache
CacheInvalidator.invalidate_viewset_list(
    prefix="courses",
    view_name="ChapterProgressViewSet",
    parent_pks={"course_pk": course_id},
    user_id=user.id  # ✓ Correct: user-isolated
)
```

### 3. Content Updates

When course content is updated (not user-specific), invalidate **all users'** cache:

```python
# Invalidate chapter cache for all users
CacheInvalidator.invalidate_viewset_list(
    prefix=ChapterViewSet.cache_prefix,
    view_name=ChapterViewSet.__name__,
    parent_pks={"course_pk": course_id}
    # ✗ No user_id: affects all users
)
```

## Signal Handler Guidelines

When writing signal handlers for cache invalidation:

1. **Identify if the model is user-specific**
   - Does it have a `user` field?
   - Does it have an `enrollment.user` relation?
   
2. **Pass `user_id` for user-specific models**
   ```python
   # For models with direct user reference
   user_id = instance.user.id
   
   # For models with enrollment reference
   user_id = instance.enrollment.user.id
   ```

3. **Omit `user_id` for global models**
   ```python
   # For models like Course, Chapter, Problem
   # Don't pass user_id - these affect all users
   ```

## Checking ViewSet Cache Type

To determine if a ViewSet uses user-isolated cache, check its `get_queryset()` method:

```python
# User-isolated example
class EnrollmentViewSet:
    def get_queryset(self):
        # Filters by user → user-isolated cache
        return Enrollment.objects.filter(user=self.request.user)

# Global cache example
class CourseViewSet:
    def get_queryset(self):
        # No user filtering → global cache
        return Course.objects.all()
```

## API Reference

### `invalidate_viewset_list()`

```python
CacheInvalidator.invalidate_viewset_list(
    prefix: str,
    view_name: str,
    parent_pks: Optional[Dict[str, int]] = None,
    user_id: Optional[int] = None
) -> bool
```

**Parameters:**
- `prefix`: Cache prefix (e.g., "api", "courses")
- `view_name`: ViewSet class name (e.g., "EnrollmentViewSet")
- `parent_pks`: Parent resource IDs (optional)
- `user_id`: User ID for user-isolated cache (optional)

**Returns:** `True` if successful, `False` otherwise

### `invalidate_viewset()`

```python
CacheInvalidator.invalidate_viewset(
    prefix: str,
    view_name: str,
    pk: int,
    parent_pks: Optional[Dict[str, int]] = None,
    user_id: Optional[int] = None
) -> bool
```

**Parameters:** Same as above, plus:
- `pk`: Primary key of the object to invalidate

## Troubleshooting

### Problem: Cache not being invalidated after data changes

**Possible Cause:** Not passing `user_id` for user-isolated ViewSet

**Solution:**
1. Check if the ViewSet filters by user
2. If yes, pass `user_id` parameter
3. Verify the pattern matches the actual cache key

### Problem: Other users' cache being cleared incorrectly

**Possible Cause:** Passing `user_id` when you shouldn't, or not passing it when you should

**Solution:**
- Check the ViewSet's `get_queryset()` method
- If it filters by user, pass `user_id`
- If it doesn't filter by user, don't pass `user_id`

## Testing

When testing cache invalidation:

```python
from unittest.mock import patch
from common.utils.cache import CacheInvalidator

def test_user_isolated_cache_invalidation():
    with patch('common.utils.cache.delete_cache_pattern') as mock_delete:
        # Invalidate user-specific cache
        CacheInvalidator.invalidate_viewset_list(
            prefix="api",
            view_name="EnrollmentViewSet",
            user_id=user.id
        )
        
        # Verify the pattern includes user_id
        expected_pattern = "api:EnrollmentViewSet:user_id=123:*"
        mock_delete.assert_called_once_with(expected_pattern)
```

## Related Documentation

- [Cache Performance Logging Guide](./cache-performance-logging.md)
- [Cache Implementation](../common/utils/cache.py)
- [Cache Invalidation Tests](../courses/tests/test_cache_invalidator.py)
