#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为products表添加is_featured字段
执行方法：python migrate_add_is_featured.py
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
            # 添加is_featured字段
            sql = "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;"
            
            print("开始执行数据库迁移...")
            print("-" * 50)
            
            try:
                # 执行SQL语句
                db.session.execute(text(sql))
                print("✅ 字段 'is_featured' 添加成功")
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print("⚠️  字段 'is_featured' 已存在，跳过")
                else:
                    print(f"❌ 字段 'is_featured' 添加失败: {error_msg}")
                    raise
            
            # 提交事务
            db.session.commit()
            print("-" * 50)
            print("✅ 数据库迁移完成！")
            print("\n现在可以在后台设置产品的首页推荐状态了。")
            
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

