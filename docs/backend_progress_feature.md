# 学习进度追踪功能说明

## 功能概述
学习进度追踪功能允许用户跟踪他们在课程中的学习进度，包括课程参与、章节完成情况和问题解决进度。系统会自动记录用户的学习行为，并计算总体进度百分比。

## 核心概念

### 1. 课程参与 (Enrollment)
表示用户参与某门课程的关系记录，包含以下信息：
- 用户ID
- 课程ID
- 注册时间
- 最后访问时间
- 学习进度百分比（基于完成章节的数量）

### 2. 章节进度 (ChapterProgress)
记录用户在特定章节的学习完成状态：
- 课程参与记录ID
- 章节ID
- 是否完成
- 完成时间

### 3. 问题进度 (ProblemProgress)
记录用户解决问题的进度和状态：
- 课程参与记录ID
- 问题ID
- 解决状态（未开始、进行中、已解决、失败）
- 尝试次数
- 最后尝试时间
- 解决时间
- 最佳提交记录（对于算法题）

## API接口

详细API文档请参见 [学习进度追踪API文档](backend_api_progress.md)

## 数据模型

### Enrollment (课程参与)
- `user`: 参与用户（外键到User模型）
- `course`: 参与课程（外键到Course模型）
- `enrolled_at`: 注册时间（自动设置）
- `last_accessed_at`: 最后访问时间（自动更新）

### ChapterProgress (章节进度)
- `enrollment`: 课程参与记录（外键到Enrollment模型）
- `chapter`: 章节（外键到Chapter模型）
- `completed`: 是否完成（布尔值）
- `completed_at`: 完成时间（当completed设为True时自动设置）

### ProblemProgress (问题进度)
- `enrollment`: 课程参与记录（外键到Enrollment模型）
- `problem`: 问题（外键到Problem模型）
- `status`: 解决状态（choices: not_started, in_progress, solved, failed）
- `attempts`: 尝试次数（每次提交增加）
- `last_attempted_at`: 最后尝试时间（每次提交更新）
- `solved_at`: 解决时间（当status设为solved时自动设置）
- `best_submission`: 最佳提交记录（外键到Submission模型，对于算法题，指向执行时间最短的成功提交）

## 使用流程

### 1. 用户参与课程
用户通过调用 `/api/v1/enrollments/` 接口参与课程，系统会创建一条Enrollment记录。

### 2. 学习章节
用户学习完某个章节后，可以通过调用相应章节的 `mark-as-completed` 接口标记章节为已完成。

### 3. 解决问题
当用户提交问题解决方案并通过评测时，系统会自动更新问题进度记录：
- 对于算法题，每次成功提交都会更新ProblemProgress中的best_submission字段
- 对于选择题，用户答对后会更新ProblemProgress状态为solved

### 4. 查看进度
用户可以随时通过 `/api/v1/enrollments/` 接口查看自己在各门课程中的学习进度。