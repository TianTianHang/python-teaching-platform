# Design: Add Collapsible Hints to Python Practice Problems

## Architecture

This is a **content-only change** that updates existing Markdown problem files to use the existing `markdown-foldable-blocks` directive syntax. No backend, database, or API changes are required.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Current State                                │
├─────────────────────────────────────────────────────────────────┤
│  Problem File (.md)                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ### 提示                                                  │    │
│  │ 使用 max() 函数...                                       │    │
│  │ (always visible)                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────────┐
│                     Target State                                 │
├─────────────────────────────────────────────────────────────────┤
│  Problem File (.md)                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ### 提示                                                  │    │
│  │ :::tip{title="提示" state="collapsed"}                   │    │
│  │ 使用 max() 函数...                                       │    │
│  │ :::                                                       │    │
│  │ (hidden by default, user-clickable to expand)            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Transformation Logic

### Basic Hint Pattern

For simple, single-paragraph hints:

**Detection Pattern:**
```regex
^### 提示\s*$\n(.*?)(?=^###|\Z)
```

**Transformation:**
```markdown
### 提示

:::tip{title="提示" state="collapsed"}
<original hint content>
:::
```

### Multi-Part Hint Pattern

For hints with multiple code blocks or approaches, create separate collapsible blocks:

**Before:**
```markdown
### 提示

方法一：使用 for 循环
```python
code here
```

方法二：使用列表推导
```python
code here
```
```

**After:**
```markdown
### 提示

:::tip{title="方法一" state="collapsed"}
使用 for 循环：
```python
code here
```
:::

:::tip{title="方法二" state="collapsed"}
使用列表推导：
```python
code here
```
:::
```

## Edge Cases

### 1. Code Blocks Within Hints

The directive syntax requires proper nesting:

```markdown
:::tip{title="提示" state="collapsed"}
提示文本

```python
code block here
```

更多提示文本
:::
```

### 2. Lists Within Hints

Lists must be properly indented within the directive block:

```markdown
:::tip{title="提示" state="collapsed"}
- 要点一
- 要点二
  - 子要点
:::
```

### 3. Empty or Minimal Hints

For very short hints (one line), still wrap in directive for consistency:

```markdown
### 提示

:::tip{title="提示" state="collapsed"}
使用 max() 函数
:::
```

## File Processing Strategy

### Batch Processing Approach

1. **Discovery Phase**
   - Scan all `.md` files in `courses/python-practice/problems/`
   - Identify files containing `### 提示` header
   - Build processing manifest

2. **Transformation Phase**
   - For each file, locate `### 提示` section
   - Extract content until next `###` header or EOF
   - Wrap content in `:::tip{title="提示" state="collapsed"}` directive
   - Handle multi-part hints (split by numbered lists or "方法" markers)
   - Write back to file

3. **Validation Phase**
   - Verify YAML frontmatter is unchanged
   - Verify test cases are unchanged
   - Verify markdown syntax is valid
   - Spot-check rendered output

### Manual Review Points

After automated transformation, manually verify:
- Complex hints with nested formatting
- Files with unusual hint section formatting
- Files where hint content may include `:::` characters (edge case)

## Testing Strategy

### Content Validation Tests

```bash
# 1. Check YAML frontmatter unchanged
# 2. Check hint sections now have :::tip blocks
# 3. Verify no malformed directives
# 4. Count files updated (should be 41)
```

### Visual Regression Tests

- Compare rendered output before/after for sample files
- Ensure hints are collapsed by default
- Ensure expand/collapse functionality works

## Rollback Plan

If issues arise:
1. Git revert the content changes
2. Files are easily identifiable by commit hash
3. No database migrations to reverse

## Future Enhancements (Out of Scope)

- Adding progressive hint levels (Hint 1, Hint 2, Solution)
- Adding hint metadata (difficulty, related concepts)
- Analytics on hint usage rates
- Hint effectiveness metrics
