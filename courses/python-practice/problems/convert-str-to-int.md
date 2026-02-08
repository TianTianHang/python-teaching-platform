---
title: "字符串转整数"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "str_to_int"
code_template:
  python: |
    def str_to_int(s):
        """
        将字符串转换为整数

        Args:
            s: 表示整数的字符串

        Returns:
            int: 转换后的整数
        """
        # 请在此实现你的代码
        # 提示：使用 int() 函数
        pass
test_cases:
  - input: '"123"'
    output: "123"
    is_sample: true
  - input: '"42"'
    output: "42"
    is_sample: true
  - input: '"0"'
    output: "0"
    is_sample: false
  - input: '"-10"'
    output: "-10"
    is_sample: false
  - input: '"1000"'
    output: "1000"
    is_sample: false
---
## 题目描述

编写一个函数，将表示整数的字符串转换为整数类型。

### 输入格式

一个表示整数的字符串 s。

### 输出格式

返回转换后的整数。

### 示例

**输入：**
```
"123"
```

**输出：**
```
123
```

### 提示

使用 `int()` 函数将字符串转换为整数：`int(s)`

### 注意事项

- 字符串必须是一个有效的整数表示
- 可以处理负数（如 "-10"）
- 空字符串或非数字字符串会导致转换错误（本题测试用例保证输入有效）

---
*本题目基于 Python 教学平台标准格式设计。*
