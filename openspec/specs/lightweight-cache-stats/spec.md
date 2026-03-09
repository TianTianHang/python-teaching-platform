# lightweight-cache-stats Specification

## Purpose
TBD - created by archiving change lightweight-cache-stats. Update Purpose after archive.
## Requirements
### Requirement: 缓存统计轻量化
缓存操作（get/set）不应该因为过度统计而导致性能下降。正常情况下（< 100ms）不应触发任何 Redis 写入或详细日志。

#### Scenario: 正常缓存命中
- **WHEN** 缓存命中且操作时间 < 100ms
- **THEN** 只返回缓存数据，不进行任何 Redis 统计写入

#### Scenario: 慢缓存操作
- **WHEN** 缓存操作时间 >= 100ms
- **THEN** 记录详细日志到 cache.log，记录 Redis 统计（采样或异步）

### Requirement: 保留基本监控能力
仍需保留基本的监控能力用于容量规划和问题排查。

#### Scenario: Prometheus 计数
- **WHEN** 缓存操作发生时
- **THEN** Prometheus counter.inc() 正常执行（内存操作，开销可忽略）

#### Scenario: 采样统计
- **WHEN** 需要统计时（慢操作或定期采样）
- **THEN** 使用采样（如 10%）或异步批量写入 Redis，避免每次请求都触发 Redis 往返

