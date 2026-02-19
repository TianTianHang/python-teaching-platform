# Proposal: Add Collapsible Hints to Python Practice Problems

## Summary

Convert the "提示" (Hint) sections in all Python practice problem files to use the existing `markdown-foldable-blocks` directive syntax, making hints hidden by default behind collapsible blocks.

## Motivation

Currently, all hints in Python practice problems are directly visible, which may:
- Give away solutions too easily
- Reduce the challenge for students who want to think through problems independently
- Not match modern educational platform best practices for progressive hinting

By using collapsible blocks, students can choose when to view hints, supporting better learning outcomes.

## Scope

This change affects **41 problem files** in `courses/python-practice/problems/` that contain "### 提示" sections.

### Files to Modify

The following problem files will be updated to use `:::tip{state="collapsed"}` directive blocks:

1. `convert-int-to-str.md`
2. `convert-list-to-str.md`
3. `convert-str-to-int.md`
4. `convert-str-to-list.md`
5. `dict-add-key.md`
6. `dict-count-words.md`
7. `dict-find-key.md`
8. `dict-get-value.md`
9. `dict-invert.md`
10. `dict-merge.md`
11. `flow-count-positive.md`
12. `flow-grade.md`
13. `flow-max-of-three.md`
14. `flow-sum-range.md`
15. `format-fstring.md`
16. `format-join.md`
17. `format-pad.md`
18. `list-filter-even.md`
19. `list-last.md`
20. `list-max.md`
21. `list-merge.md`
22. `list-min.md`
23. `list-remove-duplicates.md`
24. `math-abs.md`
25. `math-divmod.md`
26. `math-is-even.md`
27. `math-power.md`
28. `math-round.md`
29. `set-create.md`
30. `set-difference.md`
31. `set-intersection.md`
32. `set-union.md`
33. `string-concat.md`
34. `string-count-char.md`
35. `string-length.md`
36. `string-reverse.md`
37. `string-strip.md`
38. `string-upper-lower.md`
39. `tuple-access.md`
40. `tuple-merge.md`
41. `tuple-to-list.md`

## Existing Specification

This change utilizes the existing [`markdown-foldable-blocks`](../../../specs/markdown-foldable-blocks/spec.md) specification which defines:

- `:::tip{title="提示" state="collapsed"}` - For hints (collapsed by default)
- `:::answer{title="答案" state="collapsed"}` - For complete solutions
- Support for title, state, and other attributes

No new specification is required.

## Example Transformation

### Before (current format):
```markdown
### 提示

使用 Python 内置的 `max()` 函数：`max(numbers)`
```

### After (new format):
```markdown
### 提示

:::tip{title="提示" state="collapsed"}
使用 Python 内置的 `max()` 函数：`max(numbers)`
:::
```

For more complex hints with code blocks:

### Before:
```markdown
### 提示

使用字典和 for 循环：
```python
result = {}
for word in words:
    if word in result:
        result[word] += 1
    else:
        result[word] = 1
return result
```

或者使用 get() 方法：
```python
result = {}
for word in words:
    result[word] = result.get(word, 0) + 1
return result
```
```

### After:
```markdown
### 提示

:::tip{title="方法一" state="collapsed"}
使用字典和 for 循环：
```python
result = {}
for word in words:
    if word in result:
        result[word] += 1
    else:
        result[word] = 1
return result
```
:::

:::tip{title="方法二" state="collapsed"}
或者使用 get() 方法：
```python
result = {}
for word in words:
    result[word] = result.get(word, 0) + 1
return result
```
:::
```

## Implementation Approach

1. **Pattern Matching**: Identify all "### 提示" sections in problem files
2. **Content Wrapping**: Wrap hint content in `:::tip{title="提示" state="collapsed"}` directive blocks
3. **Multi-level Hints**: For problems with multiple hint approaches, create separate collapsible blocks with titles (e.g., `title="方法一"`, `title="方法二"`)
4. **Code Blocks**: Ensure code blocks within hints are properly formatted inside the directive blocks
5. **Validation**: Verify markdown syntax is correct after transformation

## Benefits

1. **Better Learning Experience**: Students can attempt problems before viewing hints
2. **Progressive Disclosure**: Supports multiple hint levels (if authors choose to implement them)
3. **Backward Compatible**: The `markdown-foldable-blocks` spec already exists and is supported
4. **Minimal Platform Changes**: No backend changes needed - only content updates

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Platform rendering issues | The spec includes fallback behavior for unsupported platforms |
| Accidental content changes | Use automated transformation with manual review |
| Markdown syntax errors | Validate each file after modification |

## Success Criteria

- All 41 problem files have their hint sections converted to `:::tip{state="collapsed"}` blocks
- Hints are collapsed by default when rendered
- All markdown remains valid
- No changes to problem metadata (YAML frontmatter) or test cases
