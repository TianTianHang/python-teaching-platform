# Design: Chapter Unlock Conditions

## Overview
This document describes the technical design for implementing chapter unlock conditions (prerequisites) in the Python teaching platform.

## Architecture

### Model Design

#### ChapterUnlockCondition Model
```python
class ChapterUnlockCondition(models.Model):
    """
    章节解锁条件模型
    支持前置章节解锁、时间解锁等条件
    """
    chapter = models.OneToOneField(
        Chapter,
        on_delete=models.CASCADE,
        related_name='unlock_condition',
        verbose_name="解锁条件关联的章节"
    )

    # 前置章节解锁条件
    prerequisite_chapters = models.ManyToManyField(
        Chapter,
        related_name='dependent_chapters',
        blank=True,
        verbose_name="前置章节",
        help_text="必须完成这些前置章节才能解锁当前章节"
    )

    # 解锁日期条件
    unlock_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="解锁日期",
        help_text="在此日期之前章节将被锁定"
    )

    # 解锁条件类型（预留扩展）
    UNLOCK_TYPES = (
        ('prerequisite', '前置章节'),
        ('date', '时间解锁'),
        ('all', '全部条件'),
    )
    unlock_condition_type = models.CharField(
        max_length=20,
        choices=UNLOCK_TYPES,
        default='all',
        verbose_name="解锁条件类型"
    )

    class Meta:
        verbose_name = "章节解锁条件"
        verbose_name_plural = "章节解锁条件"

    # 最大依赖链深度限制
    MAX_DEPENDENCY_DEPTH = 5

    def __str__(self):
        return f"{self.chapter.title} - 解锁条件"

    def clean(self):
        """
        验证解锁条件的有效性
        1. 防止自依赖（章节依赖自己）
        2. 防止循环依赖（A依赖B，B依赖A）
        3. 限制依赖链深度（防止过深的依赖链）
        """
        from django.core.exceptions import ValidationError

        super().clean()

        # 1. 检查自依赖
        if self.chapter in self.prerequisite_chapters.all():
            raise ValidationError({
                'prerequisite_chapters': '章节不能将自身作为前置章节。'
            })

        # 2. 检查循环依赖
        if self._has_circular_dependency():
            raise ValidationError({
                'prerequisite_chapters': '检测到循环依赖，请检查前置章节关系。'
            })

        # 3. 检查依赖链深度
        depth = self._calculate_dependency_depth()
        if depth > self.MAX_DEPENDENCY_DEPTH:
            raise ValidationError({
                'prerequisite_chapters': f'依赖链过深（当前深度：{depth}，最大深度：{self.MAX_DEPENDENCY_DEPTH}），请简化章节关系。'
            })

    def _has_circular_dependency(self, visited=None):
        """
        使用 DFS 检测循环依赖
        """
        if visited is None:
            visited = set()

        if self.chapter.id in visited:
            return True

        visited.add(self.chapter.id)

        for prereq in self.prerequisite_chapters.all():
            if hasattr(prereq, 'unlock_condition'):
                prereq_condition = prereq.unlock_condition
                # 递归检查每个前置章节的依赖
                if prereq_condition._has_circular_dependency(visited.copy()):
                    return True

        return False

    def _calculate_dependency_depth(self, visited=None):
        """
        计算依赖链的最大深度
        """
        if visited is None:
            visited = set()

        # 防止无限递归（虽然有 circular check，但作为保险）
        if self.chapter.id in visited:
            return 0

        visited.add(self.chapter.id)

        if not self.prerequisite_chapters.exists():
            return 1

        max_depth = 0
        for prereq in self.prerequisite_chapters.all():
            if hasattr(prereq, 'unlock_condition'):
                prereq_depth = prereq.unlock_condition._calculate_dependency_depth(visited.copy())
                max_depth = max(max_depth, prereq_depth)

        return 1 + max_depth

    def save(self, *args, **kwargs):
        """
        保存前调用 clean() 进行验证
        """
        self.full_clean()
        super().save(*args, **kwargs)
```

### Service Layer

