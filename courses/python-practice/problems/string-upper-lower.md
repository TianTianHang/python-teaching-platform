---
title: "大小写转换"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "convert_case"
code_template:
  python: |
    def convert_case(s, to_upper):
        """
        转换字符串的大小写

        Args:
            s: 一个字符串
            to_upper: 布尔值，True 转大写，False 转小写

        Returns:
            str: 转换后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 upper() 或 lower() 方法
        pass
test_cases:
  - input: '["hello",true]'
    output: '"HELLO"'
    is_sample: true
  - input: '["WORLD",false]'
    output: '"world"'
    is_sample: true
  - input: '["Python",true]'
    output: '"PYTHON"'
    is_sample: false
  - input: '["ABC",false]'
    output: '"abc"'
    is_sample: false
  - input: '["123",true]'
    output: '"123"'
    is_sample: false
---
## 题目描述

编写一个函数，根据参数将字符串转换为大写或小写。

### 输入格式

[字符串 s, 布尔值 to_upper]，to_upper 为 true 时转大写，false 时转小写。

### 输出格式

返回转换后的字符串。

### 示例

**输入：**
```
["hello", true]
```

**输出：**
```
"HELLO"
```

### 提示

- `s.upper()` 将字符串转为全大写
- `s.lower()` 将字符串转为全小写

### 注意事项

- 数字和符号不受大小写转换影响
- 使用 if/else 语句根据 to_upper 参数选择合适的方法

---
*本题目基于 Python 教学平台标准格式设计。*
