# -*- coding: utf-8 -*-

from flask import Flask,render_template,url_for,redirect,make_response,session,request,flash,send_from_directory,g,current_app
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from config import Config
from app import create_app,db
import datetime
import os
from io import BytesIO
from app.common import is_login
from flask_ckeditor import upload_fail, upload_success
from app.models.other import Reports,Files
from app.models.bill import Fee1,Fee2,Fee3,Fee4,Fee5,Wordnumbers
from app.models.system import Users,Logs,Groups
from app.models.contract import Orders,Customers
from app.forms.user import LoginForm

app=create_app('develop')


#自定义出错页
@app.errorhandler(404)
def page_not_found(e):
    return '页面没找到'


@app.route('/temp')
def temp():
    user=Users()
    user.username='admin'
    user.set_password('11111111')
    db.session.add(user)
    db.session.commit()
    return render_template('temp.html',temp='Hello')

@app.route('/files/<int:dirname>/<filename>')
@app.route('/Files/<int:dirname>/<filename>')
def up_file(dirname,filename):
    #print(str(dirname)+'filename='+filename)
    return send_from_directory(app.config['UPLOADED_PATH'],str(dirname)+'/'+filename)


@app.route('/Files/<filename>')
@app.route('/files/<filename>')
def uploaded_files(filename):
    path=os.path.join(app.config['UPLOADED_PATH'],datetime.datetime.now().strftime("%Y")+os.sep)
    return send_from_directory(app.config['UPLOADED_PATH'], filename)


#附件上传
@app.route('/upload', methods=['POST'],endpoint='upload')
@is_login
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg','doc','xls','docx','xlsx']:
        return upload_fail(message='只能上传图片、word和excel文件!')
    newfilename=session.get('username')+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path=os.path.join(app.config['UPLOADED_PATH'],datetime.datetime.now().strftime("%Y")+os.sep)
    if not os.path.exists(path):
        os.mkdir(path)
    #print(os.path.join(path, newfilename+'.'+extension))
    f.save(os.path.join(path, newfilename+'.'+extension))
    url = url_for('uploaded_files', filename=datetime.datetime.now().strftime("%Y")+'/'+newfilename+'.'+extension)
    return upload_success(url=url)

#登陆
@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm()
    # 1.判断请求方式,如果是GET,直接渲染页面
    if request.method == "GET":
        # 判断管理员是否已经登陆过了,如果登陆过了指教跳转到首页
        if str(session.get('username')) != 'None':
            return redirect("/admin/index")
        return render_template("login.html",form=form)
    # 2.如果是POST请求,获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    captcha=request.form.get('verify_code')
    # 3.校验参数,为空校验
    if not all([username, password]):
        return render_template("login.html", errmsg="参数不全",form=form)
    if session.get('imageCode') != captcha:
        return render_template("login.html", errmsg="验证码不对"+captcha+"*",form=form)
    # 4.根据用户名取出管理员对象,判断管理员是否存在
    try:
        admin = Users.query.filter(Users.username== username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("login.html", errmsg="用户查询失败",form=form)
    if not admin:
        return render_template("login.html", errmsg="管理员不存在",form=form)

    # 5.判断管理员的密码是否正确
    if not admin.check_password(password):
        return render_template("login.html", errmsg="密码错误",form=form)

    # 6.管理的session信息记录
    session["user_id"] = admin.id
    session["username"] = admin.username
    session["usermenu"]=admin.usermenu

    # 7.重定向到首页展示
    return redirect("/admin/index")

#首页
@app.route('/index',endpoint='index')
@is_login
def index():
    return render_template('index.html')


if __name__=='__main__':
    app.run('0.0.0.0', port=80, debug=True)