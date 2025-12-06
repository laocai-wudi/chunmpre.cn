# -*- coding: utf-8 -*-
"""
后台管理模块
实现管理员对产品、分类等内容的管理功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import base64
from app.routes import save_product_image, delete_product_image

from app import db
from app.models import Category, Product, ProductImage, Contact
from app.forms import CategoryForm, ProductForm, ProductEditForm, ProductImageForm
from app.auth import admin_required

# 创建后台管理蓝图
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """
    后台管理仪表盘
    显示概览信息，包括产品数量、分类数量等统计数据
    """
    # 获取产品和分类的统计信息
    product_count = Product.query.count()
    category_count = Category.query.count()
    
    # 获取未读联系表单数量
    unread_contact_count = Contact.query.filter_by(is_read=False).count()
    
    # 获取最近添加的5个产品
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    # 获取最近的5条未读联系表单
    recent_unread_contacts = Contact.query.filter_by(is_read=False).order_by(Contact.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           product_count=product_count,
                           category_count=category_count,
                           unread_contact_count=unread_contact_count,
                           recent_products=recent_products,
                           recent_unread_contacts=recent_unread_contacts)


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    """
    分类管理页面
    支持查看、添加、编辑和删除分类
    """
    # 创建分类表单
    add_form = CategoryForm()
    edit_form = CategoryForm()  # 用于编辑表单
    
    # 获取所有分类
    categories = Category.query.all()
    
    # 处理表单提交（添加分类）
    # 只处理添加分类的请求，编辑和删除请求由其他路由处理
    if request.method == 'POST':
        # 检查是否是编辑或删除请求（通过检查是否有id字段或_form_action）
        if 'id' in request.form or request.form.get('_form_action') in ['edit', 'delete']:
            # 这是编辑或删除请求，不应该在这里处理，忽略
            pass
        elif add_form.validate_on_submit():
            # 创建新分类
            new_category = Category(name=add_form.name.data)
            db.session.add(new_category)
            db.session.commit()
            flash('分类添加成功！', 'success')
            return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/categories.html', 
                           form=add_form,
                           add_form=add_form,
                           edit_form=edit_form,
                           categories=categories)


@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """
    编辑分类
    """
    category = Category.query.get_or_404(category_id)
    
    # 处理POST请求（从模态框提交）
    if request.method == 'POST':
        # 检查是否有name字段（从模态框提交）
        if 'name' in request.form:
            new_name = request.form.get('name', '').strip()
            if new_name:
                # 如果用户修改了名称，需要检查新名称是否已被使用
                if new_name != category.name:
                    existing_category = Category.query.filter_by(name=new_name).first()
                    if existing_category:
                        flash('该分类名称已存在！', 'error')
                        return redirect(url_for('admin.manage_categories'))
                
                # 更新分类信息
                category.name = new_name
                db.session.commit()
                flash('分类更新成功！', 'success')
                return redirect(url_for('admin.manage_categories'))
            else:
                flash('分类名称不能为空！', 'error')
                return redirect(url_for('admin.manage_categories'))
        else:
            # 如果没有name字段，可能是其他类型的请求，返回错误
            flash('请求参数错误！', 'error')
            return redirect(url_for('admin.manage_categories'))
    
    # GET请求，显示编辑表单页面（通常不会用到，因为使用模态框）
    form = CategoryForm(obj=category)
    return render_template('admin/edit_category.html', form=form, category=category)


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """
    删除分类
    注意：删除分类前需要检查是否有产品属于该分类
    """
    """
    删除分类
    注意：删除分类前需要检查是否有产品属于该分类
    """
    category = Category.query.get_or_404(category_id)
    
    # 检查是否有产品属于该分类
    products_in_category = Product.query.filter_by(category_id=category_id).count()
    if products_in_category > 0:
        flash(f'无法删除该分类，因为有 {products_in_category} 个产品属于此分类。请先移动或删除这些产品。', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    # 删除分类
    db.session.delete(category)
    db.session.commit()
    flash('分类删除成功！', 'success')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/products', methods=['GET'])
@admin_required
def manage_products():
    """
    产品管理页面
    支持查看所有产品，支持按分类筛选
    """
    # 获取筛选参数
    category_id = request.args.get('category')
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status')
    
    # 构建查询
    query = Product.query
    
    # 按分类筛选
    if category_id:
        try:
            category_id = int(category_id)
            query = query.filter_by(category_id=category_id)
        except (ValueError, TypeError):
            category_id = None
    
    # 按状态筛选（只有当status_filter不为空时才筛选）
    if status_filter is not None and status_filter != '':
        query = query.filter_by(status=(status_filter == '1'))
    
    # 搜索产品名称或描述
    if search_query:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%')
            )
        )
    
    products = query.order_by(Product.created_at.desc()).all()
    
    # 获取所有分类用于筛选
    categories = Category.query.all()
    
    # 转换category_id为整数用于模板比较
    selected_category_id = None
    if category_id:
        try:
            selected_category_id = int(category_id)
        except (ValueError, TypeError):
            selected_category_id = None
    
    return render_template('admin/products.html', 
                           products=products, 
                           categories=categories,
                           selected_category=selected_category_id,
                           search_query=search_query or '',
                           selected_status=status_filter or '')


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """
    添加新产品
    支持上传产品主图和多张图库图片
    """
    form = ProductForm()
    
    # 动态加载分类选项
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # 处理主图上传（存储到数据库）
        main_image_data = None
        main_image_filename = None
        main_image_mimetype = None
        
        if form.main_image.data:
            main_image_data = form.main_image.data.read()
            main_image_filename = secure_filename(form.main_image.data.filename)
            main_image_mimetype = form.main_image.data.content_type
        
        # 处理服务标签（转换为JSON）
        import json
        service_tags_json = None
        if form.service_tags.data:
            tags_list = [tag.strip() for tag in form.service_tags.data.split('\n') if tag.strip()]
            service_tags_json = json.dumps(tags_list, ensure_ascii=False)
        
        # 创建产品
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            brand=form.brand.data,
            specifications=form.specifications.data,
            technical_specs=form.technical_specs.data,
            features=form.features.data,
            advantages=form.advantages.data,
            applications=form.applications.data,
            category_id=form.category_id.data,
            main_image=main_image_data,
            main_image_filename=main_image_filename,
            main_image_mimetype=main_image_mimetype,
            price=form.price.data,
            price_min=form.price_min.data,
            price_max=form.price_max.data,
            price_note=form.price_note.data,
            stock=form.stock.data or 0,
            status=form.status.data,
            rating=form.rating.data,
            review_count=form.review_count.data or 0,
            service_tags=service_tags_json,
            tab_contents=form.tab_contents.data
        )
        db.session.add(new_product)
        db.session.flush()  # 获取产品ID，但不提交事务
        
        # 处理附加图片上传（如果有）
        if 'gallery_images' in request.files and request.files.getlist('gallery_images')[0].filename:
            gallery_images = request.files.getlist('gallery_images')
            for image in gallery_images:
                if image and image.filename:
                    image_data = image.read()
                    new_image = ProductImage(
                        product_id=new_product.id,
                        image_data=image_data,
                        filename=secure_filename(image.filename),
                        mimetype=image.content_type
                    )
                    db.session.add(new_image)
        
        # 提交事务
        db.session.commit()
        flash('产品添加成功！', 'success')
        return redirect(url_for('admin.manage_products'))
    
    return render_template('admin/add_product.html', form=form)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """
    编辑产品信息
    支持更新产品信息，选择是否更新主图
    """
    product = Product.query.get_or_404(product_id)
    form = ProductEditForm(obj=product)
    
    # 动态加载分类选项（确保表单有最新的分类列表）
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    # 处理状态切换（通过POST参数直接更新状态）
    if request.method == 'POST' and 'status' in request.form:
        status_value = request.form.get('status')
        if status_value in ['true', 'false']:
            product.status = (status_value == 'true')
            db.session.commit()
            flash('产品状态更新成功！', 'success')
            return redirect(url_for('admin.manage_products'))
    
    if form.validate_on_submit():
        import json
        
        # 更新产品基本信息
        product.name = form.name.data
        product.description = form.description.data
        product.brand = form.brand.data
        product.specifications = form.specifications.data
        product.technical_specs = form.technical_specs.data
        product.features = form.features.data
        product.advantages = form.advantages.data
        product.applications = form.applications.data
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.price_min = form.price_min.data
        product.price_max = form.price_max.data
        product.price_note = form.price_note.data
        product.stock = form.stock.data or 0
        product.status = form.status.data
        product.rating = form.rating.data
        product.review_count = form.review_count.data or 0
        product.tab_contents = form.tab_contents.data
        
        # 处理服务标签（转换为JSON）
        if form.service_tags.data:
            tags_list = [tag.strip() for tag in form.service_tags.data.split('\n') if tag.strip()]
            product.service_tags = json.dumps(tags_list, ensure_ascii=False)
        else:
            product.service_tags = None
        
        # 处理移除图片标记
        if request.form.get('remove_image') == 'true':
            product.main_image = None
            product.main_image_filename = None
            product.main_image_mimetype = None
        
        # 处理主图更新（如果用户提供了新图片）
        # 检查是否是文件上传（FileStorage对象有filename属性）
        if form.main_image.data:
            # 使用hasattr检查是否有filename属性，避免AttributeError
            if hasattr(form.main_image.data, 'filename') and form.main_image.data.filename:
                # form.main_image.data 是 FileStorage 对象，有 read() 方法
                product.main_image = form.main_image.data.read()
                product.main_image_filename = secure_filename(form.main_image.data.filename)
                product.main_image_mimetype = form.main_image.data.content_type
            # 如果没有filename属性，说明可能是bytes或其他类型，跳过更新图片
        
        # 提交事务
        db.session.commit()
        flash('产品更新成功！', 'success')
        return redirect(url_for('admin.manage_products'))
    
    return render_template('admin/edit_product.html', form=form, product=product)


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id):
    """
    删除产品
    同时删除关联的产品图片
    """
    product = Product.query.get_or_404(product_id)
    
    # 删除关联的产品图片
    ProductImage.query.filter_by(product_id=product_id).delete()
    
    # 删除产品
    db.session.delete(product)
    db.session.commit()
    flash('产品及其关联图片已删除！', 'success')
    return redirect(url_for('admin.manage_products'))


@admin_bp.route('/contacts')
@admin_required
def list_contacts():
    """
    联系表单管理页面
    显示所有用户提交的联系信息
    """
    # 获取联系表单列表，按创建时间倒序排列
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    
    # 获取未读消息数量
    unread_count = Contact.query.filter_by(is_read=False).count()
    
    return render_template('admin/contacts.html', contacts=contacts, unread_count=unread_count)


@admin_bp.route('/contacts/<int:contact_id>')
@admin_required
def view_contact(contact_id):
    """
    查看联系表单详情
    同时将状态更新为已读
    """
    contact = Contact.query.get_or_404(contact_id)
    
    # 更新为已读状态
    if not contact.is_read:
        contact.is_read = True
        db.session.commit()
    
    return render_template('admin/view_contact.html', contact=contact)


@admin_bp.route('/contacts/delete/<int:contact_id>', methods=['POST'])
@admin_required
def delete_contact(contact_id):
    """
    删除联系表单
    """
    contact = Contact.query.get_or_404(contact_id)
    
    db.session.delete(contact)
    db.session.commit()
    flash('联系信息已删除！', 'success')
    
    return redirect(url_for('admin.list_contacts'))


@admin_bp.route('/contacts/mark_all_read', methods=['POST'])
@admin_required
def mark_all_read():
    """
    将所有未读消息标记为已读
    """
    unread_contacts = Contact.query.filter_by(is_read=False).all()
    for contact in unread_contacts:
        contact.is_read = True
    
    db.session.commit()
    flash('所有消息已标记为已读！', 'success')
    
    return redirect(url_for('admin.list_contacts'))


@admin_bp.route('/products/<int:product_id>/images', methods=['GET', 'POST'])
@admin_required
def manage_product_images(product_id):
    """
    管理产品图库
    支持添加和删除产品的附加图片
    """
    product = Product.query.get_or_404(product_id)
    form = ProductImageForm()
    
    # 处理图片上传（支持多文件上传）
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'image' in request.files:
            files = request.files.getlist('image')
            uploaded_count = 0
            
            for file in files:
                if file and file.filename:
                    try:
                        image_data = file.read()
                        filename = secure_filename(file.filename)
                        
                        new_image = ProductImage(
                            product_id=product_id,
                            image_data=image_data,
                            filename=filename,
                            mimetype=file.content_type
                        )
                        db.session.add(new_image)
                        uploaded_count += 1
                    except Exception as e:
                        flash(f'上传文件 {file.filename} 时出错: {str(e)}', 'error')
                        continue
            
            if uploaded_count > 0:
                db.session.commit()
                flash(f'成功上传 {uploaded_count} 张图片！', 'success')
            else:
                flash('请选择要上传的图片！', 'error')
            
            return redirect(url_for('admin.manage_product_images', product_id=product_id))
    
    # 获取产品的所有附加图片
    images = ProductImage.query.filter_by(product_id=product_id).all()
    
    return render_template('admin/manage_product_images.html', 
                           form=form, 
                           product=product,
                           product_images=images)


@admin_bp.route('/products/<int:product_id>/images/<int:image_id>/delete', methods=['POST'])
@admin_required
def delete_product_image(product_id, image_id):
    """
    删除产品的单个附加图片
    """
    image = ProductImage.query.get_or_404(image_id)
    
    # 验证图片是否属于该产品
    if image.product_id != product_id:
        flash('操作不合法！', 'error')
        return redirect(url_for('admin.manage_product_images', product_id=product_id))
    
    db.session.delete(image)
    db.session.commit()
    flash('图片删除成功！', 'success')
    return redirect(url_for('admin.manage_product_images', product_id=product_id))


@admin_bp.route('/products/<int:product_id>/gallery_images')
@admin_required
def get_product_gallery_images(product_id):
    """
    获取产品的图库图片（用于AJAX请求）
    返回图片数据的JSON格式
    """
    images = ProductImage.query.filter_by(product_id=product_id).all()
    
    # 将图片数据转换为base64格式以便前端显示
    image_data = []
    for image in images:
        image_data.append({
            'id': image.id,
            'filename': image.filename,
            'data': base64.b64encode(image.image_data).decode('utf-8') if image.image_data else None
        })
    
    return jsonify(image_data)