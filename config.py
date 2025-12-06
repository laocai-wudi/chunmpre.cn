# -*- coding: utf-8 -*-
"""
配置文件 - 包含应用的所有配置信息
"""
import os
from dotenv import load_dotenv
from datetime import timedelta


# 加载环境变量（如果有.env文件）
load_dotenv()

#  """应用配置类"""
class Config:   
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Flask-WTF CSRF配置
    WTF_CSRF_ENABLED = False  # 暂时禁用CSRF验证，避免影响登录
    WTF_CSRF_TIME_LIMIT = None  # 不限制CSRF token有效期
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:123456@192.168.136.146/chunmpre_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 最大请求大小：50MB（允许同时上传多张图片，每张最大5MB）
    
    # 应用配置
    APP_NAME = '上海春木精密机械有限公司'
    APP_VERSION = '1.0.0'
    
    # 分页配置
    PRODUCTS_PER_PAGE = 12
    
    # 图片上传路径（这个项目我们选择将图片存储在数据库中，所以这里只是一个占位符）
    UPLOAD_FOLDER = 'app/static/uploads'
    STORAGE_TYPE = 'database'  # 可选值: 'database', 'filesystem'
    
    # 会话配置
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 站点信息
    SITE_NAME = '东莞春鸣精密机械有限公司'
    SITE_URL = 'http://localhost:5000'


class DevelopmentConfig(Config):
    # """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 开发环境打印SQL语句便于调试


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境应该从环境变量获取密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 生产环境应该从环境变量获取数据库URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    # 测试使用单独的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://admin:password@localhost:5432/chunmpre_test_db'


# 配置映射，方便根据环境选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}