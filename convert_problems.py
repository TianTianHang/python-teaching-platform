#!/usr/bin/env python3
"""
转换 problem-base 中的题目到平台格式
"""
import re
import os
from pathlib import Path


def parse_questions(content, source_file):
    """解析题目内容，返回题目列表"""
    questions = []

    # 检测格式类型
    if '## 第' in content or '## 第 1 题' in content:
        # 详细格式（带"第 X 题"标记）
        questions = parse_detailed_format(content)
    else:
        # 简略格式（直接问题列表）
        questions = parse_simple_format(content)

    return questions


def parse_detailed_format(content):
    """解析详细格式（带"第 X 题"标记）"""
    questions = []

    # 分割每道题目
    pattern = r'## 第 \d+ 题\s*\n'
    parts = re.split(pattern, content)

    for part in parts[1:]:  # 跳过第一个空部分
        question = parse_single_question(part)
        if question:
            questions.append(question)

    return questions


def parse_simple_format(content):
    """解析简略格式（直接问题列表）"""
    questions = []

    # 按分隔符分割题目
    parts = re.split(r'---+', content)

    for part in parts:
        question = parse_simple_question(part)
        if question:
            questions.append(question)

    return questions


def parse_single_question(text):
    """解析单道题目（详细格式）"""
    question = {}

    # 提取问题
    q_match = re.search(r'\*\*问题：\*\*\s*(.+?)(?=\*\*选项|\n\n|\Z)', text, re.DOTALL)
    if q_match:
        question['title'] = q_match.group(1).strip()
    else:
        return None

    # 提取选项
    options = {}
    opt_pattern = r'([A-D])\.\s*(.+?)(?=\n[A-D]\.|\n\n|\Z)'
    opt_matches = re.findall(opt_pattern, text, re.DOTALL)

    for opt in opt_matches:
        key = opt[0]
        value = opt[1].strip()
        # 清理 Markdown 格式
        value = re.sub(r'`', '', value)
        options[key] = value

    if len(options) < 4:
        return None

    question['options'] = options

    # 提取正确答案
    ans_match = re.search(r'\*\*正确答案：\*\*\s*([A-D])', text)
    if ans_match:
        question['answer'] = ans_match.group(1)
    else:
        # 尝试其他格式
        ans_match = re.search(r'正确答案：\s*([A-D])', text)
        if ans_match:
            question['answer'] = ans_match.group(1)
        else:
            return None

    # 提取解析（可选）
    exp_match = re.search(r'\*\*解析：\*\*\s*(.+?)(?=\n---|\Z)', text, re.DOTALL)
    if exp_match:
        question['explanation'] = exp_match.group(1).strip()
    else:
        question['explanation'] = ''

    return question


def parse_simple_question(text):
    """解析单道题目（简略格式）"""
    question = {}

    # 提取问题（第一行）
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if not lines:
        return None

    # 查找问题行（通常是第一个非选项、非答案行）
    question_text = ''
    for line in lines:
        if not line.startswith('-') and not line.startswith('**答案'):
            question_text = line
            break

    if not question_text:
        return None

    # 去除序号
    question_text = re.sub(r'^\d+\.\s*', '', question_text)
    question['title'] = question_text

    # 提取选项
    options = {}
    opt_pattern = r'- ([A-D])\.?\s*(.+)'
    opt_matches = re.findall(opt_pattern, text)

    for opt in opt_matches:
        key = opt[0]
        value = opt[1].strip()
        # 清理 Markdown 格式
        value = re.sub(r'`', '', value)
        options[key] = value

    if len(options) < 4:
        return None

    question['options'] = options

    # 提取答案
    ans_match = re.search(r'\*\*答案：?\*\*\s*([A-D])', text)
    if ans_match:
        question['answer'] = ans_match.group(1)
    else:
        # 尝试其他格式
        ans_match = re.search(r'答案[：:]\s*([A-D])', text)
        if ans_match:
            question['answer'] = ans_match.group(1)
        else:
            return None

    # 提取解析
    exp_match = re.search(r'\*\*解析：\*\*\s*(.+?)(?=\n\n|\Z)', text, re.DOTALL)
    if exp_match:
        question['explanation'] = exp_match.group(1).strip()
    else:
        question['explanation'] = ''

    return question


def to_slug(text):
    """转换为 slug 格式"""
    # 保留中文，只替换特殊字符
    text = re.sub(r'[^\w\u4e00-\u9fa5]+', '-', text)
    text = text.strip('-')
    return text[:50]  # 限制长度


def generate_problem_file(question, index, difficulty=1, chapter=1):
    """生成题目文件内容"""
    title = question['title']
    # 清理标题中的 Markdown
    title_clean = re.sub(r'\*\*', '', title)
    title_clean = re.sub(r'`', '', title_clean)

    options = question['options']
    answer = question['answer']

    # 生成 slug
    slug = f"quiz-{index:03d}-{to_slug(title_clean[:20])}"

    # 第二栏放题目内容（描述 + 选项展示）
    body = f"""## 题目描述

{title_clean}

### 选项

- A: {options.get('A', '')}
- B: {options.get('B', '')}
- C: {options.get('C', '')}
- D: {options.get('D', '')}
"""

    content = f"""---
title: "{title_clean[:100]}"
type: "choice"
difficulty: {difficulty}
chapter: {chapter}
is_multiple_choice: false
options:
  A: "{options.get('A', '')[:200]}"
  B: "{options.get('B', '')[:200]}"
  C: "{options.get('C', '')[:200]}"
  D: "{options.get('D', '')[:200]}"
correct_answer: "{answer}"
---

{body}
"""
    return slug + '.md', content


def main():
    source_dir = Path('/home/tiantian/project/problem-base')
    target_dir = Path('/home/tiantian/project/course-content/courses/python-quiz/problems')

    # 难度映射
    difficulty_map = {
        'python_quiz_questions': 1,
        'python_fundamentals_quiz': 1,
        'python_data_types_quiz': 1,
        'python_strings_quiz': 1,
        'python_builtins_quiz': 2,
        'python_intermediate_quiz': 2,
        'python_intermediate_concepts_quiz': 2,
        'python_intermediate_operators_quiz': 2,
        'python_advanced_quiz': 3,
        'python_advanced_concepts_quiz': 3,
        'python_advanced_internal_quiz': 3,
        'python_advanced_programming_quiz': 3,
        'python_expert_quiz': 3,
        'python_expert_internal_quiz': 3,
        'python_expert_systems_quiz': 3,
    }

    problem_count = 0
    file_count = 0

    for md_file in sorted(source_dir.glob('*.md')):
        print(f"Processing: {md_file.name}")

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        questions = parse_questions(content, md_file.name)

        # 根据文件名确定难度
        base_name = md_file.stem
        difficulty = difficulty_map.get(base_name, 1)

        for i, q in enumerate(questions):
            try:
                filename, file_content = generate_problem_file(
                    q,
                    problem_count + 1,
                    difficulty=difficulty,
                    chapter=1
                )

                target_file = target_dir / filename
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)

                problem_count += 1
            except Exception as e:
                print(f"  Error processing question {i}: {e}")

        file_count += 1
        print(f"  Generated {len(questions)} problems")

    print(f"\nTotal: {file_count} files, {problem_count} problems")


if __name__ == '__main__':
    main()
