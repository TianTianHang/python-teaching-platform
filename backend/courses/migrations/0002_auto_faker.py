# courses/migrations/0002_populate_courses_with_faker.py

from django.db import migrations
from faker import Faker

def create_fake_courses_with_faker(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    Chapter = apps.get_model('courses', 'Chapter')
    fake = Faker('zh_CN')  # 使用中文数据（可选，也可用 'en_US'）

    # 生成 10 门课程
    courses = []
    for _ in range(10):
        course = Course(
            title=fake.sentence(nb_words=4).rstrip('.'),
            description=fake.paragraph(nb_sentences=3)
        )
        courses.append(course)
    
    Course.objects.bulk_create(courses)

    # 为每门课程生成 3~6 个章节
    all_chapters = []
    for course in Course.objects.all():
        num_chapters = fake.random_int(min=3, max=6)
        used_orders = set()
        for i in range(num_chapters):
            # 确保 order 不重复（unique_together）
            order = fake.random_int(min=1, max=20)
            while order in used_orders:
                order = fake.random_int(min=1, max=20)
            used_orders.add(order)

            chapter = Chapter(
                course=course,
                title=fake.sentence(nb_words=3).rstrip('.'),
                content=fake.text(max_nb_chars=500),
                order=order
            )
            all_chapters.append(chapter)
    
    Chapter.objects.bulk_create(all_chapters)


def reverse_fake_data(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    Course.objects.all().delete()  # 级联删除章节（因 ForeignKey 设置了 CASCADE）


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),  # 确保匹配你的初始迁移名
    ]

    operations = [
        migrations.RunPython(create_fake_courses_with_faker, reverse_fake_data),
    ]