# Proposal: Add Python Practice Course

## Summary

添加一个纯算法练习课程，面向 Python 初学者，涵盖 Python 语言核心知识点，包括数据结构、数学运算、类型转换、字符串格式化和控制流等。该课程不包含章节内容，仅包含算法题目，让初学者通过动手实践全面熟悉 Python 语言。

## Motivation

Python 初学者在完成基础语法学习后，需要大量的实践练习来巩固所学知识。现有的课程（如 `python-intro`）侧重于知识讲解，练习题目分散在各章节中。本课程将：

1. 提供集中的练习环境，让学习者专注于编码实践
2. 涵盖 Python 核心知识点：数据结构、数学运算、类型转换、字符串格式化、控制流
3. 每题包含友好提示，指导初学者选择合适的操作和方法
4. 题目描述简洁明了，降低理解门槛
5. 帮助初学者建立对 Python 语言的全面认知

## Proposed Solution

创建新课程 `python-practice`，包含以下特点：

- **无章节设计**：课程直接由算法题组成，不包含章节内容
- **难度分级**：所有题目难度为 1（简单），适合初学者
- **题目分类**：按知识点类型组织（字符串、列表、字典、数学运算、元组、集合、类型转换、字符串格式化、控制流）
- **友好提示**：每题包含"提示"部分，说明建议使用的数据结构和操作
- **循序渐进**：题目从最简单开始，逐步增加复杂度

### 题目规划（约 35-40 题）

#### 基础运算题（5 题）
1. `math-abs.md` - 获取绝对值
2. `math-power.md` - 计算幂次方
3. `math-round.md` - 四舍五入
4. `math-divmod.md` - 获取商和余数
5. `math-is-even.md` - 判断奇偶性

#### 字符串题（6 题）
1. `string-length.md` - 获取字符串长度
2. `string-concat.md` - 字符串连接
3. `string-upper-lower.md` - 大小写转换
4. `string-reverse.md` - 字符串反转
5. `string-count-char.md` - 统计字符出现次数
6. `string-strip.md` - 去除首尾空格

#### 列表题（6 题）
1. `list-max.md` - 找列表最大值
2. `list-min.md` - 找列表最小值
3. `list-last.md` - 获取列表最后一个元素
4. `list-filter-even.md` - 过滤偶数
5. `list-remove-duplicates.md` - 去除重复元素
6. `list-merge.md` - 合并两个列表

#### 字典题（6 题）
1. `dict-get-value.md` - 获取字典值
2. `dict-add-key.md` - 添加键值对
3. `dict-find-key.md` - 检查键是否存在
4. `dict-count-words.md` - 统计单词频率（简化版）
5. `dict-invert.md` - 字典键值互换
6. `dict-merge.md` - 合并两个字典

#### 元组题（3 题）
1. `tuple-access.md` - 访问元组元素
2. `tuple-merge.md` - 合并元组
3. `tuple-to-list.md` - 元组转列表

#### 集合题（4 题）
1. `set-create.md` - 从列表创建集合
2. `set-union.md` - 集合并集
3. `set-intersection.md` - 集合交集
4. `set-difference.md` - 集合差集

#### 类型转换题（4 题）
1. `convert-str-to-int.md` - 字符串转整数
2. `convert-int-to-str.md` - 整数转字符串
3. `convert-list-to-str.md` - 列表转字符串
4. `convert-str-to-list.md` - 字符串转列表

#### 字符串格式化题（3 题）
1. `format-fstring.md` - 使用 f-string 格式化
2. `format-pad.md` - 字符串填充
3. `format-join.md` - 使用 join 连接字符串

#### 控制流题（4 题）
1. `flow-max-of-three.md` - 三个数最大值（使用 if/else）
2. `flow-count-positive.md` - 统计正数个数
3. `flow-grade.md` - 分数转等级
4. `flow-sum-range.md` - 计算范围内数的和

### 课程元数据配置

```yaml
title: "Python 实践练习"
description: "面向初学者的 Python 算法练习课程，涵盖数据结构、数学运算、类型转换、字符串格式化、控制流等核心知识点，帮助你通过动手实践全面熟悉 Python 语言"
order: 3
difficulty: 1
tags: ["python", "practice", "algorithm", "字符串", "列表", "字典", "元组", "集合", "类型转换", "格式化", "控制流"]
```

## Impact

### 用户受益
- 初学者获得集中的练习环境
- 每题包含友好提示，降低学习难度
- 涵盖最常用的数据结构操作

### 系统影响
- 新增课程目录 `courses/python-practice/`
- 仅包含 `course.md` 和 `problems/` 目录
- 无需修改导入逻辑，符合现有格式

## Alternatives Considered

1. **在现有课程中添加练习**：会导致单个课程过于庞大，不利于学习者专注练习
2. **使用 unlock_conditions 限制题目顺序**：考虑到这是练习课程，允许学习者自由选择题目更灵活
3. **添加选择题**：本课程专注算法实践，选择题已在其他课程中覆盖

## Implementation Plan

基于用户确认的方案：

### Directory Structure
- 复用现有 `courses/python-algorithm-practice/` 目录
- 包含 `course.md` 和 `problems/` 子目录
- 不包含 `chapters/` 目录（纯练习课程）

### Course Metadata
```yaml
title: "Python 实践练习"
description: "面向初学者的 Python 算法练习课程，涵盖数据结构、数学运算、类型转换、字符串格式化、控制流等核心知识点，帮助你通过动手实践全面熟悉 Python 语言"
order: 101
difficulty: 1
tags: ["python", "practice", "algorithm", "字符串", "列表", "字典", "元组", "集合", "类型转换", "格式化", "控制流"]
```

### Key Features
- **纯算法练习**：41 道算法题，涵盖 9 大知识点
- **严格返回值匹配**：每个函数的返回值必须与 test case 的 JSON 格式完全匹配
- **友好提示**：每题包含"提示"部分，指导使用正确的 Python 方法
- **自由练习**：无解锁条件，可任意顺序完成

### Implementation Tasks
创建 41 个算法题文件，每个文件包含：
- 完整的 YAML frontmatter（type: algorithm, difficulty: 1）
- 3-5 个测试用例（至少 1 个 sample）
- 函数模板和提示
- 正确的返回值格式（与 test case 匹配）

## Open Questions

1. 是否需要为题目设置解锁条件？（建议：否，允许自由练习）
2. 题目数量是否合适？（建议：15-20 题，每类 5-6 题）
