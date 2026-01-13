# 课程内容故障排查指南

本文档帮助课程内容创作者解决常见的格式错误、导入问题和创作过程中的各种困难。

## 📋 目录

- [格式错误排查](#格式错误排查)
- [导入失败排查](#导入失败排查)
- [创作过程问题](#创作过程问题)
- [工具使用问题](#工具使用问题)
- [性能优化](#性能优化)
- [常见 FAQ](#常见-faq)
- [联系支持](#联系支持)

## 🔧 格式错误排查

### YAML Frontmatter 错误

#### 错误类型 1：缺少引号

**错误示例：**
```yaml
title: Python编程入门
description: 这是一个描述
```

**问题：** YAML 中字符串需要引号

**解决方案：**
```yaml
title: "Python编程入门"
description: "这是一个描述"
```

#### 错误类型 2：数组格式错误

**错误示例：**
```yaml
tags: [python, 基础, 编程]
prerequisites: [Python基础]
```

**问题：** YAML 数组需要使用中括号和逗号

**解决方案：**
```yaml
tags: ["python", "基础", "编程"]
prerequisites: ["Python基础"]
```

#### 错误类型 3：冒号后面缺少空格

**错误示例：**
```yaml
title:"Python编程入门"
```

**问题：** YAML 键值对需要冒号后有空格

**解决方案：**
```yaml
title: "Python编程入门"
```

#### 检查工具
使用在线 YAML 验证器：
- [YAML Lint](https://www.yamllint.com/)
- [JSON to YAML Converter](https://codebeautify.org/yaml-to-json-xml-csv)

### 标记格式错误

#### 错误类型 1：章节标记错误

**错误示例：**
```markdown
## 章节标题
```

**问题：** 缺少"章节："前缀

**解决方案：**
```markdown
## 章节：章节标题
```

#### 错误类型 2：题目标记错误

**错误示例：**
```markdown
### 算法题：两数之和
```

**问题：** 需要包含题号

**解决方案：**
```markdown
### 题目 1：两数之和
```

#### 错误类型 3：元数据格式错误

**错误示例：**
```markdown
**类型**：algorithm
**难度**：1
```

**问题：** 缺少冒号后的空格

**解决方案：**
```markdown
**类型：** algorithm
**难度：** 1
```

### 测试用例错误

#### 错误类型 1：JSON 格式错误

**错误示例：**
```yaml
- input: [1,2,3]
  output: "123"
```

**问题：** 数组需要用引号包裹

**解决方案：**
```yaml
- input: "[1,2,3]"
  output: "[1,2,3]"
```

#### 错误类型 2：缺少 is_sample

**错误示例：**
```yaml
- input: "\"()\""
  output: "true"
```

**问题：** 至少需要一个示例用例

**解决方案：**
```yaml
- input: "\"()\""
  output: "true"
  is_sample: true
```

#### 错误类型 3：多行字符串格式错误

**错误示例：**
```yaml
input: "第一行\n第二行"
```

**问题：** 多行字符串处理

**解决方案：**
```yaml
input: |-
  第一行
  第二行
```

## 📥 导入失败排查

### 导入脚本常见错误

#### 错误 1：文件不存在

**错误信息：**
```
Error: Course file not found: /path/to/courses/01-course.md
```

**排查步骤：**
1. 检查文件路径是否正确
2. 确认文件是否在指定目录
3. 检查文件权限

**解决方案：**
```bash
# 检查目录结构
ls -la courses/

# 检查文件是否存在
ls courses/01-course.md

# 检查文件权限
ls -l courses/01-course.md
```

#### 错误 2：格式验证失败

**错误信息：**
```
Validation Error:
- title is required
- description is required
- difficulty must be beginner/intermediate/advanced
```

**排查步骤：**
1. 检查 YAML Frontmatter
2. 确认所有必填字段
3. 验证字段值格式

**解决方案：**
```bash
# 使用 dry-run 模式验证
python manage.py import_courses --dry-run

# 检查特定文件
python manage.py import_courses --course=course-name --dry-run
```

#### 错误 3：解析错误

**错误信息：**
```
Parse Error: Failed to parse YAML at line 10
```

**排查步骤：**
1. 检查 YAML 语法
2. 查看错误行附近的格式
3. 使用 YAML 验证工具

**解决方案：**
```bash
# 查看错误行
head -n 15 courses/01-course.md | tail -n 5

# 使用 YAML 验证工具
python -c "import yaml; print(yaml.safe_load(open('courses/01-course.md').split('---')[1]))"
```

### 数据库错误

#### 错误 1：重复课程

**错误信息：**
```
Error: Course with title "Python入门" already exists
```

**排查步骤：**
1. 检查数据库中是否已存在
2. 确认课程标题唯一性
3. 考虑使用 --overwrite 参数

**解决方案：**
```bash
# 查看现有课程
python manage.py shell -c "
from courses.models import Course
print(Course.objects.count())
for course in Course.objects.all():
    print(f'{course.title}: {course.id}')
"

# 使用覆盖模式
python manage.py import_courses --overwrite
```

#### 错误 2：外键约束错误

**错误信息：**
```
Error: Cannot assign "None": "Chapter.course" must be a "Course" instance.
```

**排查步骤：**
1. 检查课程创建是否成功
2. 确认章节的 course 关联正确
3. 查看导入日志

**解决方案：**
```bash
# 查看课程创建情况
python manage.py shell -c "
from courses.models import Course
print('Courses:', Course.objects.count())
from courses.models import Chapter
print('Chapters:', Chapter.objects.count())
"

# 重新导入
python manage.py import_courses --overwrite
```

## 🎨 创作过程问题

### 编辑器问题

#### 问题 1：Markdown 语法高亮失效

**症状：**
- 代码块没有语法高亮
- YAML 显示为普通文本

**解决方案：**
1. 使用支持 YAML 的编辑器（VS Code）
2. 安装相关插件
3. 检查文件扩展名（.md）

#### 问题 2：YAML 自动格式化破坏格式

**症状：**
- 导入后格式错乱
- 缩进混乱

**解决方案：**
1. 使用 YAML 格式化工具
2. 统一使用 2 空格缩进
3. 避免使用自动格式化

#### 问题 3：多行字符串处理

**症状：**
- 测试用例中的多行字符串显示异常

**解决方案：**
```yaml
# 使用 |- 保留换行
- input: |-
  第一行
  第二行
  第三行
  output: "完整内容"
```

### 写作效率问题

#### 问题 1：重复工作多

**解决方案：**
1. 使用模板开始创作
2. 创建快捷方式
3. 使用片段（Snippets）

**VS Code 配置示例：**
```json
{
  "Python课程章节": {
    "prefix": "chapter",
    "body": [
      "## 章节：${1:章节标题}",
      "",
      "### 章节概述",
      "",
      "本章将介绍 ${2:主题}，帮助你理解 ${3:概念}，掌握 ${4:技能}。",
      "",
      "### 学习内容",
      "",
      "#### 知识点 1：${5:知识点}",
      "",
      "**描述：**",
      "${6:描述}",
      "",
      "**示例代码：**",
      "```python",
      "# 代码示例",
      "```",
      ""
    ]
  }
}
```

#### 问题 2：难以保持一致性

**解决方案：**
1. 创建风格指南
2. 使用检查清单
3. 定期回顾和统一

### 内容质量保证

#### 问题 1：代码示例错误

**解决方案：**
```bash
# 创建代码验证脚本
#!/bin/bash
# validate_code.sh

for file in courses/*.md; do
    # 提取代码块并执行
    python validate_course_code.py "$file"
done
```

#### 问题 2：测试用例不足

**解决方案：**
1. 创建测试用例模板
2. 使用测试用例生成器
3. 自动化测试覆盖检查

## 🛠️ 工具使用问题

### Git 操作问题

#### 问题 1：分支切换失败

**错误：**
```
fatal: 'course-content' is not a branch name
```

**解决方案：**
```bash
# 确认分支存在
git branch -a

# 创建远程分支跟踪
git checkout -b course-content origin/course-content

# 或者重新创建分支
git checkout --orphan course-content
```

#### 问题 2：文件权限问题

**错误：**
```
Permission denied: courses/01-course.md
```

**解决方案：**
```bash
# 修改文件权限
chmod 644 courses/*.md

# 修改目录权限
chmod 755 courses/
```

### Markdown 编辑器问题

#### 问题 1：表格渲染异常

**症状：**
- 表格显示错乱
- 对齐有问题

**解决方案：**
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
```

#### 问题 2：代码块语言识别错误

**症状：**
- Python 代码没有语法高亮

**解决方案：**
```markdown
```python  # 确保使用 python
def function():
    pass
```
```

## 🚀 性能优化

### 大文件处理

#### 问题：课程文件过大

**症状：**
- 打开文件缓慢
- 编辑器卡顿

**解决方案：**
1. 拆分大章节为多个小章节
2. 使用增量加载
3. 优化图片和代码大小

```markdown
# 坏的做法：100KB 的单章节
## 章节：Python编程（100页内容）

# 好的做法：拆分为多个章节
## 章节：Python基础语法
## 章节：Python控制流
## 章节：Python函数
```

### 导入性能优化

#### 问题：导入速度慢

**症状：**
- 导入花费很长时间
- 数据库压力大

**解决方案：**
1. 使用批量插入
2. 禁用索引创建
3. 使用事务

**优化后的导入脚本：**
```python
def import_course_optimized(course_data):
    with transaction.atomic():
        # 批量创建
        Course.objects.bulk_create([course_data['course']])

        # 批量章节创建
        chapters = []
        for ch in course_data['chapters']:
            chapters.append(Chapter(**ch))
        Chapter.objects.bulk_create(chapters)

        # 其他批量操作...
```

## ❓ 常见 FAQ

### Q1：如何快速验证课程文档格式？

**A：** 使用以下命令进行快速验证：
```bash
# 方法1：使用 dry-run
python manage.py import_courses --dry-run

# 方法2：使用在线工具
https://www.yamllint.com/
https://markdownlint.com/

# 方法3：使用 VSCode 插件
- YAML
- Markdownlint
```

### Q2：如何添加图片资源？

**A：** 按照以下步骤：
1. 将图片放在 `media/images/` 目录
2. 使用相对路径引用
3. 更新后需要重新导入

```markdown
![描述](media/images/python-basics.png)
```

### Q3：如何测试算法题的测试用例？

**A：** 创建测试脚本：
```python
# test_problems.py
def test_algorithm():
    from courses.models import AlgorithmProblem, TestCase

    problem = AlgorithmProblem.objects.get(title="两数之和")
    for test_case in problem.testcases.all():
        # 执行测试
        print(f"Input: {test_case.input_data}")
        print(f"Expected: {test_case.expected_output}")
```

### Q4：如何处理多语言内容？

**A：** 使用多语言格式：
```yaml
---
title:
  zh: "Python编程入门"
  en: "Python Programming Basics"
description:
  zh: "学习Python编程的基础知识"
  en: "Learn the basics of Python programming"
---
```

### Q5：如何更新已存在的课程？

**A：** 使用覆盖模式：
```bash
# 覆盖更新
python manage.py import_courses --overwrite

# 更新特定课程
python manage.py import_courses --course=python-basics --overwrite
```

### Q6：如何设置题目解锁条件？

**A：** 在数据库中手动设置（目前功能待开发）：
```python
# 在导入后添加解锁条件
from courses.models import ProblemUnlockCondition

unlock = ProblemUnlockCondition(
    problem=problem,
    prerequisite_problem=prereq_problem,
    unlock_date=None  # 立即解锁
)
unlock.save()
```

### Q7：如何导出课程内容？

**A：** 使用导出脚本（需要开发）：
```bash
# 导出为 Markdown
python manage.py export_courses --course=python-basics

# 导出所有课程
python manage.py export_courses --format=markdown
```

### Q8：如何协作编辑课程？

**A：** 使用 Git 工作流：
```bash
# 克隆仓库
git clone https://github.com/your-repo/course-content.git

# 创建功能分支
git checkout -b feature/new-course

# 编写课程内容
git add courses/01-new-course.md
git commit -m "Add: New Course"
git push origin feature/new-course

# 创建 PR
```

### Q9：如何处理版权问题？

**A：**
1. 确保所有原创内容
2. 使用开源许可证（MIT）
3. 引用外部资源时注明出处
4. 避免使用受版权保护的图片

### Q10：如何获得帮助？

**A：**
1. 查看文档
   - [格式规范](format-specification.md)
   - [创作指南](course-authoring-guide.md)
   - [故障排查](troubleshooting.md)
2. 提交 Issue
3. 加入社区讨论
4. 联系支持团队

## 🔧 高级故障排查

### 数据库调试

#### 查看导入详情
```python
# 在 Django shell 中
from courses.models import Course, Chapter, Problem

print("=== 课程统计 ===")
print(f"总课程数: {Course.objects.count()}")
print(f"总章节数: {Chapter.objects.count()}")
print(f"总题数: {Problem.objects.count()}")

# 查看导入失败的记录
from courses.management.commands.import_courses import ImportErrorHandler
handler = ImportErrorHandler()
print(handler.errors)
```

### 日志分析

#### 启用详细日志
```bash
# 在 Django 设置中添加 LOGGING
python manage.py import_courses --verbose 2>&1 | tee import.log
```

#### 分析导入日志
```bash
# 查看错误统计
grep "ERROR" import.log | wc -l

# 查看警告统计
grep "WARNING" import.log | wc -l

# 查看成功导入的课程
grep "Success" import.log
```

### 性能分析

#### 慢查询分析
```python
# 分析数据库查询
from django.db import connection

# 执行慢查询分析
with connection.cursor() as cursor:
    cursor.execute("EXPLAIN ANALYZE SELECT * FROM courses_course;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
```

## 📞 联系支持

### 获取帮助

#### 1. 自助服务
- 查看 [格式规范](format-specification.md)
- 阅读 [创作指南](course-authoring-guide.md)
- 检查 [故障排查](troubleshooting.md)
- 搜索 [FAQ](#常见-faq)

#### 2. 社区支持
- GitHub Issues
- 讨论论坛
- QQ 群：123456789
- 微信群：扫码加入

#### 3. 专业支持
- 邮件：support@example.com
- 电话：400-123-4567
- 工作时间：周一至周五 9:00-18:00

### 报告问题

#### 问题报告模板
```markdown
## 问题描述
[简要描述遇到的问题]

## 环境信息
- 操作系统：[如 Ubuntu 20.04]
- Python 版本：[如 3.8.5]
- Django 版本：[如 3.2.0]
- 编辑器：[如 VS Code 1.50]

## 复现步骤
1. [第一步操作]
2. [第二步操作]
3. [第三步操作]

## 期望结果
[描述应该发生的事情]

## 实际结果
[描述实际发生的事情]

## 错误信息
[提供完整的错误信息]

## 其他信息
[补充任何有用的信息]
```

### 贡献改进

#### 1. 修复文档
- Fork 仓库
- 修复错误
- 提交 Pull Request

#### 2. 添加内容
- 添加新的解决方案
- 分享使用技巧
- 完善文档

#### 3. 反馈建议
- 功能需求
- 改进建议
- 使用体验

---

*本故障排查指南将持续更新，欢迎贡献解决方案。*
*让我们一起打造更好的课程内容创作体验！*