## 1. 预准备工作

- [x] 1.1 查看当前数据库结构和现有索引
- [ ] 1.2 创建测试数据生成脚本（10 万条测试数据）
- [ ] 1.3 编写性能基准测试脚本

## 2. 修改模型定义

- [x] 2.1 为 ChapterProgress 添加索引
  - [x] 2.1.1 添加 completed 字段的 db_index
  - [x] 2.1.2 添加 (enrollment, completed) 复合索引

- [x] 2.2 为 Submission 添加索引
  - [x] 2.2.1 添加 (user, problem, status) 复合索引

- [x] 2.3 为 ProblemProgress 添加索引
  - [x] 2.3.1 为 status 字段添加 db_index=True
  - [x] 2.3.2 添加 (enrollment, status) 复合索引

- [x] 2.4 为 Problem 添加索引
  - [x] 2.4.1 为 chapter 外键添加 db_index=True
  - [x] 2.4.2 添加 (type, -created_at, id) 复合索引

- [x] 2.5 为 ChapterUnlockCondition 添加索引
  - [x] 2.5.1 为 unlock_date 字段添加 db_index=True

- [x] 2.6 为 Course 添加索引
  - [x] 2.6.1 为 title 字段添加 db_index=True

- [x] 2.7 清理 ExamSubmission 重复索引
  - [x] 2.7.1 移除与 unique_together 重复的 (exam, user) 索引

## 3. 生成和应用迁移

- [x] 3.1 生成迁移文件
  - [x] 3.1.1 运行 `python manage.py makemigrations courses`
  - [x] 3.1.2 检查迁移文件内容

- [x] 3.2 在开发环境应用迁移
  - [x] 3.2.1 运行 `python manage.py migrate courses`
  - [x] 3.2.2 验证数据库结构变更

## 4. 性能验证

- [ ] 4.1 使用 EXPLAIN ANALYZE 验证索引使用情况
  - [ ] 4.1.1 验证 ChapterProgress 查询索引
  - [ ] 4.1.2 验证 Submission 查询索引
  - [ ] 4.1.3 验证 ProblemProgress 查询索引
  - [ ] 4.1.4 验证 Problem 查询索引

- [ ] 4.2 执行性能基准测试
  - [ ] 4.2.1 测试索引创建前后的查询性能
  - [ ] 4.2.2 记录响应时间改善情况

- [ ] 4.3 运行单元测试
  - [ ] 4.3.1 运行 `python manage.py test courses`
  - [ ] 4.3.2 确保所有测试通过

## 5. 测试环境部署

- [ ] 5.1 将迁移文件提交到版本控制
- [ ] 5.2 在测试环境部署变更
- [ ] 5.3 使用生产级数据量测试

## 6. 生产环境部署

- [ ] 6.1 选择部署时间窗口（低峰期）
- [ ] 6.2 执行生产环境迁移
- [ ] 6.3 监控数据库性能指标
- [ ] 6.4 验证应用正常运行