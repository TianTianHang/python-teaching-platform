# 分离缓存运维文档

## 系统架构

### 缓存服务

- **缓存系统**: Redis 7.x
- **最大内存**: 4GB
- **驱逐策略**: allkeys-lru
- **持久化**: RDB + AOF

### 应用层

- **Django**: 4.2+
- **Python**: 3.13
- **Django-Redis**: 5.x

## 部署检查清单

### 部署前准备

- [ ] 确认Redis版本 >= 7.0
- [ ] 确认Redis内存 >= 4GB
- [ ] 确认Redis持久化已启用
- [ ] 备份现有Redis数据
- [ ] 准备回滚方案

### 部署步骤

1. **代码部署**
   ```bash
   # 拉取最新代码
   git pull origin main
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 运行迁移
   python manage.py migrate
   ```

2. **Redis配置检查**
   ```bash
   # 检查Redis配置
   redis-cli CONFIG GET maxmemory
   redis-cli CONFIG GET maxmemory-policy
   redis-cli INFO memory
   ```

3. **重启服务**
   ```bash
   # 重启Django应用
   supervisorctl restart python-teaching-platform
   
   # 或使用systemd
   systemctl restart gunicorn
   ```

4. **验证部署**
   ```bash
   # 检查应用日志
   tail -f /var/log/gunicorn/access.log
   
   # 检查Redis连接
   redis-cli PING
   ```

## 监控指标

### 关键指标

#### 1. 缓存命中率

```bash
# 监控命令
redis-cli INFO stats | grep keyspace_hits

# 计算命中率
hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses) * 100%

# 目标值
全局数据缓存命中率: > 90%
用户状态缓存命中率: > 80%
```

#### 2. 内存使用

```bash
# 监控命令
redis-cli INFO memory

# 关键指标
used_memory_human: 当前内存使用
used_memory_peak: 峰值内存使用
maxmemory: 最大内存限制

# 目标值
内存使用率: < 80%
内存碎片率: < 1.5
```

#### 3. 缓存条目数

```bash
# 监控命令
redis-cli DBSIZE

# 按前缀统计
redis-cli --scan --pattern "chapter:global:*" | wc -l
redis-cli --scan --pattern "chapter:status:*" | wc -l
redis-cli --scan --pattern "problem:global:*" | wc -l
redis-cli --scan --pattern "problem:status:*" | wc -l

# 目标值
总缓存条目: < 0.1% of old strategy
```

#### 4. 响应时间

```python
# 应用层监控
from prometheus_client import Histogram

cache_response_time = Histogram(
    'cache_response_seconds',
    'Cache response time',
    ['cache_type']
)

# 目标值
全局缓存命中: < 5ms
用户状态缓存命中: < 5ms
缓存未命中: < 50ms
```

### 告警规则

```yaml
# Prometheus告警规则示例
groups:
  - name: cache_alerts
    rules:
      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.7
        for: 5m
        annotations:
          summary: "缓存命中率过低"
          
      - alert: HighMemoryUsage
        expr: redis_memory_usage > 0.9
        for: 5m
        annotations:
          summary: "Redis内存使用率过高"
          
      - alert: SlowResponseTime
        expr: cache_response_time > 0.1
        for: 5m
        annotations:
          summary: "缓存响应时间过长"
```

## 日常运维

### 日志监控

```bash
# 查看应用日志
tail -f /var/log/gunicorn/error.log | grep -i cache

# 关键日志模式
- "Global cache miss"
- "Global cache hit"
- "User status cache invalidated"
- "Cache error"
```

### 性能分析

```bash
# Redis慢查询
redis-cli SLOWLOG GET 10

# 查看大键
redis-cli --bigkeys

# 查看热点键
redis-cli --hotkeys
```

### 缓存清理

#### 手动清理特定缓存

```bash
# 清理特定课程的全局缓存
redis-cli DEL "chapter:global:list:{course_id}"

# 清理特定用户的状态缓存
redis-cli DEL "chapter:status:{course_id}:{user_id}"

# 清理匹配模式的所有缓存
redis-cli --scan --pattern "chapter:global:list:*" | xargs redis-cli DEL
```

#### 批量清理

```python
# Python脚本批量清理
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# 清理所有章节列表缓存
keys = r.keys('chapter:global:list:*')
if keys:
    r.delete(*keys)
    print(f"Deleted {len(keys)} keys")
```

### TTL调整

```bash
# 查看当前TTL
redis-cli TTL "chapter:global:123"

# 动态调整TTL
redis-cli EXPIRE "chapter:global:123" 3600  # 改为1小时
```

## 故障排查

### 问题1：缓存命中率低

**症状**：
- keyspace_hits / (keyspace_hits + keyspace_misses) < 70%
- 数据库查询频繁

**诊断**：
```bash
# 检查缓存键是否存在
redis-cli GETS "chapter:global:123" "problem:global:456"

# 检查TTL是否过短
redis-cli TTL "chapter:global:123"

# 检查内存是否不足
redis-cli INFO memory | grep used_memory
```

**解决方案**：
1. 增加TTL时间
2. 增加Redis内存
3. 优化缓存键设计
4. 检查是否有大量缓存失效

### 问题2：内存使用过高

**症状**：
- Redis内存使用率 > 90%
- 频繁驱逐缓存

**诊断**：
```bash
# 查看内存使用
redis-cli INFO memory

# 查看大键
redis-cli --bigkeys

# 查看键数量
redis-cli DBSIZE
```

**解决方案**：
1. 清理不必要的缓存
2. 优化TTL设置
3. 增加Redis内存
4. 分析是否有内存泄漏

