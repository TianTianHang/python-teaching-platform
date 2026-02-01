# 课程内容创作指南

本文档为课程内容创作者提供详细的指导，帮助你编写高质量的 Python 课程内容。

## 📋 目录

- [创作理念](#创作理念)
- [课程设计原则](#课程设计原则)
- [新格式入门](#新格式入门)
- [章节编写指南](#章节编写指南)
- [算法题设计指南](#算法题设计指南)
- [选择题设计指南](#选择题设计指南)
- [模板使用指南](#模板使用指南)
- [质量检查清单](#质量检查清单)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [进阶技巧](#进阶技巧)
- [资源推荐](#资源推荐)

## 🎯 创作理念

### 以学员为中心

始终从学员的角度思考：
- 他们已经掌握了什么？
- 他们希望学到什么？
- 学习过程中的难点在哪里？
- 如何帮助他们更好地理解？

### 循序渐进

- 从简单到复杂
- 从具体到抽象
- 从理论到实践
- 每个知识点都要建立在之前的基础上

### 实用性优先

- 提供实际的应用场景
- 结合真实项目案例
- 强调编程实践
- 注重解决问题能力的培养

## 🏗️ 课程设计原则

### 课程结构设计

#### 合理的章节划分
- 每章 1-3 小时的学习内容
- 每章 4-6 个知识点
- 每章 2-4 个练习题
- 章节之间要有明确的递进关系

#### 内容深浅安排
1. **基础阶段**（30%）：概念讲解、语法介绍
2. **实践阶段**（40%）：示例演示、动手练习
3. **进阶阶段**（20%）：深入理解、扩展应用
4. **总结阶段**（10%）：知识点串联、综合应用

### 学习路径设计

#### 先决条件检查
```yaml
prerequisites: []
# 或者
prerequisites: ["Python基础"]
```

#### 学习目标明确
- 可衡量的学习目标
- 明确的应用场景
- 具体的能力提升

### 难度梯度设计

#### 简单题目（难度 1）
- 直接应用知识点
- 单步解决问题
- 代码量 < 20 行
- 时间限制 2000ms

#### 中等题目（难度 2）
- 需要多步思考
- 简单算法设计
- 代码量 20-50 行
- 时间限制 2000ms

#### 困难题目（难度 3）
- 综合运用多个概念
- 复杂算法实现
- 考虑边界情况
- 代码量 50-100 行
- 时间限制 3000ms

## 🚀 新格式入门

### 目录结构理解

```
my-course/
├── course.md              # 课程元数据和简介
├── chapters/              # 章节目录
│   ├── chapter-01-intro.md
│   ├── chapter-02-basics.md
│   └── chapter-03-advanced.md
└── problems/              # 题目目录
    ├── hello-world.md
    ├── list-operations.md
    └── dict-operations.md
```

### 文件命名规范

- **课程文件夹**: `kebab-case`（如 `python-basics`）
- **章节文件**: `chapter-XX-slug.md`（如 `chapter-01-intro.md`）
- **题目文件**: `slug.md`（如 `two-sum.md`）
- **课程元数据**: `course.md`（必需）

### YAML Frontmatter 基础

#### 课程文件
```yaml
---
title: "Python编程入门"
description: "从零开始学习Python编程，掌握基础语法和数据结构。"
order: 1
difficulty: 1
prerequisites: []
tags: ["python", "基础"]
---
```

#### 章节文件
```yaml
---
title: "Python基础语法"
order: 1
---
```

#### 题目文件
```yaml
---
title: "Hello World"
type: "algorithm"
difficulty: 1
time_limit: 1000
memory_limit: 256
solution_name:
  python: "helloWorld"
test_cases:
  - input: "\"Hello, Python!\""
    output: "\"Hello, Python!\""
    is_sample: true
---
```

## 📖 章节编写指南

### 创建章节文件

1. **创建文件**
   ```bash
   touch chapters/chapter-01-introduction.md
   ```

2. **添加 YAML Frontmatter**
   ```yaml
   ---
   title: "章节标题"
   order: 1
   # 可选：章节解锁条件（控制学生访问权限）
   # unlock_conditions:
   #   type: "prerequisite"  # 解锁类型：prerequisite, date, all, none
   #   prerequisites: [1]     # 前置章节 order 列表（整数）
   #   unlock_date: "2025-03-01T00:00:00Z"  # ISO 8601 格式的解锁日期
   ---
   ```

3. **编写内容**
   ```markdown
   ## 章节标题

   ### 章节概述
   概述内容...

   ### 知识点 1：[知识点名称]

   **描述：**
   详细描述...

   **示例代码：**
   ```python
   # 代码示例
   ```
   ```

### 章节标题设计

#### 命名原则
- 使用中文标题
- 4-10 个字为宜
- 准确反映内容主题
- 符合学习进度

#### 示例
```markdown
## 章节：Python基础语法
## 章节：控制流语句
## 章节：函数与模块
## 章节：面向对象编程
```

### 知识点编写技巧

#### 1. 概念讲解
- 用平实的语言解释
- 避免过于学术化的表述
- 结合生活实例说明
- 图文并茂更佳

#### 2. 代码示例
```markdown
**示例代码：**
```python
# 使用变量
name = "张三"
age = 25
height = 1.75

# 格式化字符串
message = f"我的名字是{name}，今年{age}岁，身高{height}米"
print(message)
```
```

#### 3. 解释说明
- 解释代码的作用
- 说明关键语法点
- 指出常见误区
- 提供扩展建议

## 💻 算法题设计指南

### 创建算法题文件

1. **创建文件**
   ```bash
   touch problems/two-sum.md
   ```

2. **添加 YAML Frontmatter**
   ```yaml
   ---
   title: "两数之和"
   type: "algorithm"
   difficulty: 1
   time_limit: 1000
   memory_limit: 256
   solution_name:
     python: "twoSum"
   test_cases:
     - input: "[[2,7,11,15],9]"
       output: "[0,1]"
       is_sample: true
     - input: "[[3,2,4],6]"
       output: "[1,2]"
       is_sample: false
   ---
   ```

3. **编写题目内容**
   ```markdown
   ## 题目描述

   编写一个函数...
   ```

### 题目描述设计

#### 描述要求
1. **清晰明确**：避免歧义
2. **背景引入**：有实际应用场景
3. **输入输出明确**：格式要求清晰
4. **示例完整**：包含边界情况

#### 示例对比

**不好的描述：**
```
**题目描述：**
写一个函数，求数组的和。
```

**好的描述：**
```
**题目描述：**
给定一个整数数组 nums，编写一个函数返回数组所有元素的和。

**输入格式：**
一行，数组元素用逗号分隔，如：1,2,3,4,5

**输出格式：**
一个整数，表示数组元素的和

**示例：**
输入：
```
1,2,3,4,5
```
输出：
```
15
```
```

### 测试用例设计原则

#### 测试用例数量
- 简单题：3-5 个
- 中等题：5-10 个
- 困难题：10-20 个

#### 测试用例类型

1. **常规用例**：正常输入
2. **边界用例**：最大/最小值、空值
3. **异常用例**：错误输入、特殊情况
4. **性能用例**：大数据量测试

#### 示例测试用例

```yaml
test_cases:
  - input: "[2,7,11,15]"
    output: "[0,1]"
    is_sample: true
  - input: "[3,2,4]"
    output: "[1,2]"
    is_sample: false
  - input: "[3,3]"
    output: "[0,1]"
    is_sample: false
  - input: "[]"
    output: "[]"
    is_sample: false
  - input: "[1000000,1000000]"
    output: "[0,1]"
    is_sample: false
```

## 📝 选择题设计指南

### 创建选择题文件

1. **创建文件**
   ```bash
   touch/problems/variable-naming.md
   ```

2. **添加 YAML Frontmatter**
   ```yaml
   ---
   title: "Python变量命名规则"
   type: "choice"
   difficulty: 1
   is_multiple_choice: false
   options:
     A: "123abc"
     B: "my-variable"
     C: "_private_var"
     D: "class"
   correct_answer: "C"
   ---
   ```

3. **编写题目内容**
   ```markdown
   ## 题目描述

   以下哪个是合法的 Python 变量名？

   ### 题目内容
   - A: 123abc
   - B: my-variable
   - C: _private_var
   - D: class

   ### 解析
   [详细解析]
   ```

### 选项设计技巧

#### 干扰项类型

1. **概念混淆**
```yaml
A: "列表和数组是同一个概念"
B: "列表是动态的，数组是静态的"  # 正确
C: "只能存储基本数据类型"
D: "长度固定不可变"
```

2. **语法错误**
```yaml
A: "def function(a,b):"
B: "def function(a, b):"  # 正确
C: "def function(a,b ):"
D: "def function( a,b):"
```

### 解答设计要点

#### 解答要求
1. **明确指出正确答案**
2. **解释为什么正确**
3. **说明为什么错误**
4. **提供补充知识**

#### 示例解答

```markdown
**正确答案：** B

**解析：**
- A 错误：列表和数组是不同的数据结构，列表是 Python 内置的，数组需要 numpy 库
- B 正确：列表是动态的，长度可变；数组是静态的，长度固定
- C 错误：列表可以存储任意类型的对象，不限于基本数据类型
- D 错误：列表是 Python 内置的，不需要额外安装库

补充：在需要高性能数值计算时，可以使用 numpy 的数组类型。
```

## 📝 模板使用指南

### 快速开始

#### 1. 复制模板
```bash
# 复制整个模板目录
cp -r /path/to/_templates /path/to/your-course
```

#### 2. 重命名文件
```bash
# 重命名课程文件夹
mv your-course python-basics

# 重命名章节文件
mv chapters/chapter-00-template.md chapters/chapter-01-intro.md

# 重命名题目文件
mv problems/algorithm-problem-template.md problems/hello-world.md
```

#### 3. 编辑内容
```bash
# 编辑课程元数据
vim course.md

# 编辑章节内容
vim chapters/chapter-01-intro.md

# 编辑题目内容
vim problems/hello-world.md
```

### 模板文件说明

#### 课程模板 (`course.md`)
- 包含课程标题、描述、学习目标
- YAML frontmatter 有完整的元数据
- 适合作为课程介绍页

#### 章节模板 (`chapters/chapter-00-template.md`)
- 包含章节概述和知识点结构
- 预设了知识点格式和代码示例位置
- 可以直接重命名和编辑

#### 算法题模板 (`problems/algorithm-problem-template.md`)
- 包含完整的算法题结构
- YAML frontmatter 包含所有必要字段
- 提供了题目描述模板和注意事项

#### 选择题模板 (`problems/choice-problem-template.md`)
- 包含选择题的标准格式
- 提供 4 个选项的模板
- 包含详细的解析要求

### 模板自定义

#### 修改默认值
```yaml
# 在 course.md 中
title: "你的课程标题"
description: "你的课程描述"
difficulty: 1  # 1-3
```

#### 添加自定义字段
```yaml
# 在章节文件中
---
title: "章节标题"
order: 1
estimated_hours: 2  # 自定义字段
prerequisites: ["前置知识点"]
---
```

## ✅ 质量检查清单

### 课程级别检查

#### 内容质量
- [ ] 课程目标明确
- [ ] 先决条件清晰
- [ ] 内容安排合理
- [ ] 难度递进自然
- [ ] 实用性强

#### 技术准确性
- [ ] 所有代码示例正确
- [ ] 概念描述准确
- [ ] 语法正确无误
- [ ] 测试用例有效

### 章节级别检查

#### 章节结构
- [ ] YAML frontmatter 完整
- [ ] 章节标题清晰
- [ ] 章节概述完整
- [ ] 知识点安排合理
- [ ] 内容详略得当

#### 学习体验
- [ ] 循序渐进
- [ ] 图文并茂
- [ ] 举例恰当
- [ ] 解释清晰

### 题目级别检查

#### 算法题
- [ ] 题目描述清晰
- [ ] 示例完整
- [ ] 测试用例充分
- [ ] 代码模板合理
- [ ] 难度分级准确

#### 选择题
- [ ] 选项数量正确（A-D）
- [ ] 答案唯一
- [ ] 干扰项有迷惑性
- [ ] 解答详细准确

### 格式规范检查

#### YAML 验证
- [ ] YAML 语法正确
- [ ] 必填字段完整
- [ ] 数据类型正确
- [ ] JSON 格式正确

#### 文件组织
- [ ] 文件命名规范
- [ ] 目录结构清晰
- [ ] 依赖关系明确

## 🌟 最佳实践

### 内容创作最佳实践

#### 1. 写作前准备
- 了解目标学员
- 明确学习目标
- 规划课程结构
- 收集相关资料

#### 2. 内容创作
- 先写大纲，再填充内容
- 一次只关注一个知识点
- 使用简单直接的语言
- 提供充分的示例

#### 3. 内容优化
- 大声朗读检查流畅度
- 请他人审阅
- 根据反馈修改
- 保持更新

### 代码示例最佳实践

#### 1. 代码质量
```python
# 好的代码示例
def calculate_average(numbers):
    """
    计算列表的平均值

    Args:
        numbers: 数字列表

    Returns:
        平均值，列表为空时返回 0
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

#### 2. 注释规范
- 使用 docstring
- 说明参数和返回值
- 解释复杂的逻辑
- 提供使用示例

#### 3. 示例多样性
- 基础用法
- 边界情况
- 错误处理
- 实际应用

### 测试用例设计最佳实践

#### 1. 测试策略
- 测试常规功能
- 测试边界情况
- 测试异常输入
- 性能测试（可选）

#### 2. 测试用例示例
```yaml
# 常规用例
- input: "[1,2,3,4,5]"
  output: "3.0"
  is_sample: true

# 边界用例
- input: "[]"
  output: "0"
  is_sample: false

# 异常用例
- input: "[1,2,'a']"
  output: "错误：包含非数字元素"
  is_sample: false
```

## ❌ 常见问题

### 内容设计问题

#### 问题 1：内容过于理论化
**症状：**
- 全是概念解释，没有实践
- 学员学完不知道怎么用
- 内容枯燥，难以坚持

**解决方案：**
- 增加实际案例
- 提供动手练习
- 结合真实项目场景
- 保持理论与实践平衡

#### 问题 2：难度跳跃过大
**症状：**
- 基础章节到高级章节过渡突兀
- 题目难度突然增加
- 学员跟不上进度

**解决方案：**
- 设置过渡章节
- 增加基础练习
- 提供学习路径指引
- 分阶段设置目标

### 代码设计问题

#### 问题 1：代码过于复杂
**症状：**
- 一屏显示不完
- 逻辑嵌套过深
- 学员难以理解

**解决方案：**
- 分步骤讲解
- 使用简单代码
- 添加详细注释
- 提供简化版本

#### 问题 2：测试用例不足
**症状：**
- 只有一个简单示例
- 没有边界测试
- 代码有漏洞但发现不了

**解决方案：**
- 增加测试用例
- 包含边界测试
- 提供错误输入测试
- 考虑性能测试

### 格式规范问题

#### 问题 1：YAML 格式错误
**症状：**
- 字符串缺少引号
- 数组格式错误
- 缺少冒号

**解决方案：**
- 使用 YAML 验证工具
- 参考格式规范
- 检查缩进和标点
- 测试导入功能

#### 问题 2：文件命名不规范
**症状：**
- 章节文件缺少 chapter- 前缀
- 文件名包含特殊字符
- 大小写不一致

**解决方案：**
- 使用模板开始
- 统一命名规范
- 使用编辑器检查
- 定期审阅格式

## 🚀 进阶技巧

### 内容组织技巧

#### 1. 知识点地图
- 为每个课程创建知识点地图
- 显示知识点之间的关系
- 帮助学员建立知识体系

#### 2. 学习路径优化
- 根据学习进度调整内容
- 提供可选的深入学习路径
- 标记重点和可选内容

#### 3. 互动元素设计
- 添加思考题
- 设计编程挑战
- 提供扩展阅读

### 代码教学技巧

#### 1. 代码分解教学
```markdown
**步骤 1：理解问题**
我们需要找到两个数的和等于目标值

**步骤 2：设计思路**
使用哈希表存储已遍历的数字

**步骤 3：实现代码**
[代码实现]

**步骤 4：测试验证**
[测试用例]
```

#### 2. 对比教学
```python
# 方法 1：暴力解法
def twoSum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# 方法 2：优化解法
def twoSum_optimized(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        if target - num in num_map:
            return [num_map[target-num], i]
        num_map[num] = i
    return []
```

#### 3. 错误教学法
- 展示常见错误代码
- 分析错误原因
- 给出正确方案
- 总结经验教训

### 评估与反馈

#### 1. 题目难度评估
- 根据学员答题情况调整难度
- 收集难度反馈
- 建立难度参考标准

#### 2. 内容质量评估
- 学员满意度调查
- 知识点掌握度测试
- 实际应用效果跟踪

#### 3. 持续改进
- 定期更新内容
- 修复错误和漏洞
- 添加新的知识点

## 📚 资源推荐

### 学习资源

#### Python 基础
- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [廖雪峰 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400)
- [Python 入门指南](https://docs.python.org/zh-cn/3/tutorial/index.html)

#### 编程练习
- [LeetCode](https://leetcode.cn/)
- [牛客网](https://www.nowcoder.com/)
- [PTA 程序设计类实验辅助教学平台](https://pintia.cn/)

### 工具推荐

#### 编辑器
- VS Code（推荐）
- PyCharm
- Sublime Text
- Vim

#### 辅助工具
- [Markdown 预览](https://markdown-preview.github.io/)
- [JSON 验证](https://jsonlint.com/)
- [YAML 验证](https://yaml-online-parser.appspot.com/)

#### 版本控制
- Git（必学）
- GitHub
- GitLab

### 社区资源

#### 中文社区
- [CSDN](https://www.csdn.net/)
- [掘金](https://juejin.cn/)
- [知乎 Python 话题](https://www.zhihu.com/topic/python/top-answers)
- [Python 中文社区](https://www.python.org.cn/)

#### 国际社区
- [Stack Overflow](https://stackoverflow.com/)
- [Reddit r/learnpython](https://www.reddit.com/r/learnpython/)
- [Python Discord](https://discord.gg/python)

---

## 📞 联系我们

### 获取帮助
- 查看文档：[格式规范](format-specification.md)、[故障排查](troubleshooting.md)
- 使用模板：参考 `_templates/` 目录
- 提交问题：创建 GitHub Issue
- 邮件联系：course-content@example.com

### 贡献指南
1. Fork 本仓库
2. 创建特性分支
3. 提交更改（使用新格式）
4. 创建 Pull Request

### 更新日志
- v2.0.0 - 迁移到多文件格式
- v1.0.0 - 初始版本
- 更多更新请查看提交历史

---

*本课程创作指南将持续更新，欢迎提出改进建议。*
*让我们一起打造高质量的 Python 教学内容！*