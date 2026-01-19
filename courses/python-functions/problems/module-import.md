---
title: "模块导入"
type: "choice"
difficulty: 1
chapter: 3
is_multiple_choice: false
options:
  A: "math.sqrt(16)"
  B: "sqrt(16)"
  C: "math.sqrt(16) 和 sqrt(16)"
  D: "都不行"
correct_answer: "A"
---
## 题目描述

执行以下代码后，如何正确调用 `sqrt` 函数？

```python
import math
```

### 题目内容

执行以下代码后，如何正确调用 `sqrt` 函数？

```python
import math
```

A. `math.sqrt(16)`

B. `sqrt(16)`

C. `math.sqrt(16)` 和 `sqrt(16)`

D. 都不行

### 正确答案

A

### 详细解析

**正确答案：A**

**解析：**

这个题目考察的是**模块导入**的不同方式及其对应的调用方法。

**代码分析：**

```python
import math
```

- 使用 `import math` 导入整个 `math` 模块
- 模块中的函数需要通过 `模块名.函数名()` 的方式调用
- 调用方式：`math.sqrt(16)`

**各选项分析：**

- ✅ **A. `math.sqrt(16)`** - 正确
  - `import math` 后，使用 `math.sqrt()` 调用函数
  - 输出：`4.0`

- ❌ **B. `sqrt(16)`** - 错误
  - 直接使用 `sqrt()` 会报 `NameError`
  - 因为 `sqrt` 没有被导入到当前命名空间

- ❌ **C. `math.sqrt(16)` 和 `sqrt(16)`** - 错误
  - `sqrt(16)` 不可用
  - 只有 `math.sqrt(16)` 可以使用

- ❌ **D. 都不行** - 错误
  - `math.sqrt(16)` 是正确的调用方式

**不同的导入方式：**

```python
# 方式1：导入整个模块
import math
result = math.sqrt(16)  # 正确：4.0
# result = sqrt(16)    # 错误：NameError

# 方式2：导入模块并使用别名
import math as m
result = m.sqrt(16)     # 正确：4.0
# result = math.sqrt(16)  # 错误：math 未定义

# 方式3：从模块中导入特定函数
from math import sqrt
result = sqrt(16)       # 正确：4.0
# result = math.sqrt(16)  # 错误：math 未定义

# 方式4：从模块中导入特定函数并使用别名
from math import sqrt as square_root
result = square_root(16)  # 正确：4.0

# 方式5：导入模块中的所有内容（不推荐）
from math import *
result = sqrt(16)       # 正确：4.0
result = pow(2, 3)      # 正确：8.0
```

**导入方式对比：**

| 导入方式 | 调用方式 | 优点 | 缺点 |
|---------|---------|------|------|
| `import math` | `math.sqrt()` | 命名清晰，避免冲突 | 每次都要写模块名 |
| `import math as m` | `m.sqrt()` | 简洁且清晰 | 需要记住别名 |
| `from math import sqrt` | `sqrt()` | 调用简洁 | 可能命名冲突 |
| `from math import *` | `sqrt()` | 最简洁 | 强烈不推荐 |

**完整示例：**

```python
# 方式1：import math
import math
print(math.pi)        # 3.141592653589793
print(math.sqrt(16))  # 4.0
print(math.pow(2, 3)) # 8.0

# 方式2：import math as m
import math as m
print(m.pi)        # 3.141592653589793
print(m.sqrt(16))  # 4.0

# 方式3：from math import sqrt, pi
from math import sqrt, pi
print(pi)      # 3.141592653589793
print(sqrt(16))  # 4.0
# print(math.sqrt(16))  # NameError: math 未定义
```

**为什么推荐使用 `import math`？**

1. **命名清晰**：
   ```python
   import math
   math.sqrt(16)  # 一眼看出是 math 模块的 sqrt 函数
   ```

2. **避免命名冲突**：
   ```python
   # 可能冲突
   from math import sin
   from numpy import sin  # 覆盖了上面的 sin

   # 不会冲突
   import math
   import numpy as np
   math.sin(x)
   np.sin(x)
   ```

3. **代码可读性**：
   ```python
   import random
   import math

   # 清楚知道每个函数来自哪个模块
   x = random.random()
   y = math.sqrt(x)
   ```

**何时使用 `from module import name`？**

1. **常用函数**：
   ```python
   from math import sqrt, pi, sin
   # 这些函数使用频率很高，直接导入更方便
   ```

2. **模块名很长**：
   ```python
   from matplotlib import pyplot as plt
   # 比 import matplotlib.pyplot as plt 更清晰
   ```

3. **明确知道不会冲突**：
   ```python
   from datetime import datetime
   # datetime 类很常用，直接导入方便
   ```

**避免使用 `from module import *`：**

```python
# 不推荐
from math import *

# 问题1：不知道导入了什么
# 问题2：可能覆盖已有的变量
# 问题3：代码可读性差

# 推荐
import math
# 或明确指定要导入的内容
from math import sqrt, pi, sin
```

**实际应用示例：**

```python
# 示例1：随机数生成
import random

number = random.randint(1, 100)  # 1-100的随机整数
choice = random.choice(['苹果', '香蕉', '橙子'])  # 随机选择
print(random.random())  # 0.0-1.0的随机浮点数

# 示例2：日期时间处理
from datetime import datetime

now = datetime.now()
print(now.year)
print(now.month)
print(now.day)

# 示例3：路径处理
from pathlib import Path

file_path = Path("documents") / "python" / "lesson.md"
if file_path.exists():
    print(f"文件大小: {file_path.stat().st_size} 字节")
```

### 相关知识点

- **模块导入**：使用 `import` 语句导入模块
- **模块调用**：通过 `模块名.函数名()` 调用模块函数
- **模块别名**：使用 `as` 关键字为模块指定别名
- **从模块导入**：使用 `from module import name` 导入特定内容

### 进阶思考

**为什么有这么多导入方式？**

不同的导入方式适应不同的使用场景：

1. **`import module`**：适用于使用模块的多个功能
   ```python
   import math
   math.sqrt(16)
   math.sin(3.14)
   math.cos(3.14)
   math.pi
   ```

2. **`from module import name`**：适用于只使用模块的一两个功能
   ```python
   from math import sqrt
   result = sqrt(16)  # 只用到 sqrt
   ```

3. **`import module as alias`**：适用于模块名很长或需要避免冲突
   ```python
   import matplotlib.pyplot as plt
   plt.plot([1, 2, 3], [4, 5, 6])
   ```

**导入的最佳实践：**

```python
# 1. 标准库
import math
import random
from datetime import datetime

# 2. 第三方库
import numpy as np
import pandas as pd

# 3. 本地模块
import mymodule
from mypackage import helper

# 顺序：标准库 → 第三方库 → 本地模块
```

**命名约定：**
- `numpy` → `np`
- `pandas` → `pd`
- `matplotlib.pyplot` → `plt`
- `seaborn` → `sns`

这些都是社区的普遍约定，保持一致可以提高代码可读性。

---
*本题目基于 Python 教学平台标准格式设计。*
