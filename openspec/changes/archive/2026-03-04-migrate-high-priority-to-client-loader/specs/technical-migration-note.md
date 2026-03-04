# 技术迁移说明

本变更是纯技术迁移，不涉及新功能或需求变更，因此不需要创建 spec 文件。

所有变更均为实现细节重构：
- 将 useEffect + clientHttp 迁移到 clientLoader
- 不改变任何 API 接口或用户可见行为
- 不涉及需求规范变更