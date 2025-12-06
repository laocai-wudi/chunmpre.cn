# -*- coding: utf-8 -*-
"""
数据库模型定义
包含Product（产品）、Category（分类）和User（用户）三个主要模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class Category(db.Model):
    """
    产品分类模型
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系：一个分类可以有多个产品
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """
    产品模型
    使用PostgreSQL的BYTEA类型存储图片数据
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # 产品描述
    # 使用BYTEA类型存储主图片
    main_image = db.Column(db.LargeBinary)
    main_image_filename = db.Column(db.String(255))
    main_image_mimetype = db.Column(db.String(100))
    
    # 产品基本信息
    brand = db.Column(db.String(100))  # 品牌
    price = db.Column(db.Numeric(10, 2))  # 产品价格（保留用于兼容）
    price_min = db.Column(db.Numeric(10, 2))  # 最低价格（价格范围）
    price_max = db.Column(db.Numeric(10, 2))  # 最高价格（价格范围）
    price_note = db.Column(db.String(200))  # 价格说明（如"根据型号配置"）
    stock = db.Column(db.Integer, default=0)  # 库存数量
    
    # 产品详情字段
    specifications = db.Column(db.Text)  # 规格参数（旧字段，保留兼容）
    technical_specs = db.Column(db.Text)  # 技术规格（JSON格式，用于表格展示）
    features = db.Column(db.Text)  # 产品特点（旧字段，保留兼容）
    advantages = db.Column(db.Text)  # 产品优势列表（每行一个优势）
    applications = db.Column(db.Text)  # 应用场景
    
    # 评分和评价
    rating = db.Column(db.Numeric(3, 2))  # 评分（0-5分）
    review_count = db.Column(db.Integer, default=0)  # 评价数量
    
    # 服务标签（JSON格式：["支持全国配送", "一年质保服务", "终身维护支持"]）
    service_tags = db.Column(db.Text)  # 服务标签（JSON数组或逗号分隔）
    
    # 标签页内容（JSON格式：{"详细参数": "内容", "应用案例": "内容", ...}）
    tab_contents = db.Column(db.Text)  # 标签页内容（JSON格式）
    
    # 分类外键
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # 产品状态
    status = db.Column(db.Boolean, default=True)  # 是否显示在前台
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系：一个产品可以有多张图片
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def get_service_tags_list(self):
        """获取服务标签列表"""
        import json
        if self.service_tags:
            try:
                return json.loads(self.service_tags)
            except:
                # 如果不是JSON，尝试按逗号分隔
                return [tag.strip() for tag in self.service_tags.split(',') if tag.strip()]
        return []
    
    def get_advantages_list(self):
        """获取产品优势列表"""
        if self.advantages:
            return [adv.strip() for adv in self.advantages.split('\n') if adv.strip()]
        return []
    
    def get_technical_specs_dict(self):
        """获取技术规格字典"""
        import json
        if self.technical_specs:
            try:
                return json.loads(self.technical_specs)
            except:
                return {}
        return {}
    
    def get_tab_contents_dict(self):
        """获取标签页内容字典"""
        import json
        if self.tab_contents:
            try:
                # 尝试解析JSON
                parsed = json.loads(self.tab_contents)
                # 确保返回的是字典
                if isinstance(parsed, dict):
                    return parsed
                else:
                    return {}
            except json.JSONDecodeError as e:
                # JSON解析失败，返回空字典
                print(f"JSON解析错误: {e}, 内容: {self.tab_contents[:100]}")
                return {}
            except Exception as e:
                print(f"解析标签页内容时出错: {e}")
                return {}
        return {}


class ProductImage(db.Model):
    """
    产品图片模型
    用于存储产品的多张图片
    """
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 使用BYTEA类型存储图片数据
    image_data = db.Column(db.LargeBinary)
    filename = db.Column(db.String(255))
    mimetype = db.Column(db.String(100))
    
    # 排序字段
    order = db.Column(db.Integer, default=0)
    
    # 产品外键
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # 注意：product 关系由 Product.images 的 backref 自动创建，不需要在这里重复定义
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductImage {self.filename} for product {self.product_id}>'


class User(UserMixin, db.Model):
    """
    用户模型
    继承UserMixin以支持Flask-Login
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)  # 增加到255以支持scrypt等更长的哈希算法
    
    # 用户角色
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    is_active = db.Column(db.Boolean, default=True)  # 账户是否激活
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    @property
    def password(self):
        """
        密码属性，禁止直接读取
        """
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """
        设置密码时自动哈希加密
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        验证密码是否正确
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Contact(db.Model):
    """
    联系表单模型
    用于存储用户提交的联系信息
    """
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # 状态字段
    is_read = db.Column(db.Boolean, default=False)  # 是否已读
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name} - {self.subject}>'