# 项目 Key (Project Key) 说明

## 什么是项目 Key？

项目 Key 是项目的**唯一标识符**，通常是一个简短的大写字母缩写（如 `PROJ`, `BUG`, `TEST` 等）。

## 主要作用

### 1. 生成缺陷唯一编号（Bug Key）

这是项目 Key 最重要的作用！

**生成规则：** `{项目Key}-{序号}`

**示例：**
- 项目 Key：`DMTEST`
- 第一个缺陷：`DMTEST-0001`
- 第二个缺陷：`DMTEST-0002`
- 第 100 个缺陷：`DMTEST-0100`

**代码实现：**

```python
def generate_bug_key(db: Session, project_id: int) -> str:
    """生成缺陷唯一Key"""
    # 1. 获取项目信息（包含项目 key）
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    # 2. 获取该项目下的最后一个缺陷
    last_bug = db.query(models.Bug).filter(
        models.Bug.project_id == project_id
    ).order_by(models.Bug.id.desc()).first()
    
    # 3. 计算下一个序号
    number = 1
    if last_bug and last_bug.bug_key:
        parts = last_bug.bug_key.split('-')
        if len(parts) == 2:
            number = int(parts[1]) + 1
    
    # 4. 拼接：项目Key-序号（4位，不足补0）
    return f"{project.key}-{number:04d}"
```

### 2. 快速识别缺陷所属项目

通过 Bug Key，一眼就能看出缺陷属于哪个项目：

- `DMTEST-0001` → 属于 DMTEST 项目
- `AUTH-0123` → 属于 AUTH 项目
- `API-0001` → 属于 API 项目

### 3. 便于沟通和引用

在日常工作中，团队成员可以直接说：
- "我修复了 **DMTEST-0001**"
- "**API-0123** 的问题需要优先处理"
- "请看一下 **AUTH-0045** 的重现步骤"

比说"ID为123的缺陷"更直观和专业。

### 4. 跨系统追溯

- 在代码提交消息中：`fix: DMTEST-0001 修复登录问题`
- 在 Jira/禅道等其他系统中导入导出时保持一致性
- 在文档中引用：更易读易记

## 命名建议

### ✅ 好的项目 Key 命名

- **简短**：2-10 个字符
- **大写**：`PROJ`, `BUG`, `TEST`
- **有意义**：
  - `DM` - 鼎茂
  - `AUTH` - 认证系统
  - `API` - API 项目
  - `WEB` - Web 前端
  - `MOBILE` - 移动端
  
### ❌ 不好的项目 Key 命名

- 太长：`VERYLONGPROJECTNAME`
- 无意义：`PROJ1`, `TEST123`
- 小写或混合：`proj`, `Test`
- 包含特殊字符：`PROJ-1`, `TEST_A`

## 数据库结构

### projects 表

```sql
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '项目名称',
    key VARCHAR(20) UNIQUE NOT NULL COMMENT '项目Key（唯一标识）',
    description TEXT COMMENT '项目描述',
    lead VARCHAR(50) COMMENT '项目负责人',
    status ENUM('active', 'archived') DEFAULT 'active',
    ...
);
```

**约束：**
- `key` 必须唯一（UNIQUE）
- `key` 有索引（INDEX）- 用于快速查询

### bugs 表

```sql
CREATE TABLE bugs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bug_key VARCHAR(30) UNIQUE NOT NULL COMMENT '缺陷唯一编号',
    project_id INT NOT NULL COMMENT '所属项目ID',
    title VARCHAR(200) NOT NULL,
    ...
);
```

**约束：**
- `bug_key` 全局唯一（UNIQUE）
- `bug_key` 有索引（INDEX）- 用于快速查询
- 格式：`{项目Key}-{4位序号}`

## 使用示例

### 创建项目时指定 Key

```bash
curl -X POST http://localhost:43211/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "鼎茂测试项目",
    "key": "DMTEST",
    "description": "这是一个测试项目",
    "lead": "admin",
    "status": "active"
  }'
```

### 创建缺陷时自动生成 Bug Key

```bash
curl -X POST http://localhost:43211/api/bugs \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "登录页面报错",
    "reporter_id": 1,
    "priority": "major",
    "status": "open"
  }'

# 返回：
# {
#   "bug_key": "DMTEST-0001",  ← 自动生成
#   "title": "登录页面报错",
#   ...
# }
```

### 通过 Bug Key 查询缺陷

```bash
# 方式1: 通过 bug_key 过滤
GET /api/bugs?search=DMTEST-0001

# 方式2: 直接通过 bug_key 获取（如果实现了）
GET /api/bugs/by-key/DMTEST-0001
```

## 与 Jira 的对比

本系统的项目 Key 机制参考了 Jira 的设计：

| 系统 | 项目 Key | Bug Key 格式 | 示例 |
|------|----------|--------------|------|
| **本系统** | 用户自定义（2-20字符） | `{KEY}-{序号}` | `DMTEST-0001` |
| **Jira** | 用户自定义（2-10字符） | `{KEY}-{序号}` | `PROJ-123` |
| **禅道** | 无 Key 概念 | 纯数字 ID | `#12345` |
| **GitHub Issues** | 仓库名 | `#{序号}` | `owner/repo#123` |

## 常见问题

### Q1: 项目 Key 可以修改吗？

**不建议修改！** 因为：
- 所有已生成的 Bug Key 都基于项目 Key
- 修改后会导致 Bug Key 格式不一致
- 如果一定要改，需要同时更新所有相关的 Bug Key

### Q2: 不同项目的 Bug 编号会冲突吗？

**不会！** 因为 Bug Key 包含项目 Key 前缀：
- 项目 A (Key: `PROJA`)：`PROJA-0001`, `PROJA-0002`
- 项目 B (Key: `PROJB`)：`PROJB-0001`, `PROJB-0002`

每个项目的序号独立计数。

### Q3: 如果删除了某个 Bug，编号会复用吗？

**不会复用！** 序号只增不减：
- 创建 `DMTEST-0001`
- 创建 `DMTEST-0002`
- 删除 `DMTEST-0002`
- 下次创建仍然是 `DMTEST-0003`

这样可以：
- 避免混淆
- 保持历史记录的完整性
- 符合审计要求

### Q4: 序号会用完吗？

**几乎不可能！** 使用 4 位序号（0001-9999）：
- 每个项目最多 9999 个缺陷
- 如果不够，可以修改代码增加位数（如 `{:05d}` 变为 5 位）

## 总结

项目 Key 的核心价值：

1. ✅ **生成有意义的缺陷编号**（最重要）
2. ✅ **便于识别和沟通**
3. ✅ **符合行业标准**（Jira 同款）
4. ✅ **支持跨系统追溯**

建议在创建项目时，认真选择一个简短、有意义的项目 Key，因为它会伴随整个项目的生命周期！

