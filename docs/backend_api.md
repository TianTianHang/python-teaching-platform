# 后端API文档

所有API端点均位于 `/api/v1/` 前缀下。

## 认证相关 (/api/v1/auth/)

### 登录
- **URL**: `/api/v1/auth/login`
- **方法**: POST
- **描述**: 用户登录，获取访问令牌和刷新令牌
- **请求体**: 
  ```json
  {
    "username": "用户名或学号",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "refresh": "刷新令牌",
    "access": "访问令牌",
    "user_id": "用户ID",
    "username": "用户名",
    "st_number": "学号"
  }
  ```

### 注册
- **URL**: `/api/v1/auth/register`
- **方法**: POST
- **描述**: 新用户注册
- **请求体**: 
  ```json
  {
    "username": "用户名",
    "password": "密码",
    "st_number": "学号"
  }
  ```
- **响应**:
  ```json
  {
    "user": {
      "id": "用户ID",
      "username": "用户名",
      "st_number": "学号"
    },
    "access": "访问令牌",
    "refresh": "刷新令牌"
  }
  ```

### 登出
- **URL**: `/api/v1/auth/logout`
- **方法**: POST
- **描述**: 用户登出，将刷新令牌加入黑名单
- **请求体**: 
  ```json
  {
    "refresh": "刷新令牌"
  }
  ```
- **响应**:
  ```json
  {
    "detail": "Successfully logged out."
  }
  ```

### 获取当前用户信息
- **URL**: `/api/v1/auth/me`
- **方法**: GET
- **描述**: 获取当前登录用户的信息
- **响应**:
  ```json
  {
    "id": "用户ID",
    "username": "用户名",
    "st_number": "学号"
  }
  ```

### 刷新令牌
- **URL**: `/api/v1/auth/refresh`
- **方法**: POST
- **描述**: 使用刷新令牌获取新的访问令牌
- **请求体**: 
  ```json
  {
    "refresh": "刷新令牌"
  }
  ```
- **响应**:
  ```json
  {
    "access": "新的访问令牌"
  }
  ```

### 验证令牌
- **URL**: `/api/v1/auth/verify`
- **方法**: POST
- **描述**: 验证令牌的有效性
- **请求体**: 
  ```json
  {
    "token": "JWT令牌"
  }
  ```
- **响应**:
  ```json
  {
    "token": "令牌有效"
  }
  ```

## 课程相关 (/api/v1/courses/)

