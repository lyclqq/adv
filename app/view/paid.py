from flask import Blueprint, render_template, request, session
from sqlalchemy import and_

from app import db
from app.common import ins_logs
from app.models.bill import Fee4
from app.models.contract import Orders
from app.view.publish import stat_dict, handle_file, down, get_order_list

# 收付款
paid_bp = Blueprint('paid', __name__)

pagesize = 10


@paid_bp.route('/paid/list/<int:page>/', defaults={"qr_status": "-1", "qr_order": ""}, methods=["GET", "POST"])
@paid_bp.route('/paid/list/<int:page>/', methods=["GET", "POST"])
def paid_list(page):
    q = Fee4.query
    qr_status = request.args.get('qr_status')
    qr_order = request.args.get('qr_order')
    if qr_status is not None and qr_status != '-1':
        q = q.filter(Fee4.status == qr_status)
    if qr_order is not None and qr_order != '':
        q = q.filter(Fee4.order_id == qr_order)
    pagination = q.order_by(Fee4.create_datetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('paid/paid_list.html', pagination=pagination,
                           stat_dict=stat_dict)


@paid_bp.route('/paid/to_add', defaults={"fid": -1}, methods=["GET"])
@paid_bp.route('/paid/to_add/<int:fid>', methods=["GET"])
def paid_to_add(fid):
    t = get_order_list()
    ids = t[1]
    names = t[0]
    if fid != -1:
        f4 = Fee4.query.filter(Fee4.id == fid).first()
        o = Orders.query.filter(Orders.id == f4.order_id).first()
    else:
        f4 = None
        o = None
    return render_template('paid/paid_add.html', names=names, ids=ids,
                           stat_dict=stat_dict, f4=f4, o=o)


@paid_bp.route('/paid/add', methods=["POST"])
def paid_add():
    order_id = request.form.get('order_id')
    fid = request.form.get('fid')
    if fid != '':
        f4 = Fee4.query.filter(Fee4.id == fid).first()
    else:
        f4 = Fee4(
        )
        f4.order_id = int(order_id)
    #
    file4 = request.files.get('filename')
    if file4:
        t = handle_file(file4)
        f4.filename = t[0]
        f4.path = t[1]
    #
    f4.fee = float(request.form.get('fee'))
    f4.feedate = request.form.get('feedate')
    f4.status = '0'
    f4.notes = request.form.get('notes')
    f4.iuser_id = session.get("user_id")
    #
    db.session.add(f4)
    db.session.commit()
    if fid != '':
        ins_logs(session.get("user_id"), '刊登数据修改', 'fee4')
    else:
        ins_logs(session.get("user_id"), '刊登数据新增', 'fee4')
    re = '{"result":"ok"}'
    return re


@paid_bp.route('/paid/cancel', methods=["POST"])
def paid_cancel():
    pid = request.form.get('pid')
    f4 = Fee4.query.filter(and_(Fee4.id == pid, Fee4.status != '作废')).first()
    if f4:
        f4.status = '2'
        db.session.add(f4)
        db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


@paid_bp.route('/paid/audit', methods=["POST"])
def paid_audit():
    pid = request.form.get('pid')
    status = request.form.get('status')
    f4 = Fee4.query.filter(Fee4.id == pid).first()
    if f4:
        if f4.status != status:
            f4.status = status
            f4.cuser_id = session.get("user_id")
            db.session.add(f4)
            db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


@paid_bp.route('/paid/download', methods=['GET'])
def download():
    pid = request.args.get('pid')
    f4 = Fee4.query.filter(Fee4.id == pid).first()
    return down(f4.filename, f4.path)
