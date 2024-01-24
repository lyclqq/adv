# -*- coding: utf-8 -*-

import datetime
import os
from io import BytesIO
from flask import render_template, url_for, redirect, make_response, session, request, send_from_directory, current_app
from flask_ckeditor import upload_fail, upload_success
from sqlalchemy import and_
from app import create_app, getKey, getVerifyCode
from app.common import is_login, getrolemenu
from app.forms.user import LoginForm
from app.models.contract import Orders
from app.models.system import Users
from app import db

app = create_app('develop')


# 自定义出错页
@app.errorhandler(404)
def page_not_found(e):
    return '页面没找到'


# 查用户名
def replace_username(userid):
    if userid == 0:
        return None
    user = Users.query.filter(Users.id == userid).first()
    return user.username


app.add_template_filter(replace_username)


# 查合同名
def replace_ordername(orderid):
    if orderid == 0:
        return None
    order = Orders.query.filter(Orders.id == orderid).first()
    return order.title


app.add_template_filter(replace_ordername)


# 短日期时间格式
def short_time(value):
    return value.strftime('%m-%d %H:%M')


app.add_template_filter(short_time)


# 生成验证码
@app.route('/imgCode')
def img_code():
    img_key = getKey()
    image = getVerifyCode(img_key)
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    session['imageCode'] = img_key
    return response


# 登出
@app.route('/logout')
@is_login
def logout():
    session.pop("user_id")
    session.pop("group_id")
    session.pop("username")
    session.pop("usermenu")
    session.pop("type")
    session.pop("imageCode")
    return redirect(url_for('login'))


@app.route('/temp')
def temp():
    data = {
        'title': {
            'text': 'ECharts 入门示例'
        },
        'tooltip': {},
        'legend': {
            'data': ['销量1', '销量2']
        },
        'xAxis': {
            'data': ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子']
        },
        'yAxis': {},
        'series': [
            {
                'name': '销量1',
                'type': 'bar',
                'data': [5, 20, 36, 10, 10, 20]
            },
            {
                'name': '销量2',
                'type': 'bar',
                'data': [8, 21, 30, 15, 15, 20]
            }
        ]
    }

    data['title']['text'] = '这是标题'

    option = {
        'title': [
            {
                'text': '广告合同款项统计图,合同金额为'
            }
        ],
        'polar': {
            'radius': [30, '80%']
        },
        'angleAxis': {
            'max': 100,
            'startAngle': 0
        },
        'radiusAxis': {
            'type': 'category',
            'data': ['刊登金额', '到帐金额', '发票金额']
        },
        'tooltip': {},
        'series': {
            'type': 'bar',
            'data': [80, 70, 65],
            'coordinateSystem': 'polar',
            'label': {
                'show': True,
                'position': 'middle',
                'formatter': '{b}: {c}'
            }
        }
    }
    return render_template('temp.html', data=option)


@app.route('/files/<int:dirname>/<filename>')
@app.route('/Files/<int:dirname>/<filename>')
def up_file(dirname, filename):
    return send_from_directory(app.config['UPLOADED_PATH'], str(dirname) + '/' + filename)


@app.route('/Files/<filename>')
@app.route('/files/<filename>')
def uploaded_files(filename):
    # path = os.path.join(app.config['UPLOADED_PATH'], datetime.datetime.now().strftime("%Y") + os.sep)
    return send_from_directory(app.config['UPLOADED_PATH'], filename)


# 附件上传
@app.route('/upload', methods=['POST'], endpoint='upload')
@is_login
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg', 'doc', 'xls', 'docx', 'xlsx']:
        return upload_fail(message='只能上传图片、word和excel文件!')
    newfilename = session.get('username') + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    path = os.path.join(app.config['UPLOADED_PATH'], datetime.datetime.now().strftime("%Y") + os.sep)
    if not os.path.exists(path):
        os.mkdir(path)
    f.save(os.path.join(path, newfilename + '.' + extension))
    url = url_for('uploaded_files', filename=datetime.datetime.now().strftime("%Y") + '/' + newfilename + '.' + extension)
    return upload_success(url=url)


# 登陆
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    # 1.判断请求方式,如果是GET,直接渲染页面
    if request.method == "GET":
        # 判断管理员是否已经登陆过了,如果登陆过了指教跳转到首页
        if str(session.get('username')) != 'None':
            return redirect("/index")
        return render_template("login.html", form=form)
    # 2.如果是POST请求,获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    captcha = request.form.get('verify_code')
    # 3.校验参数,为空校验
    if not all([username, password]):
        return render_template("login.html", errmsg="参数不全", form=form)
    if session.get('imageCode') != captcha:
        return render_template("login.html", errmsg="验证码不对" + captcha + "*", form=form)
    # 4.根据用户名取出管理员对象,判断管理员是否存在
    try:
        user = Users.query.filter(Users.username == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("login.html", errmsg="用户查询失败", form=form)
    if not user:
        return render_template("login.html", errmsg="用户不存在", form=form)

    # 5.判断管理员的密码是否正确
    if not user.check_password(password):
        return render_template("login.html", errmsg="密码错误", form=form)

    # 6.管理的session信息记录
    session["user_id"] = user.id
    session["username"] = user.username
    session["usermenu"] = getrolemenu(user.type)
    session["group_id"] = user.group_id
    session["type"] = user.type
    # 更新用户信息
    user.updatetime = datetime.datetime.now()
    db.session.add(user)
    db.session.commit()
    # 7.重定向到首页展示
    return redirect("/index")


# 首页
@app.route('/index', endpoint='index')
@is_login
def index():
    # 有欠款的
    red = Orders.query.filter(and_(Orders.group_id == session["group_id"], Orders.Fee41 < Orders.Fee21)).order_by(Orders.contract_date)
    # 已到账的
    black = Orders.query.filter(and_(Orders.group_id == session["group_id"], Orders.Fee41 > Orders.Fee21)).order_by(Orders.contract_date)
    return render_template('index24.html', red=red, black=black)


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True)