### 获取课程列表
- **URL**: `/api/v1/courses/`
- **方法**: GET
- **描述**: 获取所有课程列表
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "课程ID",
        "title": "课程标题",
        "description": "课程描述",
        "created_at": "创建时间",
        "updated_at": "更新时间"
      }
    ]
  }
  ```

### 创建课程
- **URL**: `/api/v1/courses/`
- **方法**: POST
- **描述**: 创建新课程
- **请求体**: 
  ```json
  {
    "title": "课程标题",
    "description": "课程描述"
  }
  ```
- **响应**:
  ```json
  {
    "id": "课程ID",
    "title": "课程标题",
    "description": "课程描述",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 获取特定课程详情
- **URL**: `/api/v1/courses/{id}/`
- **方法**: GET
- **描述**: 获取特定课程的详细信息
- **响应**:
  ```json
  {
    "id": "课程ID",
    "title": "课程标题",
    "description": "课程描述",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 更新课程
- **URL**: `/api/v1/courses/{id}/`
- **方法**: PUT/PATCH
- **描述**: 更新特定课程信息
- **请求体**: 
  ```json
  {
    "title": "课程标题",
    "description": "课程描述"
  }
  ```
- **响应**:
  ```json
  {
    "id": "课程ID",
    "title": "课程标题",
    "description": "课程描述",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 删除课程
- **URL**: `/api/v1/courses/{id}/`
- **方法**: DELETE
- **描述**: 删除特定课程

### 参与课程
- **URL**: `/api/v1/courses/{id}/enroll/`
- **方法**: POST
- **描述**: 用户参与指定课程
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

## 章节相关 (/api/v1/courses/{course_pk}/chapters/)

### 获取课程下章节列表
- **URL**: `/api/v1/courses/{course_pk}/chapters/`
- **方法**: GET
- **描述**: 获取特定课程下的所有章节
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "章节ID",
        "course": "课程ID",
        "course_title": "课程标题",
        "title": "章节标题",
        "content": "章节内容",
        "order": "章节顺序",
        "created_at": "创建时间",
        "updated_at": "更新时间"
      }
    ]
  }
  ```

### 创建章节
- **URL**: `/api/v1/courses/{course_pk}/chapters/`
- **方法**: POST
- **描述**: 在特定课程下创建新章节
- **请求体**: 
  ```json
  {
    "title": "章节标题",
    "content": "章节内容",
    "order": "章节顺序"
  }
  ```
- **响应**:
  ```json
  {
    "id": "章节ID",
    "course": "课程ID",
    "course_title": "课程标题",
    "title": "章节标题",
    "content": "章节内容",
    "order": "章节顺序",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 获取特定章节详情
- **URL**: `/api/v1/courses/{course_pk}/chapters/{id}/`
- **方法**: GET
- **描述**: 获取特定章节的详细信息
- **响应**:
  ```json
  {
    "id": "章节ID",
    "course": "课程ID",
    "course_title": "课程标题",
    "title": "章节标题",
    "content": "章节内容",
    "order": "章节顺序",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 更新章节
- **URL**: `/api/v1/courses/{course_pk}/chapters/{id}/`
- **方法**: PUT/PATCH
- **描述**: 更新特定章节信息
- **请求体**: 
  ```json
  {
    "title": "章节标题",
    "content": "章节内容",
    "order": "章节顺序"
  }
  ```
- **响应**:
  ```json
  {
    "id": "章节ID",
    "course": "课程ID",
    "course_title": "课程标题",
    "title": "章节标题",
    "content": "章节内容",
    "order": "章节顺序",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 删除章节
- **URL**: `/api/v1/courses/{course_pk}/chapters/{id}/`
- **方法**: DELETE
- **描述**: 删除特定章节

### 标记章节为完成
- **URL**: `/api/v1/courses/{course_pk}/chapters/{id}/mark_as_completed/`
- **方法**: POST
- **描述**: 标记章节为已完成
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

## 问题相关 (/api/v1/problems/)

### 获取问题列表
- **URL**: `/api/v1/problems/`
- **方法**: GET
- **描述**: 获取所有问题列表，可通过"type"参数筛选问题类型
- **查询参数**: 
  - `type`: 问题类型 ("algorithm" 或 "choice")
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "问题ID",
        "type": "问题类型",
        "chapter_title": "章节标题",
        "title": "问题标题",
        "content": "问题内容",
        "difficulty": "难度等级",
        "created_at": "创建时间",
        "updated_at": "更新时间"
      }
    ]
  }
  ```

### 创建问题
- **URL**: `/api/v1/problems/`
- **方法**: POST
- **描述**: 创建新问题
- **请求体**: 
  ```json
  {
    "type": "问题类型",
    "chapter": "章节ID",
    "title": "问题标题",
    "content": "问题内容",
    "difficulty": "难度等级"
  }
  ```
- **响应**:
  ```json
  {
    "id": "问题ID",
    "type": "问题类型",
    "chapter_title": "章节标题",
    "title": "问题标题",
    "content": "问题内容",
    "difficulty": "难度等级",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 获取特定问题详情
- **URL**: `/api/v1/problems/{id}/`
- **方法**: GET
- **描述**: 获取特定问题的详细信息
- **响应**:
  ```json
  {
    "id": "问题ID",
    "type": "问题类型",
    "chapter_title": "章节标题",
    "title": "问题标题",
    "content": "问题内容",
    "difficulty": "难度等级",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 更新问题
- **URL**: `/api/v1/problems/{id}/`
- **方法**: PUT/PATCH
- **描述**: 更新特定问题信息
- **请求体**: 
  ```json
  {
    "type": "问题类型",
    "chapter": "章节ID",
    "title": "问题标题",
    "content": "问题内容",
    "difficulty": "难度等级"
  }
  ```
- **响应**:
  ```json
  {
    "id": "问题ID",
    "type": "问题类型",
    "chapter_title": "章节标题",
    "title": "问题标题",
    "content": "问题内容",
    "difficulty": "难度等级",
    "created_at": "创建时间",
    "updated_at": "更新时间"
  }
  ```

### 删除问题
- **URL**: `/api/v1/problems/{id}/`
- **方法**: DELETE
- **描述**: 删除特定问题

### 标记问题为已解决
- **URL**: `/api/v1/problems/{id}/mark_as_solved/`
- **方法**: POST
- **描述**: 标记问题为已解决
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

## 提交相关 (/api/v1/submissions/)

### 获取提交记录列表
- **URL**: `/api/v1/submissions/`
- **方法**: GET
- **描述**: 获取所有提交记录列表
- **响应**:
  ```json
  {
    "count": "总数量",
    "next": "下一页链接",
    "previous": "上一页链接",
    "results": [
      {
        "id": "提交ID",
        "user": "用户ID",
        "username": "用户名",
        "problem": "问题ID",
        "problem_title": "问题标题",
        "code": "提交的代码",
        "language": "编程语言",
        "status": "评测状态",
        "execution_time": "执行时间(毫秒)",
        "memory_used": "内存使用(KB)",
        "output": "程序输出",
        "error": "错误信息",
        "created_at": "提交时间",
        "updated_at": "更新时间"
      }
    ]
  }
  ```

### 创建提交记录
- **URL**: `/api/v1/submissions/`
- **方法**: POST
- **描述**: 创建新的提交记录，可用于自由运行代码或提交算法题解答
- **请求体**: 
  ```json
  {
    "code": "提交的代码",
    "language": "编程语言",
    "problem_id": "问题ID(可选，用于提交算法题解答)"
  }
  ```
- **响应**:
  ```json
  {
    "id": "提交ID",
    "user": "用户ID",
    "username": "用户名",
    "problem": "问题ID",
    "problem_title": "问题标题",
    "code": "提交的代码",
    "language": "编程语言",
    "status": "评测状态",
    "execution_time": "执行时间(毫秒)",
    "memory_used": "内存使用(KB)",
    "output": "程序输出",
    "error": "错误信息",
    "created_at": "提交时间",
    "updated_at": "更新时间"
  }
  ```

### 获取特定提交详情
- **URL**: `/api/v1/submissions/{id}/`
- **方法**: GET
- **描述**: 获取特定提交记录的详细信息
- **响应**:
  ```json
  {
    "id": "提交ID",
    "user": "用户ID",
    "username": "用户名",
    "problem": "问题ID",
    "problem_title": "问题标题",
    "code": "提交的代码",
    "language": "编程语言",
    "status": "评测状态",
    "execution_time": "执行时间(毫秒)",
    "memory_used": "内存使用(KB)",
    "output": "程序输出",
    "error": "错误信息",
    "created_at": "提交时间",
    "updated_at": "更新时间"
  }
  ```

### 获取特定提交结果
- **URL**: `/api/v1/submissions/{id}/result/`
- **方法**: GET
- **描述**: 获取特定提交的评测结果
- **响应**:
  ```json
  {
    "id": "提交ID",
    "user": "用户ID",
    "username": "用户名",
    "problem": "问题ID",
    "problem_title": "问题标题",
    "code": "提交的代码",
    "language": "编程语言",
    "status": "评测状态",
    "execution_time": "执行时间(毫秒)",
    "memory_used": "内存使用(KB)",
    "output": "程序输出",
    "error": "错误信息",
    "created_at": "提交时间",
    "updated_at": "更新时间"
  }
  ```

## 学习进度相关 (/api/v1/progress/)

### 获取课程参与列表
- **URL**: `/api/v1/progress/enrollments/`
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

### 获取章节进度列表
- **URL**: `/api/v1/progress/chapter-progress/`
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

### 获取问题进度列表
- **URL**: `/api/v1/progress/problem-progress/`
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