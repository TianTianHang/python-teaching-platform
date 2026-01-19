---
title: "列表统计"
type: "algorithm"
difficulty: 2
chapter: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "calculate_statistics"
code_template:
  python: |
    def calculate_statistics(numbers):
        """
        计算列表的统计信息

        Args:
            numbers: 数字列表（列表元素都是整数）

        Returns:
            返回一个字典，包含以下键值对：
            - "max": 最大值
            - "min": 最小值
            - "avg": 平均值（保留2位小数）
            - "sum": 总和
            - "count": 元素个数
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "[1, 2, 3, 4, 5]"
    output: "{\"max\": 5, \"min\": 1, \"avg\": 3.0, \"sum\": 15, \"count\": 5}"
    is_sample: true
  - input: "[10, 20, 30]"
    output: "{\"max\": 30, \"min\": 10, \"avg\": 20.0, \"sum\": 60, \"count\": 3}"
    is_sample: false
  - input: "[-5, 0, 5, 10]"
    output: "{\"max\": 10, \"min\": -5, \"avg\": 2.5, \"sum\": 10, \"count\": 4}"
    is_sample: false
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["list-indexing.md", "list-slicing.md"]
---
## 题目描述

编写一个函数，计算列表的统计信息。

### 输入格式

函数接收一个参数：
- `numbers`：数字列表（列表元素都是整数）

### 输出格式

返回一个字典，包含以下键值对：
- `"max"`：最大值
- `"min"`：最小值
- `"avg"`：平均值（保留2位小数）
- `"sum"`：总和
- `"count"`：元素个数

### 示例

**示例1：**
```python
calculate_statistics([1, 2, 3, 4, 5])
# 返回：{"max": 5, "min": 1, "avg": 3.0, "sum": 15, "count": 5}
```

**示例2：**
```python
calculate_statistics([10, 20, 30])
# 返回：{"max": 30, "min": 10, "avg": 20.0, "sum": 60, "count": 3}
```

### 提示

1. 使用内置函数`max()`、`min()`、`sum()`计算统计值
2. 平均值使用总和除以个数，注意保留2位小数
3. 元素个数使用`len()`函数
4. 使用字典创建结果字典

**示例代码：**
```python
def calculate_statistics(numbers):
    if not numbers:  # 处理空列表情况
        return {"max": None, "min": None, "avg": None, "sum": 0, "count": 0}

    result = {
        "max": max(numbers),
        "min": min(numbers),
        "avg": sum(numbers) / len(numbers),
        "sum": sum(numbers),
        "count": len(numbers)
    }
    return result

# 更简洁的实现
def calculate_statistics(numbers):
    if not numbers:
        return {"max": None, "min": None, "avg": None, "sum": 0, "count": 0}

    return {
        "max": max(numbers),
        "min": min(numbers),
        "avg": round(sum(numbers) / len(numbers), 2),
        "sum": sum(numbers),
        "count": len(numbers)
    }
```

### 注意事项
- 处理空列表的特殊情况
- 平均值使用`round()`函数保留2位小数
- 返回的字典键必须是字符串类型
- 考虑使用Python内置函数提高效率

---
*本题目基于 Python 教学平台标准格式设计。*
