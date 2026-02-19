---
title: "列表转字符串"
type: "algorithm"
chapter: 1
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "list_to_str"
code_template:
  python: |
    def list_to_str(items, separator):
        """
        将字符串列表连接成一个字符串

        Args:
            items: 字符串列表
            separator: 分隔符

        Returns:
            str: 连接后的字符串
        """
        # 请在此实现你的代码
        # 提示：使用 join() 方法
        pass
test_cases:
  - input: '["hello","world","python"],","]'
    output: '"hello,world,python"'
    is_sample: true
  - input: '["a","b","c"],"-"]'
    output: '"a-b-c"'
    is_sample: true
  - input: '["x","y"],""'
    output: '"xy"'
    is_sample: false
  - input: '["single"],","]'
    output: '"single"'
    is_sample: false
  - input: '[],"-"]'
    output: '""'
    is_sample: false
---
## 题目描述

编写一个函数，将字符串列表用指定的分隔符连接成一个字符串。

### 输入格式

[字符串列表 items, 分隔符 separator]。

### 输出格式

返回连接后的字符串。

### 示例

**输入：**
```
[["hello", "world", "python"], ","]
```

**输出：**
```
"hello,world,python"
```

### 提示

:::tip{title="提示" state="collapsed"}
使用字符串的 `join()` 方法：`separator.join(items)`
:::

### 注意事项

- 空列表 join 后得到空字符串
- 空分隔符会直接连接所有元素
- 单元素列表返回该元素本身
- join() 方法要求列表中的元素都是字符串类型

---
*本题目基于 Python 教学平台标准格式设计。*
