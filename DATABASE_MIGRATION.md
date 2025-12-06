# 数据库迁移说明

## 产品表新增字段

为了支持更丰富的产品信息展示，需要在 `products` 表中添加以下新字段：

### 新增字段列表

```sql
-- 品牌
ALTER TABLE products ADD COLUMN brand VARCHAR(100);

-- 价格范围
ALTER TABLE products ADD COLUMN price_min NUMERIC(10, 2);
ALTER TABLE products ADD COLUMN price_max NUMERIC(10, 2);
ALTER TABLE products ADD COLUMN price_note VARCHAR(200);

-- 技术规格（JSON格式）
ALTER TABLE products ADD COLUMN technical_specs TEXT;

-- 产品优势列表（每行一个）
ALTER TABLE products ADD COLUMN advantages TEXT;

-- 评分和评价
ALTER TABLE products ADD COLUMN rating NUMERIC(3, 2);
ALTER TABLE products ADD COLUMN review_count INTEGER DEFAULT 0;

-- 服务标签（JSON格式）
ALTER TABLE products ADD COLUMN service_tags TEXT;

-- 标签页内容（JSON格式）
ALTER TABLE products ADD COLUMN tab_contents TEXT;
```

### 执行迁移

在PostgreSQL数据库中执行以下SQL语句：

```sql
-- 连接到数据库后执行
BEGIN;

-- 添加新字段
ALTER TABLE products ADD COLUMN IF NOT EXISTS brand VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS price_min NUMERIC(10, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS price_max NUMERIC(10, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS price_note VARCHAR(200);
ALTER TABLE products ADD COLUMN IF NOT EXISTS technical_specs TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS advantages TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS service_tags TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tab_contents TEXT;

COMMIT;
```

### 字段说明

1. **brand**: 产品品牌（如：Taylor Hobson）
2. **price_min/price_max**: 价格范围，用于显示"¥ 128,000 - ¥ 368,000"这样的格式
3. **price_note**: 价格说明（如："根据型号配置"）
4. **technical_specs**: 技术规格，JSON格式，用于表格展示
5. **advantages**: 产品优势列表，每行一个优势
6. **rating**: 评分（0-5分）
7. **review_count**: 评价数量
8. **service_tags**: 服务标签，JSON数组格式
9. **tab_contents**: 标签页内容，JSON格式，支持多个标签页

### 注意事项

- 所有新字段都是可选的，不会影响现有数据
- 旧字段（specifications, features等）仍然保留，用于兼容
- 如果使用Flask-Migrate，可以创建迁移文件：

```bash
flask db migrate -m "Add new product fields"
flask db upgrade
```

