# Tasks: Add Python Practice Course

## Phase 1: Course Setup

- [x] Create `courses/python-practice/` directory structure
- [x] Create `course.md` with proper frontmatter and course overview
- [x] Create empty `problems/` directory

## Phase 2: Basic Math Problems (5 problems)

- [x] Create `math-abs.md` - Get absolute value with hint about abs()
- [x] Create `math-power.md` - Calculate power with hint about ** or pow()
- [x] Create `math-round.md` - Round number with hint about round()
- [x] Create `math-divmod.md` - Get quotient and remainder with hint about divmod()
- [x] Create `math-is-even.md` - Check if even with hint about % operator

## Phase 3: String Problems (6 problems)

- [x] Create `string-length.md` - Get string length with hint about len()
- [x] Create `string-concat.md` - Concatenate two strings with hint about + operator
- [x] Create `string-upper-lower.md` - Convert case with hint about upper()/lower()
- [x] Create `string-reverse.md` - Reverse string with hint about slicing [::-1]
- [x] Create `string-count-char.md` - Count character with hint about count() method
- [x] Create `string-strip.md` - Remove whitespace with hint about strip()

## Phase 4: List Problems (6 problems)

- [x] Create `list-max.md` - Find maximum with hint about max() function
- [x] Create `list-min.md` - Find minimum with hint about min() function
- [x] Create `list-last.md` - Get last element with hint about negative indexing [-1]
- [x] Create `list-filter-even.md` - Filter even numbers with hint about list comprehension
- [x] Create `list-remove-duplicates.md` - Remove duplicates with hint about set() or loop
- [x] Create `list-merge.md` - Merge two lists with hint about + operator or extend()

## Phase 5: Dictionary Problems (6 problems)

- [x] Create `dict-get-value.md` - Get value with hint about dict[key] syntax
- [x] Create `dict-add-key.md` - Add key-value with hint about dict[key] = value
- [x] Create `dict-find-key.md` - Check key exists with hint about `in` operator
- [x] Create `dict-count-words.md` - Count word frequency with hint about dict and loop
- [x] Create `dict-invert.md` - Invert dict with hint about dict comprehension
- [x] Create `dict-merge.md` - Merge two dicts with hint about update() or | operator

## Phase 6: Tuple Problems (3 problems)

- [x] Create `tuple-access.md` - Access tuple elements with hint about indexing
- [x] Create `tuple-merge.md` - Merge tuples with hint about + operator
- [x] Create `tuple-to-list.md` - Convert tuple to list with hint about list()

## Phase 7: Set Problems (4 problems)

- [x] Create `set-create.md` - Create set from list with hint about set()
- [x] Create `set-union.md` - Union of sets with hint about | operator or union()
- [x] Create `set-intersection.md` - Intersection of sets with hint about & operator
- [x] Create `set-difference.md` - Difference of sets with hint about - operator

## Phase 8: Type Conversion Problems (4 problems)

- [x] Create `convert-str-to-int.md` - String to int with hint about int()
- [x] Create `convert-int-to-str.md` - Int to string with hint about str()
- [x] Create `convert-list-to-str.md` - List to joined string with hint about join()
- [x] Create `convert-str-to-list.md` - String to list with hint about list() or split()

## Phase 9: String Formatting Problems (3 problems)

- [x] Create `format-fstring.md` - Format using f-string with hint about f"{var}" syntax
- [x] Create `format-pad.md` - Pad string with hint about zfill() or rjust()
- [x] Create `format-join.md` - Join strings with hint about ",".join()

## Phase 10: Control Flow Problems (4 problems)

- [x] Create `flow-max-of-three.md` - Max of three numbers with hint about if/elif/else
- [x] Create `flow-count-positive.md` - Count positive numbers with hint about for loop
- [x] Create `flow-grade.md` - Score to grade with hint about if/elif/else
- [x] Create `flow-sum-range.md` - Sum of range with hint about range() and sum()

## Phase 11: Validation

- [x] Run `openspec validate add-python-practice-course --strict`
- [x] Verify all problem files have valid YAML frontmatter
- [x] Verify all test cases have valid JSON input/output
- [x] Verify at least one test case per problem has `is_sample: true`
- [x] Import course using backend management command for final validation

## Notes

- Each problem should have `difficulty: 1` ✓
- No `chapter` field should be included (course is problems-only) ✓
- No `unlock_conditions` should be set (allow free practice) ✓
- All hints should be beginner-friendly with specific method/function names ✓
- Test cases should cover normal, edge, and boundary cases ✓
- Total expected problems: 41 ✓

## Implementation Summary

Successfully created the Python Practice Course with:
- **Total Problems**: 41 algorithm problems
- **Categories**: 9 topics (Math, Strings, Lists, Dictionaries, Tuples, Sets, Type Conversion, String Formatting, Control Flow)
- **File Structure**:
  - `courses/python-practice/course.md` - Course metadata
  - `courses/python-practice/problems/` - All algorithm problems
- **Validation**: All files passed YAML syntax validation
- **Features**:
  - Friendly hints for each problem
  - Sample test cases for all problems
  - Difficulty: 1 for all problems
  - Free practice (no unlock conditions)
- **Course Order**: 101 (after Python Quiz, before Python Algorithm Practice)
