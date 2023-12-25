from flask import Blueprint, render_template, request, session
from sqlalchemy.sql.elements import and_
from app import db
from app.common import ins_logs, is_login
from app.models.bill import Fee5
from app.models.contract import Orders
from app.view.publish import stat_dict, get_order_list

# 绩效
performance_bp = Blueprint('performance', __name__)
pagesize = 10


# 列表页
@performance_bp.route('/perf/list/<int:page>/', defaults={"qr_status": "-1", "qr_order": ""}, methods=["GET", "POST"])
@performance_bp.route('/perf/list/<int:page>/', methods=["GET", "POST"])
@is_login
def performance_list(page):
    q = Fee5.query
    qr_status = request.args.get('qr_status')
    qr_order = request.args.get('qr_order')
    if qr_status is not None and qr_status != '-1':
        q = q.filter(Fee5.status == qr_status)
    if qr_order is not None and qr_order != '':
        q = q.filter(Fee5.order_id == qr_order)
    pagination = q.order_by(Fee5.create_datetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('performance/perf_list.html', pagination=pagination,
                           stat_dict=stat_dict)


# 添加页
@performance_bp.route('/perf/to_add', defaults={"fid": -1}, methods=["GET"])
@performance_bp.route('/perf/to_add/<int:fid>', methods=["GET"])
def performance_to_add(fid):
    t = get_order_list()
    ids = t[1]
    names = t[0]
    if fid != -1:
        f5 = Fee5.query.filter(Fee5.id == fid).first()
        o = Orders.query.filter(Orders.id == f5.order_id).first()
    else:
        f5 = None
        o = None
    return render_template('performance/perf_add.html', names=names, ids=ids,
                           stat_dict=stat_dict, f5=f5, o=o)


# 添加方法
@performance_bp.route('/perf/add', methods=["POST"])
def perf_add():
    order_id = request.form.get('order_id')
    fid = request.form.get('fid')
    if fid != '':
        f5 = Fee5.query.filter(Fee5.id == fid).first()
    else:
        f5 = Fee5(
        )
        f5.order_id = int(order_id)
    #
    f5.fee = float(request.form.get('fee'))
    f5.prize = float(request.form.get('prize'))
    f5.feedate = request.form.get('feedate')
    f5.status = '0'
    f5.notes = request.form.get('notes')
    f5.iuser_id = session.get("user_id")
    #
    db.session.add(f5)
    db.session.commit()
    if fid != '':
        ins_logs(session.get("user_id"), '绩效数据修改', 'Fee5')
    else:
        ins_logs(session.get("user_id"), '绩效数据新增', 'Fee5')
    re = '{"result":"ok"}'
    return re


# 作废方法
@performance_bp.route('/perf/cancel', methods=["POST"])
def perf_cancel():
    pid = request.form.get('pid')
    f5 = Fee5.query.filter(and_(Fee5.id == pid, Fee5.status != '作废')).first()
    if f5:
        f5.status = '2'
        db.session.add(f5)
        db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


# 审核方法
@performance_bp.route('/perf/audit', methods=["POST"])
def perf_audit():
    pid = request.form.get('pid')
    status = request.form.get('status')
    f5 = Fee5.query.filter(Fee5.id == pid).first()
    if f5:
        if f5.status != status:
            f5.status = status
            f5.cuser_id = session.get("user_id")
            db.session.add(f5)
            db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re
