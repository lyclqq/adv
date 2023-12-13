import datetime
import os
from nanoid import generate
from flask import Blueprint, render_template, request, current_app, send_from_directory, make_response
from sqlalchemy import and_

from app import db
from app.models.bill import Fee2
from app.models.contract import Orders

# 刊登
publish_bp = Blueprint('publish', __name__)

pagesize = 10

stat_dict = {"0": "未审", "1": "已审", "2": "作废"}


@publish_bp.route('/publish/list/<int:page>', defaults={"qr_status": "-1", "qr_order": ""}, methods=["GET", "POST"])
@publish_bp.route('/publish/list/<int:page>/', methods=["GET", "POST"])
def publish_list(page):
    ids = ''
    names = ''
    orders = Orders.query.all()
    for o in orders:
        names = names + ',' + o.title
        ids = ids + ',' + str(o.id)
    q = Fee2.query
    qr_status = request.args.get('qr_status')
    qr_order = request.args.get('qr_order')
    if qr_status is not None and qr_status != '-1':
        q = q.filter(Fee2.status == qr_status)
    if qr_order is not None and qr_order != '':
        q = q.filter(Fee2.order_id == qr_order)
    pagination = q.paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('publish/publish_list.html', pagination=pagination, names=names, ids=ids,
                           stat_dict=stat_dict, qr_status=qr_status, qr_order=qr_order)


@publish_bp.route('/publish/add', methods=["POST"])
def publish_add():
    order_id = request.form.get('order_id')
    f = Fee2(
    )
    file = request.files.get('filename')
    if file:
        t = handle_file(file)
        f.filename = t[0]
        f.path = t[1]
    #
    f.order_id = int(order_id)
    f.fee = float(request.form.get('fee'))
    f.area = float(request.form.get('area'))
    f.feedate = request.form.get('feedate')
    f.pagename = request.form.get('pagename')
    f.status = '0'
    f.money = request.form.get('money')
    f.notes = request.form.get('notes')
    #
    db.session.add(f)
    db.session.commit()
    re = '{"result":"ok"}'
    return re


def get_order_list():
    orders = Orders.query.all()
    names = []
    ids = []
    for o in orders:
        ids.append(o.id)
        names.append(o.title)
    re = '[{"names":' + str(names) + '},{"ids":' + str(ids) + '}]'
    return re


@publish_bp.route('/publish/cancel', methods=["POST"])
def publish_cancel():
    pid = request.form.get('pid')
    f2 = Fee2.query.filter(and_(Fee2.id == pid, Fee2.status != '作废')).first()
    if f2:
        f2.status = '2'
        db.session.add(f2)
        db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


@publish_bp.route('/publish/audit', methods=["POST"])
def publish_audit():
    pid = request.form.get('pid')
    status = request.form.get('status')
    f2 = Fee2.query.filter(Fee2.id == pid).first()
    if f2:
        if f2.status != status:
            f2.status = status
            db.session.add(f2)
            db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


@publish_bp.route('/publish/download', methods=['GET'])
def download():
    pid = request.args.get('pid')
    f2 = Fee2.query.filter(Fee2.id == pid).first()
    return down(f2.path)


def handle_file(file):
    old_name = file.filename[0:file.filename.rindex('.')]
    ext = file.filename.split('.')[-1].lower()
    abs_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], datetime.datetime.now().strftime("%Y") + os.sep)
    if not os.path.exists(abs_path):
        os.mkdir(abs_path)
    new_name = generate(size=10) + '.' + ext
    file.save(abs_path + new_name)
    new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], datetime.datetime.now().strftime("%Y") + os.sep) + new_name
    return [old_name, new_path]


def down(path):
    is_file = os.path.isfile(os.path.join(current_app.root_path, path))
    if is_file:
        # 路径
        # print(f2.path[0:str(f2.path).rindex('\\')])
        # 名字
        # print(f2.path[str(f2.path).rindex('\\') + 1:])
        response = make_response(send_from_directory(os.path.join(current_app.root_path, path[0:str(path).rindex('\\')]), path[str(path).rindex('\\') + 1:], as_attachment=True))
        return response
