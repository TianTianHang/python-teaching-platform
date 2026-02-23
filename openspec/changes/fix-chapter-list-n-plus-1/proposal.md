## Why

ChapterSerializer still contains N+1 query issues that impact performance when loading chapter lists. After fixing ProblemSerializer, we need to optimize ChapterSerializer methods that:
1. Query user progress data for each chapter
2. Access enrollment information for user permissions
3. Retrieve unlock condition and prerequisite data
4. Fetch course information for prerequisite chapters

## What Changes

- Fix N+1 query in ChapterSerializer.get_status() by using pre-fetched user_progress data
- Optimize ChapterSerializer.get_is_locked() by leveraging pre-fetched enrollment data
- Improve ChapterSerializer.get_prerequisite_progress() using pre-fetched progress records
- Enhance ChapterUnlockConditionSerializer to avoid course title N+1 queries
- Update ChapterViewSet to prefetch required relationship data

## Capabilities

### New Capabilities
- `chapter-list-optimization`: Optimize chapter list API by eliminating N+1 queries in ChapterSerializer
- `chapter-unlock-status-optimization`: Improve unlock condition checking performance

### Modified Capabilities
- `chapter-status-retrieval`: Optimize user progress retrieval from O(n) to O(1)

## Impact

- **Backend**: courses/serializers.py, courses/views.py ChapterViewSet
- **API**: `/api/chapters/` list endpoint performance improvement
- **Database**: Reduced query count from ~n+1 to constant queries per chapter list request
- **Frontend**: Chapter lists will load faster, especially for courses with many chapters
- **User Experience**: Reduced latency when navigating course content