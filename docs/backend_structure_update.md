# 项目结构更新说明

## 新增功能模块

### 学习进度追踪模块
为了实现学习进度追踪功能，我们在`courses`应用中新增了以下组件：

#### 数据模型 (models.py)
1. **Enrollment** - 课程参与模型
   - 记录用户参与课程的关系
   - 包含注册时间和最后访问时间
   - 自动计算学习进度百分比

2. **ChapterProgress** - 章节进度模型
   - 记录用户在特定章节的学习完成状态
   - 包含完成状态和完成时间

3. **ProblemProgress** - 问题进度模型
   - 记录用户解决问题的进度和状态
   - 包含解决状态、尝试次数、最后尝试时间等信息
   - 对于算法题，还记录最佳提交记录

#### 序列化器 (serializers.py)
1. **EnrollmentSerializer** - 课程参与序列化器
   - 提供课程参与信息的序列化和反序列化
   - 计算并返回学习进度百分比

2. **ChapterProgressSerializer** - 章节进度序列化器
   - 提供章节进度信息的序列化和反序列化

3. **ProblemProgressSerializer** - 问题进度序列化器
   - 提供问题进度信息的序列化和反序列化

#### 视图集 (views.py)
1. **EnrollmentViewSet** - 课程参与视图集
   - 提供课程参与的CRUD操作
   - 只允许用户查看和操作自己的参与记录

2. **ChapterProgressViewSet** - 章节进度视图集
   - 提供章节进度的只读操作
   - 只允许用户查看自己的进度记录

3. **ProblemProgressViewSet** - 问题进度视图集
   - 提供问题进度的只读操作
   - 只允许用户查看自己的进度记录

#### URL路由 (urls.py)
1. **新增路由**:
   - `/api/v1/enrollments/` - 课程参与相关接口
   - `/api/v1/chapter-progress/` - 章节进度相关接口
   - `/api/v1/problem-progress/` - 问题进度相关接口
   - `/api/v1/courses/{course_pk}/chapters/{chapter_pk}/mark-as-completed/` - 标记章节为完成的接口
   - `/api/v1/problems/{problem_pk}/mark_as_solved/` - 标记问题为已解决的接口

#### 数据库迁移
1. **新增迁移文件**:
   - `0002_alter_problem_type_enrollment_chapterprogress_and_more.py` - 添加了新的学习进度相关模型表

#### 文档更新
1. **新增文档文件**:
   - `backend_api_progress.md` - 学习进度追踪API详细文档
   - `backend_progress_feature.md` - 学习进度追踪功能说明

这些新增模块共同构成了完整的学习进度追踪功能，使用户能够更好地跟踪和管理自己的学习进程。