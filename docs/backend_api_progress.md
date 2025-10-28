# 学习进度追踪API文档

学习进度追踪功能扩展了原有API，增加了用户课程参与、章节进度和问题进度相关的接口。所有新接口均位于 `/api/v1/` 前缀下。

## 课程参与相关 (/api/v1/enrollments/)

### 获取用户课程参与列表
- **URL**: `/api/v1/enrollments/`
- **方法**: GET
- **描述**: 获取当前用户参与的所有课程记录
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "参与记录ID",
        "user": "用户ID",
        "user_username": "用户名",
        "course": "课程ID",
        "course_title": "课程标题",
        "enrolled_at": "注册时间",
        "last_accessed_at": "最后访问时间",
        "progress_percentage": "进度百分比"
      }
    ]
  }
  ```

### 参与课程
- **URL**: `/api/v1/enrollments/`
- **方法**: POST
- **描述**: 用户参与指定课程
- **请求体**: 
  ```json
  {
    "course": "课程ID"
  }
  ```
- **响应**:
  ```json
  {
    "id": "参与记录ID",
    "user": "用户ID",
    "user_username": "用户名",
    "course": "课程ID",
    "course_title": "课程标题",
    "enrolled_at": "注册时间",
    "last_accessed_at": "最后访问时间",
    "progress_percentage": "进度百分比"
  }
  ```

### 获取特定课程参与详情
- **URL**: `/api/v1/enrollments/{id}/`
- **方法**: GET
- **描述**: 获取特定课程参与记录的详细信息
- **响应**:
  ```json
  {
    "id": "参与记录ID",
    "user": "用户ID",
    "user_username": "用户名",
    "course": "课程ID",
    "course_title": "课程标题",
    "enrolled_at": "注册时间",
    "last_accessed_at": "最后访问时间",
    "progress_percentage": "进度百分比"
  }
  ```

### 更新课程参与记录
- **URL**: `/api/v1/enrollments/{id}/`
- **方法**: PUT/PATCH
- **描述**: 更新特定课程参与记录信息
- **请求体**: 
  ```json
  {
    "course": "课程ID"
  }
  ```
- **响应**:
  ```json
  {
    "id": "参与记录ID",
    "user": "用户ID",
    "user_username": "用户名",
    "course": "课程ID",
    "course_title": "课程标题",
    "enrolled_at": "注册时间",
    "last_accessed_at": "最后访问时间",
    "progress_percentage": "进度百分比"
  }
  ```

### 删除课程参与记录
- **URL**: `/api/v1/enrollments/{id}/`
- **方法**: DELETE
- **描述**: 删除特定课程参与记录

## 章节进度相关 (/api/v1/chapter-progress/)

### 获取用户章节进度列表
- **URL**: `/api/v1/chapter-progress/`
- **方法**: GET
- **描述**: 获取当前用户所有章节的学习进度记录
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "章节进度ID",
        "enrollment": "课程参与记录ID",
        "chapter": "章节ID",
        "chapter_title": "章节标题",
        "course_title": "课程标题",
        "completed": "是否完成",
        "completed_at": "完成时间"
      }
    ]
  }
  ```

### 获取特定章节进度详情
- **URL**: `/api/v1/chapter-progress/{id}/`
- **方法**: GET
- **描述**: 获取特定章节进度记录的详细信息
- **响应**:
  ```json
  {
    "id": "章节进度ID",
    "enrollment": "课程参与记录ID",
    "chapter": "章节ID",
    "chapter_title": "章节标题",
    "course_title": "课程标题",
    "completed": "是否完成",
    "completed_at": "完成时间"
  }
  ```

### 标记章节为完成
- **URL**: `/api/v1/courses/{course_pk}/chapters/{chapter_pk}/mark-as-completed/`
- **方法**: POST
- **描述**: 将指定章节标记为已完成状态 或者创建进度
- **请求体**: 
  ```json
  {
    "completed": "true or false",
  }
  ```
- **响应**:
  ```json
  {
    "id": "章节进度ID",
    "enrollment": "课程参与记录ID",
    "chapter": "章节ID",
    "chapter_title": "章节标题",
    "course_title": "课程标题",
    "completed": true,
    "completed_at": "完成时间"
  }
  ```

## 问题进度相关 (/api/v1/problem-progress/)

### 获取用户问题进度列表
- **URL**: `/api/v1/problem-progress/`
- **方法**: GET
- **描述**: 获取当前用户所有问题的解决进度记录
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "问题进度ID",
        "enrollment": "课程参与记录ID",
        "problem": "问题ID",
        "problem_title": "问题标题",
        "chapter_title": "章节标题",
        "course_title": "课程标题",
        "status": "解决状态",
        "attempts": "尝试次数",
        "last_attempted_at": "最后尝试时间",
        "solved_at": "解决时间",
        "best_submission": "最佳提交记录ID"
      }
    ]
  }
  ```

### 获取特定问题进度详情
- **URL**: `/api/v1/problem-progress/{id}/`
- **方法**: GET
- **描述**: 获取特定问题进度记录的详细信息
- **响应**:
  ```json
  {
    "id": "问题进度ID",
    "enrollment": "课程参与记录ID",
    "problem": "问题ID",
    "problem_title": "问题标题",
    "chapter_title": "章节标题",
    "course_title": "课程标题",
    "status": "解决状态",
    "attempts": "尝试次数",
    "last_attempted_at": "最后尝试时间",
    "solved_at": "解决时间",
    "best_submission": "最佳提交记录ID"
  }
  ```

### 标记问题为已解决
- **URL**: `/api/v1/problems/{problem_pk}/mark_as_solved/`
- **方法**: POST
- **描述**: 将指定问题标记为已解决状态
- **请求体**: 
  ```json
  {
    "solved": "is solved"
  }
- **响应**:
  ```json
  {
    "id": "问题进度ID",
    "enrollment": "课程参与记录ID",
    "problem": "问题ID",
    "problem_title": "问题标题",
    "chapter_title": "章节标题",
    "course_title": "课程标题",
    "status": "solved",
    "attempts": "尝试次数",
    "last_attempted_at": "最后尝试时间",
    "solved_at": "解决时间",
    "best_submission": "最佳提交记录ID"
  }
  ```