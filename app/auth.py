# -*- coding: utf-8 -*-
"""
用户认证模块
处理用户登录、登出和管理员权限验证
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.urls import url_parse
from urllib.parse import urlparse as url_parse
from datetime import datetime

from app import db
from app.models import User
from app.forms import LoginForm

# 创建认证蓝图
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录视图
    """
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 创建登录表单
    form = LoginForm()
    
    # 处理表单提交
    if form.validate_on_submit():
        # 查询用户
        user = User.query.filter_by(username=form.username.data).first()
        
        # 验证用户和密码
        if user is None or not user.verify_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))
        
        # 检查用户是否激活
        if not user.is_active:
            flash('账户已被禁用', 'warning')
            return redirect(url_for('auth.login'))
        
        # 登录用户
        login_user(user, remember=form.remember.data)
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # 获取下一个页面
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # 如果是管理员，重定向到后台首页
            if user.is_admin:
                next_page = url_for('admin.admin_dashboard')
            else:
                next_page = url_for('main.index')
        
        flash('登录成功', 'success')
        return redirect(next_page)
    
    # 渲染登录页面
    return render_template('admin/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    用户登出视图
    """
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('main.index'))


def admin_required(f):
    """
    管理员权限装饰器
    检查当前用户是否为管理员
    """
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('您没有管理员权限', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
