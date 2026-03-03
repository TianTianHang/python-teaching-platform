# Generated data migration to add status field to existing snapshots

from django.db import migrations


def add_status_to_course_snapshots(apps, schema_editor):
    """
    为现有的 CourseUnlockSnapshot 添加 status 字段

    遍历所有现有的快照，为每个章节的 unlock_states 添加 status 字段。
    status 值根据 ChapterProgress 记录计算：
    - 如果章节已完成：'completed'
    - 如果章节已开始但未完成：'in_progress'
    - 如果章节未开始：'not_started'
    """
    CourseUnlockSnapshot = apps.get_model('courses', 'CourseUnlockSnapshot')
    ChapterProgress = apps.get_model('courses', 'ChapterProgress')

    for snapshot in CourseUnlockSnapshot.objects.all():
        # 获取该用户在该课程中的章节进度
        progress_records = ChapterProgress.objects.filter(
            enrollment=snapshot.enrollment,
            chapter__course=snapshot.course
        ).values('chapter_id', 'completed')

        # 构建进度映射
        progress_map = {p['chapter_id']: p['completed'] for p in progress_records}

        # 更新 unlock_states
        updated_states = {}
        for chapter_id, state in snapshot.unlock_states.items():
            # 复制现有字段
            updated_states[chapter_id] = dict(state)

            # 添加 status 字段（如果不存在）
            if 'status' not in updated_states[chapter_id]:
                chapter_id_int = int(chapter_id)
                is_completed = progress_map.get(chapter_id_int, False)

                if chapter_id_int not in progress_map:
                    status = 'not_started'
                elif is_completed:
                    status = 'completed'
                else:
                    status = 'in_progress'

                updated_states[chapter_id]['status'] = status

        # 保存更新后的快照
        snapshot.unlock_states = updated_states
        snapshot.save(update_fields=['unlock_states'])


def add_status_to_problem_snapshots(apps, schema_editor):
    """
    为现有的 ProblemUnlockSnapshot 添加 status 字段

    遍历所有现有的快照，为每个问题的 unlock_states 添加 status 字段。
    status 值根据 ProblemProgress 记录计算：
    - 如果问题已解决：'solved'
    - 如果问题正在尝试：'in_progress'
    - 如果问题未开始：'not_started'
    - 如果问题失败：'failed'
    """
    ProblemUnlockSnapshot = apps.get_model('courses', 'ProblemUnlockSnapshot')
    ProblemProgress = apps.get_model('courses', 'ProblemProgress')

    for snapshot in ProblemUnlockSnapshot.objects.all():
        # 获取该用户在该课程中的问题进度
        progress_records = ProblemProgress.objects.filter(
            enrollment=snapshot.enrollment,
            problem__chapter__course=snapshot.course
        ).values('problem_id', 'status')

        # 构建进度映射
        progress_map = {p['problem_id']: p['status'] for p in progress_records}

        # 更新 unlock_states
        updated_states = {}
        for problem_id, state in snapshot.unlock_states.items():
            # 复制现有字段
            updated_states[problem_id] = dict(state)

            # 添加 status 字段（如果不存在）
            if 'status' not in updated_states[problem_id]:
                problem_id_int = int(problem_id)
                # 从进度映射获取状态，默认为 'not_started'
                status = progress_map.get(problem_id_int, 'not_started')
                updated_states[problem_id]['status'] = status

        # 保存更新后的快照
        snapshot.unlock_states = updated_states
        snapshot.save(update_fields=['unlock_states'])


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_problemunlocksnapshot'),
    ]

    operations = [
        migrations.RunPython(
            add_status_to_course_snapshots,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            add_status_to_problem_snapshots,
            reverse_code=migrations.RunPython.noop,
        ),
    ]