### 问题3：数据不一致

**症状**：
- 用户看到过期数据
- 状态更新不生效

**诊断**：
```python
# 检查信号处理器
import logging
logger = logging.getLogger('courses.signals')

# 查看信号日志
logger.setLevel(logging.DEBUG)

# 检查缓存失效
redis-cli GET "chapter:status:5:1001"
```

**解决方案**：
1. 检查信号处理器是否正常
2. 手动清除相关缓存
3. 检查TTL设置
4. 重启应用服务

### 问题4：响应时间过长

**症状**：
- API响应时间 > 100ms
- 用户投诉慢

**诊断**：
```bash
# 检查Redis响应时间
redis-cli --latency

# 检查网络延迟
ping redis-server

# 检查应用日志
grep "cache.*duration" /var/log/gunicorn/access.log
```

**解决方案**：
1. 优化网络连接
2. 使用Redis Pipeline
3. 优化查询逻辑
4. 增加缓存容量

## 备份与恢复

### Redis备份

```bash
# RDB快照备份
redis-cli BGSAVE

# 查看备份文件
ls -lh /var/lib/redis/dump.rdb

# 远程备份
scp /var/lib/redis/dump.rdb backup-server:/backups/
```

### 缓存预热

```python
# 缓存预热脚本
from courses.models import Chapter, Course
from django.core.cache import cache
from courses.serializers import ChapterGlobalSerializer

def warmup_cache():
    """预热常用缓存"""
    # 预热所有课程的全局数据
    courses = Course.objects.all()
    
    for course in courses:
        chapters = Chapter.objects.filter(course=course)
        global_data = ChapterGlobalSerializer(chapters, many=True).data
        
        cache_key = f"chapter:global:list:{course.id}"
        cache.set(cache_key, global_data, timeout=1800)
        
        print(f"Warmed up cache for course {course.id}")

if __name__ == "__main__":
    warmup_cache()
```

## 性能优化

### Redis优化

```bash
# 禁用THP（Transparent Huge Pages）
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# 调整maxmemory-policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 启用持久化
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### 应用优化

```python
# 使用连接池
CACHE_POOL = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50
)

# 使用Pipeline
pipe = cache.client.pipeline()
for i in range(100):
    pipe.get(f"key:{i}")
results = pipe.execute()
```

## 安全建议

### 访问控制

```bash
# 设置Redis密码
redis-cli CONFIG SET requirepass "your-strong-password"

# 绑定特定IP
redis-cli CONFIG SET bind "127.0.0.1"

# 禁用危险命令
redis-cli CONFIG SET rename-command FLUSHDB ""
redis-cli CONFIG SET rename-command FLUSHALL ""
```

### 网络安全

```bash
# 使用防火墙限制访问
iptables -A INPUT -p tcp --dport 6379 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP

# 启用TLS（生产环境推荐）
stunnel配置...
```

## 应急预案

### Redis宕机

**症状**：Redis服务不可用

**影响**：所有缓存失效，降级到数据库查询

**应急步骤**：
1. 检查Redis状态
   ```bash
   systemctl status redis
   ```
2. 尝试重启Redis
   ```bash
   systemctl restart redis
   ```
3. 检查日志
   ```bash
   tail -f /var/log/redis/redis.log
   ```
4. 应用自动降级到数据库查询

### 缓存雪崩

**症状**：大量缓存同时失效，数据库压力骤增

**预防措施**：
1. TTL增加随机值
   ```python
   import random
   ttl = 1800 + random.randint(-300, 300)  # 30分钟 ± 5分钟
   ```
2. 使用互斥锁
   ```python
   if cache.add(lock_key, "1", nx=True, ex=10):
       data = db_query()
       cache.set(key, data, ttl)
   ```
3. 限流保护
   ```python
   from django.core.cache import cache
   from rest_framework.throttling import UserRateThrottle
   ```

### 缓存穿透

**症状**：恶意请求不存在的数据，绕过缓存直接查数据库

**预防措施**：
1. 布隆过滤器
   ```python
   from pybloom_live import ScalableBloomFilter
   bloom = ScalableBloomFilter()
   bloom.add("chapter:123")  # 添加存在的ID
   ```
2. 空值缓存
   ```python
   if data is None:
       cache.set(key, NULL_VALUE, timeout=60)
   ```
3. 请求参数校验

## 维护窗口

### 定期维护任务

| 任务 | 频率 | 时间窗口 |
|------|------|---------|
| Redis RDB备份 | 每日 | 02:00-04:00 |
| 缓存键清理 | 每周 | 周日 03:00-05:00 |
| 性能分析 | 每周 | 周一 09:00-10:00 |
| 容量规划 | 每月 | 第一周周一 |

### 维护脚本

```bash
#!/bin/bash
# cache_maintenance.sh

echo "Starting cache maintenance..."

# 1. 清理过期缓存
redis-cli --scan --pattern "chapter:*" | \
  xargs -I {} sh -c 'redis-cli TTL {} | awk "{if(\$1<60) print \}" | xargs redis-cli DEL'

# 2. 备份Redis
redis-cli BGSAVE

# 3. 分析内存使用
redis-cli INFO memory > /var/log/redis/memory_$(date +%Y%m%d).log

# 4. 清理慢查询日志
redis-cli SLOWLOG RESET

echo "Cache maintenance completed."
```

## 相关文档

- [API文档](./separated-cache-api.md)
- [缓存策略文档](./separated-cache-strategy.md)
- [部署文档](../deployment.md)
