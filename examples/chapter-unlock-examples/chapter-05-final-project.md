---
title: "综合项目实战"
order: 5
unlock_conditions:
  type: "all"
  prerequisites: [3]
  unlock_date: "2025-04-01T00:00:00Z"
---

## 综合项目实战

### 章节概述

本章将通过一个综合项目，将前面学习的 Python 知识整合应用。项目是一个简单的任务管理系统，包含数据库操作、用户交互、文件读写等功能。

### 知识点 1：项目设计

**描述：**
任务管理系统将实现以下功能：
1. 添加任务
2. 查看任务列表
3. 标记任务完成
4. 删除任务
5. 保存任务到文件

**示例代码：**
```python
import json
from datetime import datetime

class Task:
    """任务类"""
    def __init__(self, title, description=""):
        self.title = title
        self.description = description
        self.completed = False
        self.created_at = datetime.now()

    def to_dict(self):
        """转换为字典"""
        return {
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建任务对象"""
        task = cls(data['title'], data['description'])
        task.completed = data['completed']
        task.created_at = datetime.fromisoformat(data['created_at'])
        return task

class TaskManager:
    """任务管理器"""
    def __init__(self):
        self.tasks = []

    def add_task(self, title, description=""):
        """添加任务"""
        task = Task(title, description)
        self.tasks.append(task)
        print(f"任务已添加：{title}")

    def list_tasks(self):
        """列出所有任务"""
        print("\n任务列表：")
        for i, task in enumerate(self.tasks, 1):
            status = "✓" if task.completed else "○"
            print(f"{i}. [{status}] {task.title}")
            if task.description:
                print(f"   {task.description}")

    def complete_task(self, index):
        """完成任务"""
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
            print(f"任务已完成：{self.tasks[index].title}")
        else:
            print("无效的任务编号")

    def delete_task(self, index):
        """删除任务"""
        if 0 <= index < len(self.tasks):
            deleted = self.tasks.pop(index)
            print(f"任务已删除：{deleted.title}")
        else:
            print("无效的任务编号")

    def save_tasks(self, filename):
        """保存任务到文件"""
        data = [task.to_dict() for task in self.tasks]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"任务已保存到 {filename}")

    def load_tasks(self, filename):
        """从文件加载任务"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
            print(f"任务已从 {filename} 加载")
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
```

**解释：**
这个项目展示了如何使用面向对象编程的思想来组织代码。`Task` 类表示单个任务，`TaskManager` 类管理所有的任务。项目还展示了文件操作、错误处理等重要的编程概念。

### 知识点 2：使用系统

**描述：**
演示如何使用这个任务管理系统。

**示例代码：**
```python
def main():
    """主函数"""
    manager = TaskManager()

    # 添加一些任务
    manager.add_task("学习 Python 基础")
    manager.add_task("完成课后练习", "需要完成第1-3章的所有练习")
    manager.add_task("准备项目作业")

    # 查看任务列表
    manager.list_tasks()

    # 完成任务
    manager.complete_task(0)
    manager.complete_task(1)

    # 再次查看任务列表
    manager.list_tasks()

    # 保存任务
    manager.save_tasks("tasks.json")

if __name__ == "__main__":
    main()
```

**解释：**
这个示例展示了如何创建一个完整的应用程序。程序包含主函数、类定义、用户交互等多个部分。通过这个项目，你将学到如何将各种 Python 知识点综合应用到实际项目中。

**关键要点：**
- 类和对象的设计原则
- 文件操作的实现
- 用户交互的处理
- 错误处理的重要性
- 模块化编程的思想

---

*本章内容基于 Python 教学平台标准格式设计。*
