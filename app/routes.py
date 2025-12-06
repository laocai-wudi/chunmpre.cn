# -*- coding: utf-8 -*-
"""
前台路由模块
处理网站前台页面的访问和数据展示
"""
from flask import Blueprint, render_template, request, send_file, redirect, url_for, current_app
from io import BytesIO

from app import db
from app.models import Product, Category, ProductImage, Contact, PageContent
import os
import uuid
from werkzeug.utils import secure_filename

# 创建主蓝图
main = Blueprint('main', __name__)


def save_product_image(image_file):
    """
    保存产品图片到指定目录
    返回图片的相对路径
    """
    # 获取文件名并确保安全
    filename = secure_filename(image_file.filename)
    
    # 生成唯一文件名
    unique_filename = str(uuid.uuid4()) + '_' + filename
    
    # 确保上传目录存在
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 保存文件
    image_path = os.path.join(upload_dir, unique_filename)
    image_file.save(image_path)
    
    # 返回相对路径
    return os.path.join('uploads', 'products', unique_filename)


def delete_product_image(image_path):
    """
    删除指定路径的产品图片
    """
    # 构建完整的文件路径
    full_path = os.path.join(current_app.root_path, 'static', image_path)
    
    # 检查文件是否存在，存在则删除
    if os.path.exists(full_path):
        os.remove(full_path)


