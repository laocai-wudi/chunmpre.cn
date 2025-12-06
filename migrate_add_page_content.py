#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：创建page_contents表
执行方法：python migrate_add_page_content.py
"""
import os
import sys
from app import create_app, db

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始执行数据库迁移...")
            print("-" * 50)
            
            # 创建所有表（包括新的page_contents表）
            db.create_all()
            
            print("✅ page_contents 表创建成功")
            print("-" * 50)
            print("✅ 数据库迁移完成！")
            print("\n现在可以在后台管理首页内容了。")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库迁移失败: {str(e)}")
            print("\n如果遇到错误，请检查：")
            print("1. 数据库连接是否正常")
            print("2. 是否有足够的权限执行CREATE TABLE操作")
            print("3. 查看上面的错误信息")
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()

