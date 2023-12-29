# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import timedelta
import redis
#from redis import StrictRedis

class Config(object):

    #调试信息
    DEBUG = True
    SECRET_KEY = "fdfdjfkdjfkdf"

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Panda1@127.0.0.1:3306/adv?charset=utf8'  # 数据库联接字
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = True
    SCALE=5
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 600
    CKEDITOR_FILE_UPLOADER = 'files'
    CKEDITOR_ENABLE_CSRF = True


    # redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 2
    # session配置信息
    SESSION_TYPE = "redis"  # 设置session存储类型
    SESSION_REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)  # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True #设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=1) #设置session有效期,两天时间

    PAGEROWS=15

    #默认日志级别
    LEVEL_NAME = logging.DEBUG

    UPLOAD_FOLDER = 'static\\files\\'
    PASSWORD = '11111111'


#开发环境配置信息
class DevelopConfig(Config):
    pass


#生产(线上)环境配置信息
class ProductConfig(Config):
    DEBUG = False
    LEVEL_NAME = logging.ERROR


#提供一个统一的访问入口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig
}


