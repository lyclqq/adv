import json
import os
from flask import Blueprint, render_template, session, flash, request, current_app
from app import db
from app.common import is_login, ins_logs,month_difference
from app.forms.user import PwdForm,MonthForm
from app.models.system import Users, Groups,Systeminfo
from app.models.contract import Orders
from app.models.other import History
from sqlalchemy.sql import func

# 用户管理
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
@is_login
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


# 列表页
@userView.route('/list/<int:page>', methods=["GET", "POST"])
def user_list(page):
    pagination = Users.query.order_by(Users.updatetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('user/user_list.html', pagination=pagination, dept_dict=get_dept_dict())


# 添加页
@userView.route('/to_add', defaults={"fid": -1}, methods=["GET"])
@userView.route('/to_add/<int:fid>', methods=["GET"])
def user_to_add(fid):
    if fid != -1:
        user = Users.query.filter(Users.id == fid).first()
    else:
        user = None
    dept = Groups.query.filter(Groups.status == 'on').all()
    return render_template('user/user_add.html', user=user, dept=dept, roles=get_roles())


# 查询部门数据
def get_dept_dict():
    dept_dict = dict()
    gs = Groups.query.filter(Groups.status == 'on').all()
    for g in gs:
        dept_dict[g.id] = g.groupname
    return dept_dict


# 查询角色数据
def get_roles():
    strpath = os.getcwd() + "\\app\\static\\role.json"
    with open(strpath, 'r', encoding='utf-8') as f:
        roles = json.load(f)
    return roles


# 添加方法
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


# 状态开关
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


# 密码重置方法
@userView.route('/reset_pwd', methods=["POST"])
def reset_pwd():
    try:
        print(request.form.get('uid'))
        print(request.form.get('reset_new'))
        userid = int(request.form.get('uid'))
        user = Users.query.get(userid)
        user.set_password(request.form.get('reset_new'))
        # user.passwd = request.form.get('reset_new')
        db.session.add(user)
        db.session.commit()
        ins_logs(userid, '修改密码', 'user')
        re = '{"result":"ok"}'
    except Exception as e:
        current_app.logger.error(e)
        re = '{"result":"wrong"}'
    return re

#初始化
@userView.route('/setmonth', methods=["GET", "POST"])
@is_login
def setmonth():
    form = MonthForm()
    systeminfo = db.session.query(Systeminfo).filter(Systeminfo.id == 1).first()
    systoday=systeminfo.systemmonth
    form.today.data=systoday.strftime('%Y-%m')
    if form.validate_on_submit():
        month=month_difference(form.today.data+'-01',form.fee_date.data)
        if month==1:
            try:
                fee32=db.session.query(Orders).with_entities(func.sum(Orders.Fee32)).scalar()
                fee22 = db.session.query(Orders).with_entities(func.sum(Orders.Fee22)).scalar()
                fee42=db.session.query(Orders).with_entities(func.sum(Orders.Fee42)).scalar()
                fee52 = db.session.query(Orders).with_entities(func.sum(Orders.Fee52)).scalar()
                history=History()
                history.title=form.fee_date.data.strftime('%Y-%m')
                history.fee_date = form.fee_date.data.strftime('%Y-%m-%d')
                history.fee=fee22
                history.type='Fee22'
                db.session.add(history)
                history=History()
                history.title=form.fee_date.data.strftime('%Y-%m')
                history.fee_date=form.fee_date.data.strftime('%Y-%m-%d')
                history.fee=fee32
                history.type='Fee32'
                db.session.add(history)
                history = History()
                history.title=form.fee_date.data.strftime('%Y-%m')
                history.fee_date=form.fee_date.data.strftime('%Y-%m-%d')
                history.fee=fee42
                history.type='Fee42'
                db.session.add(history)
                history = History()
                history.title=form.fee_date.data.strftime('%Y-%m')
                history.fee_date=form.fee_date.data.strftime('%Y-%m-%d')
                history.fee=fee52
                history.type='Fee52'
                db.session.add(history)
                Orders.query.update({'Fee22': 0,'Fee32':0,'Fee42':0,'Fee52':0,'Fee62':0})
                if form.fee_date.data.year-systoday.year==1:
                    Orders.query.update({'Fee23': 0, 'Fee33': 0, 'Fee43': 0, 'Fee53': 0})
                systeminfo.systemmonth= form.fee_date.data.strftime('%Y%m%d')
                db.session.add(systeminfo)
                db.session.commit()
                flash('初使化成功!')
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
                flash('初使化失败')
        else:
            flash('所选月份不对!')
    return render_template('user/month.html', form=form)