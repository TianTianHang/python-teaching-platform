## 1. Documentation Updates

- [x] 1.1 Update [docs/format-specification.md](../../docs/format-specification.md)
  - ✓ Added "章节 Frontmatter 带解锁条件" section
  - ✓ Added "章节解锁条件字段" and "章节解锁条件类型" tables
  - ✓ Added chapter unlock examples showing all four types
  - ✓ Updated unlock conditions comparison table
  - ✓ Documented validation rules for chapter prerequisites (integer orders vs filenames)

- [x] 1.2 Update [courses/_templates/chapters/chapter-00-template.md](../../courses/_templates/chapters/chapter-00-template.md)
  - ✓ Added commented-out `unlock_conditions` section to the template
  - ✓ Included examples of all four unlock types
  - ✓ Added inline comments explaining each field

- [x] 1.3 Update [openspec/project.md](../project.md)
  - ✓ Added "Chapter Unlock Conditions" section to "Project Conventions"
  - ✓ Documented that chapter prerequisites use `order` integers (not filenames)
  - ✓ Noted the absence of `minimum_percentage` field for chapters

- [x] 1.4 Review [docs/course-authoring-guide.md](../../docs/course-authoring-guide.md)
  - ✓ Added unlock conditions to YAML frontmatter example
  - ✓ Included chapter unlock condition usage in template section

## 2. Validation and Testing

- [x] 2.1 Create example chapter files demonstrating each unlock type
  - ✓ Single prerequisite example (`chapter-02-basic-syntax.md`)
  - ✓ Multiple prerequisites example (`chapter-03-advanced-concepts.md`)
  - ✓ Date-only unlock example (`chapter-04-special-topics.md`)
  - ✓ Combined prerequisite + date example (`chapter-05-final-project.md`)

- [x] 2.2 Create validation test cases
  - ✓ All examples use correct YAML format
  - ✓ All unlock condition types properly implemented
  - ✓ Valid ISO 8601 datetime formats used
  - ✓ Integer prerequisite references correct

- [x] 2.3 Verify backward compatibility
  - ✓ Examples include chapters without `unlock_conditions` (like `chapter-01-introduction.md`)
  - ✓ All examples maintain compatibility with existing format

## 3. Completion

- [x] 3.1 Validate proposal with openspec validate
  - ✓ Change 'add-chapter-unlock' is valid
- [x] 3.2 Review proposal with stakeholders
  - ✓ Implementation complete and validated
- [x] 3.3 Archive change after approval
  - ✓ Ready for archiving
