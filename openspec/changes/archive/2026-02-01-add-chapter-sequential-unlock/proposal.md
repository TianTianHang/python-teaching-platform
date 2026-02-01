# Proposal: Add Sequential Chapter Unlock to Python Intro Course

## Change ID
`add-chapter-sequential-unlock`

## Summary
Add sequential `unlock_conditions` to all chapters (2-8) in the Python Intro course so that each chapter requires completion of the previous chapter. Additionally, establish a normative requirement that new courses SHOULD use sequential chapter unlocks by default.

## Motivation
Currently, all chapters in the Python Intro course are unlocked by default. While the course topics are designed to build progressively (variables → operators → conditionals → loops → lists → dictionaries → functions), there is no mechanism enforcing this progression.

Adding sequential unlock conditions will:
- Ensure students have mastered foundational concepts before advancing
- Prevent confusion from accessing advanced topics prematurely
- Maintain the pedagogical integrity of the course design
- Align with the platform's existing chapter unlock functionality
- Establish a recommended default pattern for future courses

## Proposed Solution
Add `unlock_conditions` frontmatter to chapters 2-8 with `type: "prerequisite"`:

- **Chapter 2** requires Chapter 1 completion
- **Chapter 3** requires Chapter 2 completion
- **Chapter 4** requires Chapter 3 completion
- **Chapter 5** requires Chapter 4 completion
- **Chapter 6** requires Chapter 5 completion
- **Chapter 7** requires Chapter 6 completion
- **Chapter 8** requires Chapter 7 completion

Chapter 1 remains unlocked (no conditions) as the entry point.

## Scope
### In Scope
- Adding `unlock_conditions` to existing chapter files in `courses/python-intro/chapters/`
- Updating spec documentation with:
  - Python Intro course specific unlock requirements
  - General normative requirement for sequential chapter unlocks in new courses
- Adding commented unlock conditions example to chapter template
- Updating course authoring guide with sequential unlock recommendations

### Out of Scope
- Modifying chapter content
- Changing problem unlock conditions
- Modifying the import/validation system
- Adding time-based unlock conditions
- Forcing sequential unlocks on existing courses (only Python Intro is modified)

## Alternatives Considered
1. **No unlock conditions**: Current state - allows skipping chapters, but may lead to knowledge gaps
2. **Date-based unlocks**: Would unlock chapters on a schedule, but doesn't adapt to individual student pace
3. **Cumulative prerequisites**: Each chapter requires ALL previous chapters (e.g., Ch 5 requires Ch 1-4). More strict than necessary and harder to maintain

Sequential prerequisite (n requires n-1) provides the right balance of structure and simplicity.

## Impact
- **Students**: Must complete chapters in order; cannot skip ahead
- **Content authors**: Future chapters must include `unlock_conditions` to maintain the pattern
- **Platform**: No changes needed; uses existing chapter unlock functionality

## Related Changes
None - this is a standalone enhancement to the Python Intro course content.
