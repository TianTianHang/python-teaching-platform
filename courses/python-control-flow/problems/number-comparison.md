---
title: "数字比较与判断"
type: "algorithm"
difficulty: 1
chapter: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "compare_numbers"
code_template:
  python: |
    def compare_numbers(a, b):
        """
        比较两个数字的大小关系

        Args:
            a: 第一个数字
            b: 第二个数字

        Returns:
            返回比较结果字符串，可能是：
            - "a > b"：a大于b
            - "a < b"：a小于b
            - "a == b"：a等于b
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "[10, 5]"
    output: "\"a > b\""
    is_sample: true
  - input: "[3, 7]"
    output: "\"a < b\""
    is_sample: false
  - input: "[42, 42]"
    output: "\"a == b\""
    is_sample: false
---
## 题目描述

编写一个函数，比较两个数字的大小关系。

### 输入格式

函数接收两个参数：
- `a`：第一个数字（整数或浮点数）
- `b`：第二个数字（整数或浮点数）

### 输出格式

返回一个字符串，表示比较结果：
- 当`a > b`时，返回`"a > b"`
- 当`a < b`时，返回`"a < b"`
- 当`a == b`时，返回`"a == b"`

### 示例

**示例1：a大于b**
```python
compare_numbers(10, 5)
# 返回："a > b"
```

**示例2：a小于b**
```python
compare_numbers(3, 7)
# 返回："a < b"
```

**示例3：a等于b**
```python
compare_numbers(42, 42)
# 返回："a == b"
```

### 提示

1. 使用if-elif-else结构进行条件判断
2. 直接使用比较运算符（`>`、`<`、`==`）
3. 考虑浮点数的精度问题（虽然本题比较简单）

**示例代码：**
```python
def compare_numbers(a, b):
    if a > b:
        return "a > b"
    elif a < b:
        return "a < b"
    else:
        return "a == b"
```

### 注意事项
- 处理所有三种情况：大于、小于、等于
- 函数应该返回字符串，而不是直接打印
- 不需要考虑a和b为None的特殊情况

---
*本题目基于 Python 教学平台标准格式设计。*
