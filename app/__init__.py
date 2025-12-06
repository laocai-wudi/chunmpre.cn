# -*- coding: utf-8 -*-
"""
应用初始化文件
用于创建Flask应用实例，初始化数据库连接，注册蓝图等
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# 创建数据库实例
db = SQLAlchemy()

# 创建登录管理器实例
login_manager = LoginManager()
# 设置登录视图，当未登录用户访问需要认证的页面时，会重定向到这个视图
login_manager.login_view = 'auth.login'
# 设置登录消息类别
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    """
    创建Flask应用实例的工厂函数
    
    Args:
        config_name: 配置名称，默认为None，会根据环境变量FLASK_CONFIG或使用default
    
    Returns:
        Flask: 配置好的Flask应用实例
    """
    # 导入需要的模型类
    from app.models import User, Category
    
    # 如果没有提供配置名称，从环境变量获取或使用默认配置
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 从配置对象加载配置
    app.config.from_object(config[config_name])
    
    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager.init_app(app)
    
    # 注册蓝图
    # 导入蓝图并注册
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # 注册认证蓝图
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # 注册管理员蓝图
    from app.admin import admin_bp as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # 注册CLI命令
    register_cli_commands(app)
    
    return app


def register_cli_commands(app):
    """注册Flask CLI命令"""
    from werkzeug.security import generate_password_hash
    from app.models import User, Category, Product, ProductImage
    import os
    
    @app.cli.command('init-db')
    def init_db():
        """初始化数据库命令"""
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
        """创建管理员账户命令"""
        # 检查是否已存在管理员账户
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print('管理员账户已存在！')
            return
        
        # 创建新的管理员账户
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        # 使用 password 属性会自动哈希，不要手动使用 generate_password_hash
        admin.password = 'admin123'
        
        db.session.add(admin)
        db.session.commit()
        
        print('管理员账户创建成功！\n用户名: admin\n密码: admin123\n请在首次登录后修改密码！')
    
    @app.cli.command('import-sample-data')
    def import_sample_data():
        """导入示例产品数据命令"""
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
        """数据库迁移命令"""
        try:
            # 只创建不存在的表，不删除现有表
            db.create_all()
            print('数据库表结构更新完成。')
        except Exception as e:
            print(f'数据库迁移失败: {str(e)}')


def init_db():
    """
    初始化数据库
    创建所有表并添加默认数据
    """
    db.create_all()
    
    # 检查是否已有默认分类
    if Category.query.count() == 0:
        # 创建默认分类
        default_categories = [
            {'name': '精密测量仪器', 'description': '各类精密测量设备'},
            {'name': '机械加工设备', 'description': '各种机械加工工具'},
            {'name': '维修配件', 'description': '各类设备维修所需配件'}
        ]
        
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        print('默认分类已创建')
    
    # 检查是否已有默认管理员
    if User.query.count() == 0:
        # 创建默认管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.password = 'admin123'  # 设置默认密码
        
        db.session.add(admin)
        db.session.commit()
        print('默认管理员已创建：用户名=admin，密码=admin123')
    
    print('数据库初始化完成')


@login_manager.user_loader
def load_user(user_id):
    """
    登录管理器的用户加载回调函数
    当用户登录后，Flask-Login会通过这个函数加载用户对象
    
    Args:
        user_id: 用户ID
    
    Returns:
        User: 用户对象，如果不存在返回None
    """
    from app.models import User
    return User.query.get(int(user_id))