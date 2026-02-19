# Tasks: Add Collapsible Hints to Python Practice Problems

## Phase 1: Preparation

- [x] T1.1: Create sample test transformation on 2-3 problem files to validate approach
  - Choose simple hint (`list-max.md`)
  - Choose complex hint with code blocks (`dict-count-words.md`)
  - Choose hint with multiple approaches (`flow-grade.md`)
  - Validate markdown syntax is correct

## Phase 2: Content Transformation (41 Files)

### String Problems (7 files)
- [x] T2.1: Update `string-reverse.md` - Wrap slicing hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.2: Update `string-length.md` - Wrap `len()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.3: Update `string-strip.md` - Wrap strip methods hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.4: Update `string-concat.md` - Wrap concatenation methods hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.5: Update `string-upper-lower.md` - Wrap case conversion methods hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.6: Update `string-count-char.md` - Wrap `count()` method hint in `:::tip{title="提示" state="collapsed"}`

### Math Problems (6 files)
- [x] T2.7: Update `math-abs.md` - Wrap `abs()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.8: Update `math-power.md` - Wrap `**` or `pow()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.9: Update `math-round.md` - Wrap `round()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.10: Update `math-divmod.md` - Wrap `divmod()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.11: Update `math-is-even.md` - Wrap modulo hint in `:::tip{title="提示" state="collapsed"}`

### List Problems (6 files)
- [x] T2.12: Update `list-max.md` - Wrap `max()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.13: Update `list-min.md` - Wrap `min()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.14: Update `list-last.md` - Wrap negative indexing hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.15: Update `list-merge.md` - Wrap list concatenation/extend hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.16: Update `list-remove-duplicates.md` - Wrap set conversion or loop hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.17: Update `list-filter-even.md` - Wrap list comprehension hint in `:::tip{title="提示" state="collapsed"}`

### Dict Problems (6 files)
- [x] T2.18: Update `dict-get-value.md` - Wrap dict access hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.19: Update `dict-add-key.md` - Wrap key assignment hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.20: Update `dict-find-key.md` - Wrap `in` operator hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.21: Update `dict-count-words.md` - Split into two `:::tip` blocks with titles (e.g., `title="方法一"`, `title="方法二"`)
- [x] T2.22: Update `dict-merge.md` - Wrap `**` unpacking or `update()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.23: Update `dict-invert.md` - Wrap dictionary comprehension hint in `:::tip{title="提示" state="collapsed"}`

### Set Problems (4 files)
- [x] T2.24: Update `set-create.md` - Wrap `set()` constructor hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.25: Update `set-union.md` - Wrap `|` or `union()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.26: Update `set-intersection.md` - Wrap `&` or `intersection()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.27: Update `set-difference.md` - Wrap `-` or `difference()` hint in `:::tip{title="提示" state="collapsed"}`

### Tuple Problems (4 files)
- [x] T2.28: Update `tuple-access.md` - Wrap indexing hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.29: Update `tuple-merge.md` - Wrap tuple concatenation hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.30: Update `tuple-to-list.md` - Wrap `list()` conversion hint in `:::tip{title="提示" state="collapsed"}`

### Format Problems (4 files)
- [x] T2.31: Update `format-fstring.md` - Wrap f-string syntax hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.32: Update `format-join.md` - Wrap `str.join()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.33: Update `format-pad.md` - Wrap `str.ljust()`/`rjust()`/`center()` hint in `:::tip{title="提示" state="collapsed"}`

### Convert Problems (4 files)
- [x] T2.34: Update `convert-int-to-str.md` - Wrap `str()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.35: Update `convert-str-to-int.md` - Wrap `int()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.36: Update `convert-list-to-str.md` - Wrap `str()` conversion hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.37: Update `convert-str-to-list.md` - Wrap `list()` or `split()` hint in `:::tip{title="提示" state="collapsed"}`

### Flow Control Problems (4 files)
- [x] T2.38: Update `flow-max-of-three.md` - Wrap if/elif comparison hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.39: Update `flow-count-positive.md` - Wrap loop with conditional hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.40: Update `flow-sum-range.md` - Wrap `range()` and `sum()` hint in `:::tip{title="提示" state="collapsed"}`
- [x] T2.41: Update `flow-grade.md` - Consider splitting into multiple progressive hints with titles (e.g., `title="提示"`, `title="完整代码"`)

## Phase 3: Validation

- [x] T3.1: Verify YAML frontmatter unchanged in all 41 files
  - Run grep check for `^---` boundaries
  - Validate no frontmatter fields were modified

- [x] T3.2: Verify test cases unchanged in all 41 files
  - Run validation to check `test_cases:` sections intact

- [x] T3.3: Verify markdown syntax is valid
  - Check all `:::tip` blocks are properly closed
  - Check for malformed directive syntax

- [x] T3.4: Spot-check rendered output for 5 representative files
  - Simple hint (`list-max.md`)
  - Complex hint with code (`dict-count-words.md`)
  - Multi-approach hint (`flow-grade.md`)

- [x] T3.5: Count updated files
  - Verify exactly 41 files were modified
  - Verify no files were missed

## Phase 4: Documentation

- [x] T4.1: Update [format-specification.md](../../../docs/format-specification.md)
  - Add note about using `:::tip{state="collapsed"}` for hints
  - Reference existing `markdown-foldable-blocks` spec

- [x] T4.2: Update [course-authoring-guide.md](../../../docs/course-authoring-guide.md)
  - Add section on "Writing Collapsible Hints"
  - Provide examples for progressive hinting

## Dependencies

- T2.x tasks can be done in parallel (batch processing)
- T3.x tasks depend on completion of T2.x tasks
- T4.x tasks can be done in parallel with T3.x tasks

## Estimated Effort

- Phase 1: 15 minutes (validation)
- Phase 2: 30-45 minutes (batch processing with script assistance)
- Phase 3: 15-20 minutes (validation and spot-checks)
- Phase 4: 10 minutes (documentation updates)

**Total**: ~70-90 minutes
