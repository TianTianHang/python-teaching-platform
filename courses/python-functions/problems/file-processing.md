---
title: "文件处理"
type: "algorithm"
difficulty: 2
chapter: 3
time_limit: 1000
memory_limit: 256
solution_name:
  python: "process_file"
code_template:
  python: |
    def process_file(filename):
        """
        处理文本文件并统计信息

        Args:
            filename: 文件名（字符串）

        Returns:
            返回一个字典，包含以下键值对：
            - "lines": 总行数
            - "words": 总单词数
            - "chars": 总字符数（不含空格）
            - "non_empty_lines": 非空行数
        """
        # 请在此实现你的代码
        pass
test_cases:
  - input: "\"test.txt\""
    output: "{\"lines\": 3, \"words\": 6, \"chars\": 20, \"non_empty_lines\": 2}"
    is_sample: true
  - input: "\"empty.txt\""
    output: "{\"lines\": 0, \"words\": 0, \"chars\": 0, \"non_empty_lines\": 0}"
    is_sample: false
  - input: "\"single.txt\""
    output: "{\"lines\": 1, \"words\": 3, \"chars\": 11, \"non_empty_lines\": 1}"
    is_sample: false
unlock_conditions:
  type: "prerequisite"
  prerequisites: ["factorial-calculator.md", "module-import.md"]
---
## 题目描述

编写一个函数，读取文本文件并统计文件的基本信息，包括总行数、总单词数、总字符数（不含空格）和非空行数。

### 输入格式

函数接收一个参数：
- `filename`：文件名（字符串）

### 输出格式

返回一个字典，包含以下键值对：
- `"lines"`：总行数
- `"words"`：总单词数
- `"chars"`：总字符数（不含空格）
- `"non_empty_lines"`：非空行数

### 示例

**示例1：**
假设文件 `test.txt` 内容为：
```
Hello world
Python编程

This is a test
```

```python
process_file("test.txt")
# 返回：{"lines": 3, "words": 6, "chars": 20, "non_empty_lines": 2}
```

**解释：**
- 总行数：3（包含空行）
- 总单词数：6（"Hello", "world", "Python编程", "This", "is", "a", "test"）
- 总字符数：20（不含空格和换行符）
- 非空行数：2（第2行是空行）

**示例2：**
空文件 `empty.txt`：
```python
process_file("empty.txt")
# 返回：{"lines": 0, "words": 0, "chars": 0, "non_empty_lines": 0}
```

**示例3：**
单行文件 `single.txt` 内容为：
```
Hello Python World
```

```python
process_file("single.txt")
# 返回：{"lines": 1, "words": 3, "chars": 11, "non_empty_lines": 1}
```

### 提示

1. 使用 `open()` 函数打开文件
2. 使用 `with` 语句确保文件正确关闭
3. 使用 `readlines()` 或逐行读取
4. 使用 `split()` 方法分割单词
5. 使用 `strip()` 去除首尾空白
6. 使用 `replace()` 去除空格

**基础实现：**
```python
def process_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)
        total_words = 0
        total_chars = 0
        non_empty_lines = 0

        for line in lines:
            # 统计单词数
            words = line.split()
            total_words += len(words)

            # 统计字符数（去除空格和换行符）
            chars = line.replace(' ', '').replace('\n', '').replace('\t', '')
            total_chars += len(chars)

            # 统计非空行
            if line.strip():
                non_empty_lines += 1

        return {
            "lines": total_lines,
            "words": total_words,
            "chars": total_chars,
            "non_empty_lines": non_empty_lines
        }

    except FileNotFoundError:
        return {
            "lines": 0,
            "words": 0,
            "chars": 0,
            "non_empty_lines": 0
        }
```

**更简洁的实现：**
```python
def process_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return {
            "lines": len(lines),
            "words": sum(len(line.split()) for line in lines),
            "chars": sum(len(line.replace(' ', '').replace('\n', ''))
                        for line in lines),
            "non_empty_lines": sum(1 for line in lines if line.strip())
        }

    except FileNotFoundError:
        return {"lines": 0, "words": 0, "chars": 0, "non_empty_lines": 0}
```

### 注意事项

- 文件编码：使用 UTF-8 编码读取文件
- 异常处理：处理文件不存在的情况
- 空行判断：使用 `strip()` 后检查长度
- 单词分割：使用 `split()` 自动处理多个空格
- 字符统计：需要去除空格、换行符、制表符等空白字符
- 文件操作：始终使用 `with` 语句确保文件正确关闭

### 文件操作基础

**打开文件的模式：**
- `'r'`：只读模式（默认）
- `'w'`：写入模式（覆盖）
- `'a'`：追加模式
- `'rb'`：二进制读取
- `'wb'`：二进制写入

**读取文件的方法：**
```python
# 方法1：读取全部内容
with open('file.txt', 'r') as f:
    content = f.read()

# 方法2：读取所有行
with open('file.txt', 'r') as f:
    lines = f.readlines()

# 方法3：逐行读取
with open('file.txt', 'r') as f:
    for line in f:
        print(line.strip())
```

### 实际应用

文件处理在实际开发中非常常见：

1. **日志分析**：
   - 统计错误日志数量
   - 分析访问频率
   - 提取关键信息

2. **数据导入**：
   - 读取CSV文件
   - 解析配置文件
   - 导入文本数据

3. **文本处理**：
   - 词频统计
   - 内容搜索
   - 格式转换

4. **系统管理**：
   - 分析服务器日志
   - 监控文件变化
   - 生成报告

### 进阶挑战

如果你想挑战更高级的内容：

1. **支持命令行参数**：
```python
import sys

if len(sys.argv) > 1:
    filename = sys.argv[1]
    result = process_file(filename)
    print(result)
```

2. **处理多个文件**：
```python
def process_multiple_files(filenames):
    results = {}
    for filename in filenames:
        results[filename] = process_file(filename)
    return results
```

3. **生成报告**：
```python
def generate_report(filename):
    stats = process_file(filename)
    report = f"""
    文件统计报告：{filename}
    ================================
    总行数：{stats['lines']}
    总单词数：{stats['words']}
    总字符数：{stats['chars']}
    非空行数：{stats['non_empty_lines']}
    """
    return report
```

4. **处理大文件（逐行读取，不一次性加载到内存）**：
```python
def process_large_file(filename):
    lines = 0
    words = 0
    chars = 0
    non_empty = 0

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            lines += 1
            words += len(line.split())
            chars += len(line.replace(' ', '').replace('\n', ''))
            if line.strip():
                non_empty += 1

    return {"lines": lines, "words": words,
            "chars": chars, "non_empty_lines": non_empty}
```

### 测试你的代码

创建测试文件：
```python
# 创建测试文件
with open('test.txt', 'w', encoding='utf-8') as f:
    f.write('Hello world\n')
    f.write('Python编程\n')
    f.write('\n')
    f.write('This is a test\n')

# 测试
result = process_file('test.txt')
print(result)
# 预期输出：{'lines': 4, 'words': 6, 'chars': 20, 'non_empty_lines': 3}
```

---
*本题目基于 Python 教学平台标准格式设计。*