#### ChapterUnlockService
```python
class ChapterUnlockService:
    """
    章节解锁服务
    处理章节解锁状态的检查和查询
    """

    @staticmethod
    def is_unlocked(chapter: Chapter, enrollment: Enrollment) -> bool:
        """
        检查章节对指定用户是否已解锁

        规则：
        1. 如果没有解锁条件，则已解锁
        2. 根据 unlock_condition_type 执行相应检查：
           - 'prerequisite': 只检查前置章节
           - 'date': 只检查解锁日期
           - 'all': 同时检查前置章节和解锁日期（默认）
        """
        if not hasattr(chapter, 'unlock_condition'):
            return True

        condition = chapter.unlock_condition
        unlock_type = condition.unlock_condition_type

        # 检查前置章节（仅当类型为 prerequisite 或 all）
        if unlock_type in ('prerequisite', 'all') and condition.prerequisite_chapters.exists():
            prerequisite_ids = condition.prerequisite_chapters.values_list('id', flat=True)
            completed_count = ChapterProgress.objects.filter(
                enrollment=enrollment,
                chapter_id__in=prerequisite_ids,
                completed=True
            ).count()

            if completed_count != prerequisite_ids.count():
                return False

        # 检查解锁日期（仅当类型为 date 或 all）
        if unlock_type in ('date', 'all') and condition.unlock_date:
            from django.utils import timezone
            if timezone.now() < condition.unlock_date:
                return False

        return True

    @staticmethod
    def get_unlock_status(chapter: Chapter, enrollment: Enrollment) -> dict:
        """
        获取章节解锁状态详情
        返回：是否解锁、缺少哪些前置章节、解锁倒计时等
        """
        # Implementation details...
```

### API Changes

#### ChapterViewSet Modifications
```python
class ChapterViewSet(CacheListMixin, CacheRetrieveMixin, viewsets.ModelViewSet):
    # ... existing code ...

    def get_queryset(self):
        queryset = Chapter.objects.select_related('course').prefetch_related(
            'unlock_condition__prerequisite_chapters'
        ).all()

        # 学生用户过滤已锁定的章节（数据库层面过滤，避免内存加载）
        if not self._is_instructor_or_admin():
            enrollment = self._get_enrollment()
            if enrollment:
                queryset = self._filter_locked_chapters(queryset, enrollment)

        return queryset

    def _filter_locked_chapters(self, queryset, enrollment):
        """
        数据库层面过滤已锁定章节，避免加载到内存

        策略：
        1. 获取学生已完成的章节 ID 列表
        2. 排除以下章节：
           - 有解锁条件且前置章节未完成
           - 有解锁条件且未到解锁日期
        """
        from django.db.models import Q, Exists, OuterRef
        from django.utils import timezone

        # 获取学生已完成的章节 ID
        completed_chapter_ids = ChapterProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).values_list('chapter_id', flat=True)

        # 构建 Annotation 标记每个章节是否已解锁
        queryset = queryset.annotate(
            # 检查是否有前置章节未完成
            has_unmet_prerequisites=Exists(
                ChapterUnlockCondition.objects.filter(
                    chapter=OuterRef('pk')
                ).filter(
                    Q(prerequisite_chapters__isnull=False) &
                    ~Q(prerequisite_chapters__id__in=completed_chapter_ids)
                )
            ),
            # 检查是否未到解锁日期
            is_before_unlock_date=Exists(
                ChapterUnlockCondition.objects.filter(
                    chapter=OuterRef('pk'),
                    unlock_date__gt=timezone.now()
                )
            )
        )

        # 根据 unlock_condition_type 构建过滤条件
        locked_conditions = Q(has_unmet_prerequisites=True) | Q(is_before_unlock_date=True)

        # 排除锁定章节
        queryset = queryset.exclude(locked_conditions)

        return queryset

    @action(detail=True, methods=['get'])
    def unlock_status(self, request, pk=None):
        """
        获取章节解锁状态详情
        返回前置章节完成进度、解锁时间等信息
        """
        # Implementation...
```

#### Serializer Updates
```python
class ChapterUnlockConditionSerializer(serializers.ModelSerializer):
    prerequisite_chapters = ChapterSerializer(many=True, read_only=True)
    prerequisite_chapter_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = ChapterUnlockCondition
        fields = [
            'id', 'chapter', 'prerequisite_chapters',
            'prerequisite_chapter_ids', 'unlock_date', 'unlock_condition_type'
        ]

class ChapterSerializer(serializers.ModelSerializer):
    # ... existing fields ...
    unlock_condition = ChapterUnlockConditionSerializer(read_only=True)
    is_locked = serializers.SerializerMethodField()
    prerequisite_progress = serializers.SerializerMethodField()

    def get_is_locked(self, obj):
        # Check if locked for current user
        # Implementation...

    def get_prerequisite_progress(self, obj):
        # Return completion status of prerequisites
        # Implementation...
```

