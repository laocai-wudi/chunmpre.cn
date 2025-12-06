# -*- coding: utf-8 -*-
"""
主应用入口文件
用于创建和配置Flask应用，注册蓝图，初始化数据库
并提供数据库迁移和创建管理员账户的功能
"""
import os
from flask import Flask, render_template
from werkzeug.security import generate_password_hash

# 从config模块导入配置
from config import config

# 导入数据库实例和登录管理器
from app import create_app, db, login_manager
from app.models import User, Category, Product, ProductImage

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command('init-db')
def init_db():
    """
    初始化数据库命令
    使用方法: flask init-db
    创建所有数据库表
    """
    # 删除所有现有表并重新创建
    db.drop_all()
    db.create_all()
    
    # 创建默认分类
    default_categories = [
        {'name': '光学测量仪器'},
        {'name': '坐标测量仪'},
        {'name': '激光干涉仪'},
        {'name': '三坐标测量机'},
        {'name': '影像测量仪'}
    ]
    
    for cat_data in default_categories:
        category = Category(name=cat_data['name'])
        db.session.add(category)
    
    # 提交分类数据
    db.session.commit()
    
    print('数据库初始化完成，已创建默认分类。')


@app.cli.command('create-admin')
def create_admin():
    """
    创建管理员账户命令
    使用方法: flask create-admin
    创建一个默认的管理员账户
    """
    # 检查是否已存在管理员账户
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print('管理员账户已存在！')
        return
    
    # 创建新的管理员账户
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('admin123'),  # 默认密码，生产环境请修改
        is_admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print('管理员账户创建成功！\n用户名: admin\n密码: admin123\n请在首次登录后修改密码！')


@app.cli.command('import-sample-data')
def import_sample_data():
    """
    导入示例产品数据命令
    使用方法: flask import-sample-data
    导入一些示例产品数据，包括从现有文件夹导入图片
    """
    # 检查分类是否存在
    categories = Category.query.all()
    if not categories:
        print('请先运行 flask init-db 初始化数据库和分类！')
        return
    
    # 定义示例产品数据
    sample_products = [
        {
            'name': '高精度三坐标测量机',
            'description': '本产品采用先进的测量技术，提供高精度的三维坐标测量，广泛应用于机械制造、航空航天等领域。测量精度可达0.001mm，支持多种测量模式和数据导出格式。',
            'category_id': categories[3].id,  # 三坐标测量机分类
            'price': 128000.00,
            'stock': 5,
            'status': True,
            'image_path': 'instrument-images/sanzuobiao.jpg'
        },
        {
            'name': 'FANUC加工中心',
            'description': '日本原装进口FANUC加工中心，高精度、高效率的数控加工设备，适用于复杂零件的精密加工。配备先进的控制系统和自动换刀系统，可实现24小时不间断生产。',
            'category_id': categories[0].id,  # 光学测量仪器分类
            'price': 356000.00,
            'stock': 3,
            'status': True,
            'image_path': 'instrument-images/FANUC.jpg'
        },
        {
            'name': '泰勒霍普森圆度仪',
            'description': '英国泰勒霍普森公司生产的高精度圆度仪，用于测量旋转零件的圆度、圆柱度、同轴度等几何误差。配备专业测量软件，支持数据统计分析和报告生成。',
            'category_id': categories[1].id,  # 坐标测量仪分类
            'price': 89000.00,
            'stock': 2,
            'status': True,
            'image_path': 'instrument-images/TAYLOR HOBSON.png'
        },
        {
            'name': 'TRIOPTICS光学测量系统',
            'description': '德国TRIOPTICS公司生产的光学元件测量系统，用于测量透镜、棱镜等光学元件的面型、曲率、中心厚度等参数。采用非接触式测量方法，保证测量精度和效率。',
            'category_id': categories[0].id,  # 光学测量仪器分类
            'price': 218000.00,
            'stock': 1,
            'status': True,
            'image_path': 'instrument-images/TRIOPTICS.png'
        },
        {
            'name': 'UA3P全自动影像测量仪',
            'description': 'UA3P系列全自动影像测量仪，采用高精度光学系统和数控平台，可实现二维尺寸的快速精确测量。支持自动对焦、自动识别和批量测量，提高检测效率。',
            'category_id': categories[4].id,  # 影像测量仪分类
            'price': 76500.00,
            'stock': 4,
            'status': True,
            'image_path': 'instrument-images/UA3P.jpg'
        },
        {
            'name': '数控车床',
            'description': '高精度数控车床，适用于轴类、盘类零件的加工。配备高性能数控系统和精密主轴，保证加工精度和表面质量。支持多种编程方式和自动化操作。',
            'category_id': categories[3].id,  # 三坐标测量机分类
            'price': 98000.00,
            'stock': 6,
            'status': True,
            'image_path': 'instrument-images/chechuang.jpg'
        }
    ]
    
    # 导入产品数据和图片
    imported_count = 0
    for prod_data in sample_products:
        # 检查产品是否已存在
        existing_product = Product.query.filter_by(name=prod_data['name']).first()
        if existing_product:
            print(f'产品「{prod_data["name"]}」已存在，跳过导入。')
            continue
        
        # 读取图片数据
        image_path = os.path.join(app.root_path, '..', prod_data['image_path'])
        main_image_data = None
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    main_image_data = f.read()
            except Exception as e:
                print(f'读取图片「{image_path}」出错: {str(e)}')
        
        # 创建产品
        product = Product(
            name=prod_data['name'],
            description=prod_data['description'],
            category_id=prod_data['category_id'],
            main_image=main_image_data,
            price=prod_data['price'],
            stock=prod_data['stock'],
            status=prod_data['status']
        )
        
        db.session.add(product)
        imported_count += 1
    
    # 提交数据
    db.session.commit()
    
    print(f'示例数据导入完成，共导入 {imported_count} 个产品。')


@app.cli.command('db-migrate')
def db_migrate():
    """
    数据库迁移命令
    使用方法: flask db-migrate
    更新数据库表结构以匹配模型定义
    """
    # 由于我们使用的是简单的SQLAlchemy方式，直接使用drop_all和create_all
    # 在生产环境中，应考虑使用Flask-Migrate进行更复杂的数据库迁移
    try:
        # 只创建不存在的表，不删除现有表
        db.create_all()
        print('数据库表结构更新完成。')
    except Exception as e:
        print(f'数据库迁移失败: {str(e)}')


# 添加在文件的适当位置，通常在所有蓝图注册之后

@app.errorhandler(404)
def page_not_found(error):
    """处理404错误（页面未找到）"""
    return render_template('frontend/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """处理500错误（服务器内部错误）"""
    # 在生产环境中，我们可以在这里记录错误日志
    return render_template('frontend/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):    
    """处理403错误（禁止访问）"""
    return render_template('frontend/404.html'), 403


if __name__ == '__main__':
    # 开发环境运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)