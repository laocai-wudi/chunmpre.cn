#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为products表添加新字段
执行方法：python migrate_add_product_fields.py
"""
import os
import sys
from sqlalchemy import text
from app import create_app, db

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在，如果不存在则添加
            migrations = [
                ("brand", "ALTER TABLE products ADD COLUMN IF NOT EXISTS brand VARCHAR(100);"),
                ("price_min", "ALTER TABLE products ADD COLUMN IF NOT EXISTS price_min NUMERIC(10, 2);"),
                ("price_max", "ALTER TABLE products ADD COLUMN IF NOT EXISTS price_max NUMERIC(10, 2);"),
                ("price_note", "ALTER TABLE products ADD COLUMN IF NOT EXISTS price_note VARCHAR(200);"),
                ("technical_specs", "ALTER TABLE products ADD COLUMN IF NOT EXISTS technical_specs TEXT;"),
                ("advantages", "ALTER TABLE products ADD COLUMN IF NOT EXISTS advantages TEXT;"),
                ("rating", "ALTER TABLE products ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 2);"),
                ("review_count", "ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;"),
                ("service_tags", "ALTER TABLE products ADD COLUMN IF NOT EXISTS service_tags TEXT;"),
                ("tab_contents", "ALTER TABLE products ADD COLUMN IF NOT EXISTS tab_contents TEXT;"),
            ]
            
            print("开始执行数据库迁移...")
            print("-" * 50)
            
            for field_name, sql in migrations:
                try:
                    # 执行SQL语句
                    db.session.execute(text(sql))
                    print(f"✅ 字段 '{field_name}' 添加成功")
                except Exception as e:
                    # 如果字段已存在或其他错误，继续执行
                    error_msg = str(e)
                    if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                        print(f"⚠️  字段 '{field_name}' 已存在，跳过")
                    else:
                        print(f"❌ 字段 '{field_name}' 添加失败: {error_msg}")
            
            # 提交事务
            db.session.commit()
            print("-" * 50)
            print("✅ 数据库迁移完成！")
            print("\n现在可以在后台编辑产品时使用新字段了。")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库迁移失败: {str(e)}")
            print("\n如果遇到错误，请检查：")
            print("1. 数据库连接是否正常")
            print("2. 是否有足够的权限执行ALTER TABLE操作")
            print("3. 查看上面的错误信息")
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()

