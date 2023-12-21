# -*- coding: utf-8 -*-
from flask import Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
from config import Config,config_dict
import random
import string
from PIL import Image,ImageFont,ImageDraw
import click
from flask_bootstrap import Bootstrap
import os

redis_store = None
db=SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    # 根据传入的配置类名称,取出对应的配置类
    config = config_dict.get(config_name)

    # 调用日志方法,记录程序运行信息
    log_file(config.LEVEL_NAME)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'static', 'files') + os.sep

    # 加载配置类
    app.config.from_object(config)

    bootstrap = Bootstrap()
    bootstrap.init_app(app)

    # 创建SQLAlchemy对象,关联app
    db.init_app(app)

    # 创建Session对象,读取APP中session配置信息
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    from app.view.system import systemView
    app.register_blueprint(systemView,url_prefix='/system') #系统管理菜单
    from app.view.user import userView #个人相关
    app.register_blueprint(userView,url_prefix='/user')
    from app.view.contract import contractView #个人相关
    app.register_blueprint(contractView,url_prefix='/contract')
    from app.view.publish import publish_bp
    from app.view.paid import paid_bp
    from app.view.performance import performance_bp
    app.register_blueprint(publish_bp, url_prefix='/')  # 刊登
    app.register_blueprint(paid_bp, url_prefix='/')  # 收付款
    app.register_blueprint(performance_bp, url_prefix='/')  # 绩效
    from app.view.logs import log_bp
    app.register_blueprint(log_bp, url_prefix='/')  # 日志
    return app

#日志文件
def log_file(LEVEL_NAME):
    # 设置日志的记录等级,常见的有四种,大小关系如下: DEBUG < INFO < WARNING < ERROR
    logging.basicConfig(level=LEVEL_NAME)  # 调试debug级,一旦设置级别那么大于等于该级别的信息全部都会输出
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 10, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def getVerifyCode(imgKey):
    width,height=120,50
    im=Image.new('RGB',(width,height),'white')
    font= ImageFont.truetype('arial', 40)
    draw=ImageDraw.Draw(im)
    for item in range(4):
        draw.text((5+random.randint(-3,3)+23*item,5+random.randint(-3,3)),text=imgKey[item],fill=rndColor(),font=font)
    return im


def getKey():
    return ''.join(random.sample(string.digits,4))


def rndColor():
    return (random.randint(16,128),random.randint(16,128),random.randint(16,128))

