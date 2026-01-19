---
title: "列表方法"
type: "choice"
difficulty: 2
chapter: 1
is_multiple_choice: false
options:
  A: "[1, 2, 3, 4]"
  B: "[1, 3, 4]"
  C: "[1, 2, 3]"
  D: "[1, 2, 3, 3, 4]"
correct_answer: "C"
---
## 题目描述

执行以下Python代码后，输出结果是什么？

```python
numbers = [1, 2, 3, 4]
numbers.remove(4)
numbers.append(3)
print(numbers)
```

### 题目内容

A. [1, 2, 3, 4]
B. [1, 3, 4]
C. [1, 2, 3]
D. [1, 2, 3, 3, 4]

### 解析

**正确答案：C**

**详细解析：**

这道题考查列表方法`remove()`和`append()`的使用。

**代码执行分析：**

1. `numbers = [1, 2, 3, 4]`：创建列表
2. `numbers.remove(4)`：
   - `remove()`删除列表中第一个匹配的值
   - 删除4后，列表变为[1, 2, 3]
3. `numbers.append(3)`：
   - `append()`在列表末尾添加元素
   - 添加3后，列表变为[1, 2, 3, 3]
4. 输出：[1, 2, 3, 3]

**重要区别：**
- `remove(value)`：按值删除
- `pop(index)`：按索引删除并返回值
- `append(value)`：在末尾添加

**选项分析：**
- **选项 A**：原列表，没有进行任何操作
- **选项 B**：删除了2但没有添加3
- **选项 C**：删除了4但没有添加3
- **选项 D（正确）**：先删除4，再添加3，得到[1, 2, 3, 3]

**其他常用列表方法：**
```python
# 插入元素
numbers.insert(0, 0)  # 在索引0位置插入0

# 扩展列表
numbers.extend([4, 5])  # 添加多个元素

# 计数
count = numbers.count(3)  # 统计3出现的次数

# 排序
numbers.sort()  # 升序排序
numbers.sort(reverse=True)  # 降序排序
```

### 相关知识点
- list.remove()方法
- list.append()方法
- 列表方法的使用

---
*本题基于 Python 教学平台标准格式设计。*
