import datetime
import os
from nanoid import generate
from flask import Blueprint, render_template, request, current_app, send_from_directory, make_response, session
from sqlalchemy import and_
from app import db
from app.common import ins_logs, is_login
from app.models.bill import Fee2
from app.models.contract import Orders

# 刊登
publish_bp = Blueprint('publish', __name__)

pagesize = 10

stat_dict = {"0": "未审", "1": "已审", "2": "作废"}


# 列表页
@publish_bp.route('/publish/list/<int:page>', defaults={"qr_status": "-1", "qr_order": ""}, methods=["GET", "POST"])
@publish_bp.route('/publish/list/<int:page>/', methods=["GET", "POST"])
@is_login
def publish_list(page):
    q = Fee2.query
    qr_status = request.args.get('qr_status')
    qr_order = request.args.get('qr_order')
    if qr_status is not None and qr_status != '-1':
        q = q.filter(Fee2.status == qr_status)
    if qr_order is not None and qr_order != '':
        q = q.filter(Fee2.order_id == qr_order)
    pagination = q.order_by(Fee2.create_datetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('publish/publish_list.html', pagination=pagination,
                           stat_dict=stat_dict, qr_status=qr_status)


# 添加页
@publish_bp.route('/publish/to_add', defaults={"fid": -1}, methods=["GET"])
@publish_bp.route('/publish/to_add/<int:fid>', methods=["GET"])
def publish_to_add(fid):
    t = get_order_list()
    ids = t[1]
    names = t[0]
    if fid != -1:
        f2 = Fee2.query.filter(Fee2.id == fid).first()
        o = Orders.query.filter(Orders.id == f2.order_id).first()
    else:
        f2 = None
        o = None
    return render_template('publish/publish_add.html', names=names, ids=ids,
                           stat_dict=stat_dict, f2=f2, o=o)


# 添加方法
@publish_bp.route('/publish/add', methods=["POST"])
def publish_add():
    order_id = request.form.get('order_id')
    fid = request.form.get('fid')
    if fid != '':
        f = Fee2.query.filter(Fee2.id == fid).first()
    else:
        f = Fee2(
        )
        f.order_id = int(order_id)
    file = request.files.get('filename')
    #
    if file:
        old_file_check(f.filename, f.path)
        t = handle_file(file)
        f.filename = t[0]
        f.path = t[1]
    #
    f.fee = float(request.form.get('fee'))
    f.area = float(request.form.get('area'))
    f.feedate = request.form.get('feedate')
    f.pagename = request.form.get('pagename')
    f.status = '0'
    f.money = request.form.get('money')
    f.notes = request.form.get('notes')
    f.iuser_id = session.get("user_id")
    #
    db.session.add(f)
    db.session.commit()
    re = '{"result":"ok"}'
    if fid != '':
        ins_logs(session.get("user_id"), '刊登数据修改', 'fee2')
    else:
        ins_logs(session.get("user_id"), '刊登数据新增', 'fee2')
    return re


# 查询合同信息
def get_order_list():
    ids = ''
    names = ''
    orders = Orders.query.all()
    for o in orders:
        ids = ids + ',' + str(o.id)
        names = names + ',' + o.title
    t = (names, ids)
    return t


# 作废
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


# 审核方法
@publish_bp.route('/publish/audit', methods=["POST"])
def publish_audit():
    pid = request.form.get('pid')
    status = request.form.get('status')
    f2 = Fee2.query.filter(Fee2.id == pid).first()
    if f2:
        if f2.status != status:
            f2.status = status
            f2.cuser_id = session.get("user_id")
            db.session.add(f2)
            db.session.commit()
        re = '{"result":"ok"}'
    else:
        re = '{"result":"wrong"}'
    return re


# 附件下载
@publish_bp.route('/publish/download', methods=['GET'])
def download():
    pid = request.args.get('pid')
    f2 = Fee2.query.filter(Fee2.id == pid).first()
    return down(f2.filename, f2.path)


# 上传文件处理
def handle_file(file):
    # old_name = file.filename[0:file.filename.rindex('.')]
    ext = file.filename.split('.')[-1].lower()
    parent_path = datetime.datetime.now().strftime("%Y") + os.sep
    # , current_app.config['UPLOAD_FOLDER']
    abs_path = os.path.join(current_app.root_path, 'static', 'files', parent_path)
    if not os.path.exists(abs_path):
        os.mkdir(abs_path)
    new_name = generate(size=10) + '.' + ext
    file.save(abs_path + new_name)
    # new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], datetime.datetime.now().strftime("%Y") + os.sep) + new_name
    return [new_name, parent_path]


# 附件下载
def down(name, path):
    is_file = os.path.isfile(os.path.join(current_app.root_path, 'static', 'files', path, name))
    if is_file:
        # 路径
        # print(f2.path[0:str(f2.path).rindex('\\')])
        # 名字
        # print(f2.path[str(f2.path).rindex('\\') + 1:])
        # print(path[str(path).rindex('.'):])
        # print(os.path.join(current_app.root_path, 'static', 'files', path))
        response = make_response(send_from_directory(os.path.join(current_app.root_path, 'static', 'files', path), name, download_name=name, as_attachment=True))
        return response


# 上传新附件时，删除旧附件
def old_file_check(name, path):
    if name is not None and path is not None:
        file = os.path.join(current_app.root_path, 'static', 'files', path, name)
        if os.path.isfile(file):
            os.remove(file)
