# 数据库模型文档

## accounts 应用

### User
继承自Django的AbstractUser，扩展了学号字段。
- `st_number`: 学号 (CharField, unique=True, null=True)

## courses 应用

### Course (课程)
- `title`: 课程标题 (CharField)
- `description`: 课程描述 (TextField, 可为空)
- `created_at`: 创建时间 (DateTimeField, auto_now_add)
- `updated_at`: 更新时间 (DateTimeField, auto_now)

### Chapter (章节)
- `course`: 所属课程 (ForeignKey to Course)
- `title`: 章节标题 (CharField)
- `content`: 章节内容 (TextField, 可为空)
- `order`: 章节顺序 (PositiveIntegerField, default=0)
- `created_at`: 创建时间 (DateTimeField, auto_now_add)
- `updated_at`: 更新时间 (DateTimeField, auto_now)

### Problem (问题基类)
- `chapter`: 所属章节 (ForeignKey to Chapter, 可为空)
- `type`: 问题类型 (CharField, choices={'algorithm', 'choice'})
- `title`: 问题标题 (CharField)
- `content`: 问题内容 (TextField)
- `difficulty`: 难度等级 (PositiveSmallIntegerField, 1-3)
- `created_at`: 创建时间 (DateTimeField, auto_now_add)
- `updated_at`: 更新时间 (DateTimeField, auto_now)

### AlgorithmProblem (算法题详情)
一对一关联Problem主表，存储算法题特有属性。
- `problem`: 关联问题主表 (OneToOneField to Problem)
- `time_limit`: 时间限制(毫秒) (PositiveSmallIntegerField, default=1000)
- `memory_limit`: 内存限制(MB) (PositiveSmallIntegerField, default=256)
- `code_template`: 编码模板 (JSONField, 可为空)
- `solution_name`: 解决方案函数名 (JSONField, 可为空)

### ChoiceProblem (选择题详情)
一对一关联Problem主表，存储选择题特有属性。
- `problem`: 关联问题主表 (OneToOneField to Problem)
- `options`: 选项列表 (JSONField)
- `correct_answer`: 正确答案 (JSONField)
- `is_multiple_choice`: 是否为多选题 (BooleanField, default=False)

### TestCase (测试用例)
用于算法题的测试用例。
- `problem`: 所属问题 (ForeignKey to AlgorithmProblem)
- `input_data`: 输入数据 (TextField)
- `expected_output`: 预期输出 (TextField)
- `is_sample`: 是否为示例测试用例 (BooleanField, default=False)
- `created_at`: 创建时间 (DateTimeField, auto_now_add)

### Submission (提交记录)
记录用户对算法题的提交和评测结果。
- `user`: 提交用户 (ForeignKey to User)
- `problem`: 提交的问题 (ForeignKey to Problem, 可为空)
- `code`: 提交的代码 (TextField)
- `language`: 编程语言 (CharField, default="python")
- `status`: 评测状态 (CharField)
- `execution_time`: 执行时间(毫秒) (FloatField, 可为空)
- `memory_used`: 内存使用(KB) (FloatField, 可为空)
- `output`: 程序输出 (TextField, 可为空)
- `error`: 错误信息 (TextField, 可为空)
- `created_at`: 提交时间 (DateTimeField, auto_now_add)
- `updated_at`: 更新时间 (DateTimeField, auto_now)