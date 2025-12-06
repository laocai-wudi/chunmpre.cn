# -*- coding: utf-8 -*-
"""
表单定义模块
包含登录表单、产品表单等
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, Category


class LoginForm(FlaskForm):
    """
    登录表单
    """
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')


class CategoryForm(FlaskForm):
    """
    分类表单
    """
    name = StringField('分类名称', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('分类描述')
    
    def validate_name(self, name):
        """
        验证分类名称是否已存在
        注意：编辑时应该排除当前分类
        """
        # 如果表单有obj属性（编辑模式），排除当前分类
        if hasattr(self, 'obj') and self.obj:
            category = Category.query.filter(
                Category.name == name.data,
                Category.id != self.obj.id
            ).first()
        else:
            category = Category.query.filter_by(name=name.data).first()
        
        if category:
            raise ValidationError('该分类名称已存在')


class ProductForm(FlaskForm):
    """
    产品表单
    """
    name = StringField('产品名称', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('产品描述', render_kw={'rows': 5})
    brand = StringField('品牌', validators=[Optional(), Length(max=100)])
    
    # 价格相关
    price = DecimalField('价格（单一价格）', validators=[Optional()], places=2)
    price_min = DecimalField('最低价格', validators=[Optional()], places=2)
    price_max = DecimalField('最高价格', validators=[Optional()], places=2)
    price_note = StringField('价格说明', validators=[Optional(), Length(max=200)], 
                            description='如："根据型号配置"')
    
    # 产品详情
    specifications = TextAreaField('规格参数（旧格式）', validators=[Optional()], 
                                  render_kw={'rows': 4}, 
                                  description='每行一个参数，格式：参数名: 参数值')
    technical_specs = TextAreaField('技术规格（JSON格式）', validators=[Optional()], 
                                   render_kw={'rows': 6},
                                   description='JSON格式：{"品牌": "Taylor Hobson", "型号": "xxx", ...}')
    features = TextAreaField('产品特点（旧格式）', validators=[Optional()], render_kw={'rows': 4})
    advantages = TextAreaField('产品优势列表', validators=[Optional()], 
                              render_kw={'rows': 6},
                              description='每行一个优势，将显示为带勾号的列表')
    applications = TextAreaField('应用场景', validators=[Optional()], render_kw={'rows': 3})
    
    # 评分和评价
    rating = DecimalField('评分（0-5分）', validators=[Optional(), NumberRange(min=0, max=5)], places=2)
    review_count = IntegerField('评价数量', validators=[Optional()], default=0)
    
    # 服务标签
    service_tags = TextAreaField('服务标签', validators=[Optional()], 
                                render_kw={'rows': 3},
                                description='每行一个标签，如：支持全国配送、一年质保服务、终身维护支持')
    
    # 标签页内容
    tab_contents = TextAreaField('标签页内容（JSON格式）', validators=[Optional()], 
                                render_kw={'rows': 8},
                                description='JSON格式：{"详细参数": "内容", "应用案例": "内容", "技术文档": "内容", "用户评价": "内容"}')
    
    category_id = SelectField('所属分类', coerce=int, validators=[DataRequired()])
    main_image = FileField('主图片', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许图片文件')
    ])
    stock = IntegerField('库存', validators=[Optional()], default=0)
    status = BooleanField('是否显示', default=True)
    is_featured = BooleanField('首页推荐', default=False, description='勾选后将在首页产品中心展示（最多6个）')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # 动态加载分类选项
        from flask import current_app
        from app import db
        with current_app.app_context():
            self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


class ProductEditForm(FlaskForm):
    """
    产品编辑表单（允许不更新图片）
    """
    name = StringField('产品名称', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('产品描述', render_kw={'rows': 5})
    brand = StringField('品牌', validators=[Optional(), Length(max=100)])
    
    # 价格相关
    price = DecimalField('价格（单一价格）', validators=[Optional()], places=2)
    price_min = DecimalField('最低价格', validators=[Optional()], places=2)
    price_max = DecimalField('最高价格', validators=[Optional()], places=2)
    price_note = StringField('价格说明', validators=[Optional(), Length(max=200)], 
                            description='如："根据型号配置"')
    
    # 产品详情
    specifications = TextAreaField('规格参数（旧格式）', validators=[Optional()], 
                                  render_kw={'rows': 4}, 
                                  description='每行一个参数，格式：参数名: 参数值')
    technical_specs = TextAreaField('技术规格（JSON格式）', validators=[Optional()], 
                                   render_kw={'rows': 6},
                                   description='JSON格式：{"品牌": "Taylor Hobson", "型号": "xxx", ...}')
    features = TextAreaField('产品特点（旧格式）', validators=[Optional()], render_kw={'rows': 4})
    advantages = TextAreaField('产品优势列表', validators=[Optional()], 
                              render_kw={'rows': 6},
                              description='每行一个优势，将显示为带勾号的列表')
    applications = TextAreaField('应用场景', validators=[Optional()], render_kw={'rows': 3})
    
    # 评分和评价
    rating = DecimalField('评分（0-5分）', validators=[Optional(), NumberRange(min=0, max=5)], places=2)
    review_count = IntegerField('评价数量', validators=[Optional()], default=0)
    
    # 服务标签
    service_tags = TextAreaField('服务标签', validators=[Optional()], 
                                render_kw={'rows': 3},
                                description='每行一个标签，如：支持全国配送、一年质保服务、终身维护支持')
    
    # 标签页内容
    tab_contents = TextAreaField('标签页内容（JSON格式）', validators=[Optional()], 
                                render_kw={'rows': 8},
                                description='JSON格式：{"详细参数": "内容", "应用案例": "内容", "技术文档": "内容", "用户评价": "内容"}')
    
    category_id = SelectField('所属分类', coerce=int, validators=[DataRequired()])
    main_image = FileField('主图片', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许图片文件')
    ])
    stock = IntegerField('库存', validators=[Optional()], default=0)
    status = BooleanField('是否显示')
    is_featured = BooleanField('首页推荐', default=False, description='勾选后将在首页产品中心展示（最多6个）')
    
    def __init__(self, *args, **kwargs):
        super(ProductEditForm, self).__init__(*args, **kwargs)
        # 动态加载分类选项（延迟加载，避免在没有应用上下文时出错）
        from flask import current_app
        from app import db
        with current_app.app_context():
            self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


class ProductImageForm(FlaskForm):
    """
    产品图片表单
    """
    image = FileField('图片', validators=[
        FileRequired('请选择图片'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许图片文件')
    ])
    order = IntegerField('排序', default=0)