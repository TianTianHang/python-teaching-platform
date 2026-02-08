---
title: "字符串填充"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "pad_string"
code_template:
  python: |
    def pad_string(s, width):
        """
        将字符串填充到指定宽度（左侧补0）

        Args:
            s: 一个字符串（数字字符串）
            width: 目标宽度

        Returns:
            str: 填充后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 zfill() 或 rjust() 方法
        pass
test_cases:
  - input: '["42",5]'
    output: '"00042"'
    is_sample: true
  - input: '["123",6]'
    output: '"000123"'
    is_sample: true
  - input: '["99",4]'
    output: '"0099"'
    is_sample: false
  - input: '["5",3]'
    output: '"005"'
    is_sample: false
  - input: '["123",3]'
    output: '"123"'
    is_sample: false
---
## 题目描述

编写一个函数，将字符串填充到指定宽度，如果字符串长度小于宽度，在左侧补 0。

### 输入格式

[字符串 s, 目标宽度 width]。

### 输出格式

返回填充后的字符串。

### 示例

**输入：**
```
["42", 5]
```

**输出：**
```
"00042"
```

### 提示

- 方法 1：使用 `zfill()` 方法：`s.zfill(width)`
- 方法 2：使用 `rjust()` 方法：`s.rjust(width, '0')`

### 注意事项

- 如果字符串长度已经大于或等于 width，返回原字符串
- zfill() 是 "zero fill" 的缩写，专门用于左侧补 0
- 这个方法常用于格式化数字（如序号、日期等）

---
*本题目基于 Python 教学平台标准格式设计。*