### Admin Interface

#### Admin Inline
```python
class ChapterUnlockConditionInline(admin.TabularInline):
    model = ChapterUnlockCondition
    can_delete = False
    verbose_name_plural = "解锁条件"

class ChapterAdmin(admin.ModelAdmin):
    # ... existing code ...
    inlines = [ChapterUnlockConditionInline]
```

### Frontend Integration

#### TypeScript Types
```typescript
interface ChapterUnlockCondition {
  id: number;
  chapter: number;
  prerequisite_chapters: Chapter[];
  prerequisite_chapter_ids: number[];
  unlock_date: string | null;
  unlock_condition_type: 'prerequisite' | 'date' | 'all';
}

interface Chapter {
  // ... existing fields ...
  unlock_condition?: ChapterUnlockCondition;
  is_locked?: boolean;
  prerequisite_progress?: {
    total: number;
    completed: number;
    remaining_chapters: Chapter[];
  };
}
```

#### Component Changes
- Chapter list item: Show lock icon, prerequisite count
- Chapter detail: Lock screen with "Complete X more chapters to unlock"
- Admin chapter form: Add unlock condition editor

## Caching Strategy

### Cache Keys
```
chapter_unlock:{chapter_id}:{enrollment_id} -> bool (15 min)
chapter_prerequisite_progress:{chapter_id}:{enrollment_id} -> dict (15 min)
```

### Invalidation
- Invalidate on `ChapterProgress.completed` change
- Invalidate on `ChapterUnlockCondition` save/delete

## Database Schema Changes

### Migration Plan
```python
# Migration: add_chapter_unlock_condition
operations = [
    migrations.CreateModel(
        name='ChapterUnlockCondition',
        fields=[
            ('id', models.BigAutoField(primary_key=True)),
            ('unlock_date', models.DateTimeField(blank=True, null=True)),
            ('unlock_condition_type', models.CharField(
                choices=[...],
                default='all',
                max_length=20
            )),
            ('chapter', models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='unlock_condition',
                to='courses.chapter'
            )),
            ('prerequisite_chapters', models.ManyToManyField(
                blank=True,
                related_name='dependent_chapters',
                to='courses.chapter'
            )),
        ],
        options={
            'verbose_name': '章节解锁条件',
            'verbose_name_plural': '章节解锁条件',
        },
    ),
]
```

## Testing Strategy

### Unit Tests
- `ChapterUnlockServiceTest`: Test unlock logic for various scenarios
- `ChapterViewSetTest`: Test filtering of locked chapters
- `ChapterSerializerTest`: Test serialization of unlock status

### Integration Tests
- Create chapter with prerequisites, verify unlock flow
- Test prerequisite completion triggers unlock
- Test admin interface for setting conditions

## Security Considerations

1. **Server-side enforcement**: API must filter locked content, not rely on frontend
2. **Instructor bypass**: Instructors and admins see all chapters
3. **Cache poisoning**: Ensure cache is properly invalidated on progress changes

## Performance Impact

### Query Optimization
- Use `prefetch_related` for prerequisite chapters
- Cache unlock status checks (15 min default)
- Batch unlock checks for chapter list views

### Estimated Impact
- +1 query per chapter with unlock conditions (for prerequisites)
- Cached queries reduce repeated checks
- Negligible impact on courses without unlock conditions

## Migration & Rollout

### Phase 1: Backend
1. Create model and migration
2. Implement service layer
3. Add API filtering
4. Write tests

### Phase 2: Admin
1. Add admin interface
2. Test unlock condition creation

### Phase 3: Frontend
1. Update types
2. Add locked chapter UI
3. Add prerequisite progress display
4. Test end-to-end flow

### Backwards Compatibility
- Existing chapters without `ChapterUnlockCondition` remain unlocked
- No migration needed for existing data
- Optional feature - can be adopted incrementally
