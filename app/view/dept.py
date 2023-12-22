from flask import Blueprint, render_template, request, session
from app import db
from app.common import ins_logs, is_login
from app.models.system import Groups

# 部门管理
dept_bp = Blueprint('dept', __name__)
pagesize = 10


# 列表页
@dept_bp.route('/dept/list/<int:page>/', methods=["GET", "POST"])
@is_login
def dept_list(page):
    pagination = Groups.query.order_by(Groups.groupname).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('dept/dept_list.html', pagination=pagination)


# 添加页
@dept_bp.route('/dept/to_add', defaults={"fid": -1}, methods=["GET"])
@dept_bp.route('/dept/to_add/<int:fid>', methods=["GET"])
def dept_to_add(fid):
    if fid != -1:
        dept = Groups.query.filter(Groups.id == fid).first()
    else:
        dept = None
    return render_template('dept/dept_add.html', dept=dept)


# 添加方法
@dept_bp.route('/dept/add', methods=["POST"])
def dept_add():
    fid = request.form.get('fid')
    if fid != '':
        dept = Groups.query.filter(Groups.id == fid).first()
    else:
        dept = Groups(
        )
    #
    dept.groupname = request.form.get('groupname')
    dept.type = request.form.get('type')
    dept.flag = float(request.form.get('flag'))
    dept.status = request.form.get('status')
    dept.notes = request.form.get('notes')
    #
    db.session.add(dept)
    db.session.commit()
    if fid != '':
        ins_logs(session.get("user_id"), '部门数据修改', 'Groups')
    else:
        ins_logs(session.get("user_id"), '部门数据新增', 'Groups')
    re = '{"result":"ok"}'
    return re


# 状态修改
@dept_bp.route('/dept/status', methods=["POST"])
def dept_status():
    pid = request.form.get('pid')
    dept = Groups.query.filter(Groups.id == pid).first()
    if dept:
        if dept.status == 'on':
            dept.status = 'off'
        else:
            dept.status = 'on'
        db.session.add(dept)
        db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re
