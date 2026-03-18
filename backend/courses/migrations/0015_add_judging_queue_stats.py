# Generated manually for async-code-judging-system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0014_add_status_to_snapshots"),
    ]

    operations = [
        # Add task_id and estimated_wait_seconds to Submission model
        migrations.AddField(
            model_name="submission",
            name="task_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="关联的Celery异步任务ID",
                max_length=255,
                null=True,
                verbose_name="Celery任务ID"
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="estimated_wait_seconds",
            field=models.IntegerField(
                blank=True,
                help_text="基于队列长度预估的等待时间",
                null=True,
                verbose_name="预估等待时间(秒)"
            ),
        ),
        # Create JudgingQueueStats model
        migrations.CreateModel(
            name="JudgingQueueStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "等待中"),
                            ("started", "已开始"),
                            ("success", "成功"),
                            ("failed", "失败"),
                            ("timeout", "超时"),
                            ("cancelled", "已取消"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                        verbose_name="队列状态"
                    ),
                ),
                (
                    "queue_position",
                    models.IntegerField(
                        blank=True,
                        help_text="在队列中的位置（从1开始）",
                        null=True,
                        verbose_name="队列位置"
                    ),
                ),
                (
                    "estimated_start_time",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="预估开始时间"
                    ),
                ),
                (
                    "started_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="实际开始时间"
                    ),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="完成时间"
                    ),
                ),
                (
                    "queue_wait_seconds",
                    models.IntegerField(
                        blank=True,
                        help_text="从提交到开始执行的秒数",
                        null=True,
                        verbose_name="实际等待时间(秒)"
                    ),
                ),
                (
                    "execution_seconds",
                    models.IntegerField(
                        blank=True,
                        help_text="从开始到完成的秒数",
                        null=True,
                        verbose_name="执行时长(秒)"
                    ),
                ),
                (
                    "worker_name",
                    models.CharField(
                        blank=True,
                        help_text="处理此任务的Worker进程标识",
                        max_length=255,
                        null=True,
                        verbose_name="Worker名称"
                    ),
                ),
                (
                    "retry_count",
                    models.IntegerField(
                        default=0,
                        verbose_name="重试次数"
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True,
                        help_text="失败或超时的详细错误信息",
                        verbose_name="错误信息"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="创建时间"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="更新时间"
                    ),
                ),
                (
                    "submission",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="queue_stats",
                        to="courses.submission",
                        verbose_name="关联提交记录"
                    ),
                ),
            ],
            options={
                "verbose_name": "评测队列统计",
                "verbose_name_plural": "评测队列统计",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status", "created_at"], name="courses_que_status_idx"),
                    models.Index(fields=["submission", "status"], name="courses_que_sub_idx"),
                    models.Index(fields=["created_at"], name="courses_que_created_idx"),
                    models.Index(fields=["started_at"], name="courses_que_started_idx"),
                    models.Index(fields=["completed_at"], name="courses_que_completed_idx"),
                ],
            },
        ),
    ]
