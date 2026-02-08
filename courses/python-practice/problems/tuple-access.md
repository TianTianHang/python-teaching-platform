---
title: "访问元组元素"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "access_tuple"
code_template:
  python: |
    def access_tuple(t, index):
        """
        访问元组中指定位置的元素

        Args:
            t: 一个元组
            index: 要访问的索引位置

        Returns:
            该位置的元素
        """
        # 请在此实现你的代码
        # 提示：使用 t[index] 语法
        pass
test_cases:
  - input: '[(1,2,3,4,5),2]'
    output: "3"
    is_sample: true
  - input: '[("a","b","c"),0]'
    output: '"a"'
    is_sample: true
  - input: '[(10,20,30),1]'
    output: "20"
    is_sample: false
  - input: '[(42,),0]'
    output: "42"
    is_sample: false
  - input: '[(1,2,3),2]'
    output: "3"
    is_sample: false
---
## 题目描述

编写一个函数，访问元组中指定位置的元素。

### 输入格式

[元组 t, 索引 index]。

### 输出格式

返回元组中指定位置的元素。

### 示例

**输入：**
```
[(1, 2, 3, 4, 5), 2]
```

**输出：**
```
3
```

### 提示

使用索引访问元组元素：`t[index]`

### 注意事项

- 索引从 0 开始
- 索引必须在有效范围内（0 到 len(t)-1）
- 元组是不可变的，但可以读取元素
- 本题目测试用例保证索引是有效的

---
*本题目基于 Python 教学平台标准格式设计。*