def allowed_file(filename):
    """
    检查文件类型是否允许
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    """
    网站首页
    展示公司信息、产品分类和部分产品
    """
    # 获取所有分类
    categories = Category.query.order_by(Category.created_at).all()
    
    # 获取首页推荐产品（最多6个）
    featured_products = Product.query.filter_by(status=True, is_featured=True).order_by(Product.created_at.desc()).limit(6).all()
    # 如果推荐产品不足6个，用最新产品补充
    if len(featured_products) < 6:
        remaining_count = 6 - len(featured_products)
        featured_ids = [p.id for p in featured_products]
        additional_products = Product.query.filter_by(status=True).filter(~Product.id.in_(featured_ids if featured_ids else [0])).order_by(Product.created_at.desc()).limit(remaining_count).all()
        featured_products = list(featured_products) + additional_products
    
    # 获取页面内容
    page_content = {}
    for key in ['home_hero_title', 'home_hero_description', 'home_hero_image',
                'home_about_title', 'home_about_subtitle', 'home_about_description', 'home_about_image',
                'home_about_intro_title', 'home_about_intro_text',
                'home_services_title', 'home_services_subtitle',
                'home_services_results_title', 'home_services_results_subtitle',
                'home_contact_title', 'home_contact_subtitle']:
        page_content[key] = PageContent.get_content(key)
    
    # 获取JSON格式的内容
    import json
    page_content['home_hero_stats'] = PageContent.get_content('home_hero_stats', '[]')
    page_content['home_about_features'] = PageContent.get_content('home_about_features', '[]')
    page_content['home_services_list'] = PageContent.get_content('home_services_list', '[]')
    page_content['home_services_results_images'] = PageContent.get_content('home_services_results_images', '[]')
    page_content['home_contact_info'] = PageContent.get_content('home_contact_info', '{}')
    
    # 获取图片内容对象（用于获取ID）
    hero_image_content = PageContent.query.filter_by(page_key='home_hero_image').first()
    about_image_content = PageContent.query.filter_by(page_key='home_about_image').first()
    page_content['home_hero_image_id'] = hero_image_content.id if hero_image_content and hero_image_content.image_data else None
    page_content['home_about_image_id'] = about_image_content.id if about_image_content and about_image_content.image_data else None
    
    return render_template('frontend/index.html', 
                         categories=categories,
                         featured_products=featured_products,
                         page_content=page_content)


@main.route('/about')
def about():
    """
    关于我们页面 - 重定向到首页的关于我们部分
    """
    return redirect(url_for('main.index') + '#about')


@main.route('/products')
def products():
    """
    产品列表页面
    支持按分类筛选和分页
    """
    from flask import request
    from sqlalchemy import or_
    
    # 获取所有分类
    categories = Category.query.order_by(Category.created_at).all()
    
    # 获取分类ID参数
    category_id = request.args.get('category', type=int)
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 9  # 每页显示9个产品
    
    # 构建查询
    query = Product.query.filter_by(status=True)
    
    # 按分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)
        current_category = Category.query.get(category_id)
    else:
        current_category = None
    
    # 排序
    query = query.order_by(Product.created_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    products = pagination.items
    
    return render_template('frontend/products.html', 
                         categories=categories,
                         products=products,
                         current_category=current_category,
                         pagination=pagination)


@main.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    产品详情页面
    """
    # 获取产品信息
    product = Product.query.get_or_404(product_id)
    
    # 检查产品状态
    if not product.status:
        return redirect(url_for('main.products'))
    
    # 获取所有分类（用于导航栏）
    categories = Category.query.order_by(Category.created_at).all()
    
    # 获取相关产品（同分类的其他产品）
    related_products = Product.query.filter_by(
        category_id=product.category_id,
        status=True
    ).filter(Product.id != product_id).order_by(Product.created_at.desc()).limit(4).all()
    
    # 获取产品的图库图片
    product_images = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.order).all()
    
    return render_template('frontend/product-detail.html',
                         product=product,
                         categories=categories,
                         related_products=related_products,
                         product_images=product_images)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    联系我们页面
    支持表单提交和处理
    """
    # 获取所有分类（用于导航栏）
    categories = Category.query.order_by(Category.created_at).all()
    
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # 简单的表单验证
        if not name or not email or not phone or not subject or not message:
            from flask import flash
            flash('请填写所有必填字段', 'danger')
            return render_template('frontend/contact.html', categories=categories)
        
        # 保存到数据库
        from app.models import Contact
        try:
            new_contact = Contact(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()
            
            # 记录日志
            import logging
            logging.info(f'收到新的联系表单并保存: 姓名={name}, 邮箱={email}, 主题={subject}')
            
            # 这里可以添加发送邮件通知管理员的代码
            # from app.utils import send_email
            # send_email('新的联系表单提交', 'admin@example.com', f'收到来自{name}的新消息')
            
            from flask import flash
            flash('您的留言已成功提交，我们将尽快与您联系！', 'success')
            # 提交成功后重定向，防止刷新页面重复提交
            return redirect(url_for('main.contact'))
        except Exception as e:
            db.session.rollback()
            import logging
            logging.error(f'保存联系表单失败: {str(e)}')
            from flask import flash
            flash('提交失败，请稍后再试', 'danger')
    
    return render_template('frontend/contact.html', categories=categories)


@main.route('/image/product/<int:product_id>')
def get_product_image(product_id):
    """
    获取产品主图片
    从数据库中读取图片数据并返回
    """
    product = Product.query.get_or_404(product_id)
    
    if product.main_image:
        # 使用BytesIO将二进制数据转换为可发送的文件对象
        # 如果没有mimetype，尝试从文件名推断，否则使用默认值
        mimetype = product.main_image_mimetype or 'image/jpeg'
        filename = product.main_image_filename or f'product_{product_id}.jpg'
        return send_file(
            BytesIO(product.main_image),
            mimetype=mimetype,
            as_attachment=False,
            download_name=filename
        )
    else:
        # 如果没有图片，返回404或默认图片
        from flask import abort
        abort(404)


@main.route('/image/gallery/<int:image_id>')
def get_gallery_image(image_id):
    """
    获取产品图库图片
    从数据库中读取图片数据并返回
    """
    from app.models import ProductImage
    
    image = ProductImage.query.get_or_404(image_id)
    
    if image.image_data and image.mimetype:
        # 使用BytesIO将二进制数据转换为可发送的文件对象
        return send_file(
            BytesIO(image.image_data),
            mimetype=image.mimetype,
            as_attachment=False,
            download_name=image.filename
        )
    else:
        # 如果没有图片，返回默认图片
        return redirect(url_for('static', filename='images/default-product.jpg'))


@main.route('/image/page-content/<int:content_id>')
def get_page_content_image(content_id):
    """
    获取页面内容图片（前台访问）
    """
    from app.models import PageContent
    
    content = PageContent.query.get_or_404(content_id)
    
    if content.image_data:
        return send_file(
            BytesIO(content.image_data),
            mimetype=content.image_mimetype or 'image/jpeg',
            as_attachment=False,
            download_name=content.image_filename or f'image_{content_id}.jpg'
        )
    else:
        from flask import abort
        abort(404)