import json
import os
from flask import Blueprint, render_template, session, flash, request, current_app
from app import db
from app.common import is_login, ins_logs
from app.forms.user import PwdForm
from app.models.system import Users, Groups

userView = Blueprint('user', __name__)
pagesize = 10


@userView.route('/editpwd', methods=["GET", "POST"])
@is_login
def editpwd():
    form = PwdForm()
    form.username.data = session.get("username")
    if form.validate_on_submit():
        if form.password1.data == form.password2.data and len(form.password1.data) > 5:
            userid = int(session.get('user_id'))
            user = Users.query.get(userid)
            user.set_password(form.password1.data)
            db.session.add(user)
            db.session.commit()
            flash('密码修改成功')
        else:
            flash('密码不能太短')
    return render_template('admin/pwd.html', form=form)


@userView.route('/edit_pwd', methods=["POST"])
def edit_pwd():
    pwd2 = request.form.get('new_pwd2')
    if session.get('user_id'):
        try:
            userid = int(session.get('user_id'))
            user = Users.query.get(userid)
            user.set_password(pwd2)
            db.session.add(user)
            db.session.commit()
            ins_logs(userid, '修改密码', 'user')
        except Exception as e:
            current_app.logger.error(e)
        re = '{"result":"ok"}'
    else:
        re = '{"result":"out_of_date"}'
    return re


@userView.route('/list/<int:page>', methods=["GET", "POST"])
def user_list(page):
    pagination = Users.query.order_by(Users.updatetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('user/user_list.html', pagination=pagination, dept_dict=get_dept_dict())


@userView.route('/to_add', defaults={"fid": -1}, methods=["GET"])
@userView.route('/to_add/<int:fid>', methods=["GET"])
def user_to_add(fid):
    if fid != -1:
        user = Users.query.filter(Users.id == fid).first()
    else:
        user = None
    dept = Groups.query.filter(Groups.status == 'on').all()
    return render_template('user/user_add.html', user=user, dept=dept, roles=get_roles())


def get_dept_dict():
    dept_dict = dict()
    gs = Groups.query.filter(Groups.status == 'on').all()
    for g in gs:
        dept_dict[g.id] = g.groupname
    return dept_dict


def get_roles():
    strpath = os.getcwd() + "\\app\\static\\role.json"
    with open(strpath, 'r', encoding='utf-8') as f:
        roles = json.load(f)
    return roles


@userView.route('/add', methods=["POST"])
def user_add():
    fid = request.form.get('fid')
    if fid != '':
        user = Users.query.filter(Users.id == fid).first()
    else:
        user = Users(
        )
        user.set_password(request.form.get('passwd'))
    #
    user.username = request.form.get('username')
    user.type = request.form.get('type')
    user.group_id = request.form.get('group_id')
    user.status = request.form.get('status')
    user.notes = request.form.get('notes')
    #
    db.session.add(user)
    db.session.commit()
    if fid != '':
        ins_logs(session.get("user_id"), '用户数据修改', 'Users')
    else:
        ins_logs(session.get("user_id"), '用户数据新增', 'Users')
    re = '{"result":"ok"}'
    return re


@userView.route('/status', methods=["POST"])
def user_status():
    pid = request.form.get('pid')
    user = Users.query.filter(Users.id == pid).first()
    if user:
        if user.status == 'on':
            user.status = 'off'
        else:
            user.status = 'on'
        db.session.add(user)
        db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


@userView.route('/reset_pwd', methods=["POST"])
def reset_pwd():
    try:
        print(request.form.get('uid'))
        print(request.form.get('reset_new'))
        userid = int(request.form.get('uid'))
        user = Users.query.get(userid)
        user.set_password(request.form.get('reset_new'))
        #user.passwd = request.form.get('reset_new')
        db.session.add(user)
        db.session.commit()
        ins_logs(userid, '修改密码', 'user')
        re = '{"result":"ok"}'
    except Exception as e:
        current_app.logger.error(e)
        re = '{"result":"wrong"}'
    return re
