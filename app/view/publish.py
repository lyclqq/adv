from flask import Blueprint, render_template, request

from app import db
from app.models.bill import Fee2
from app.models.contract import Orders

# 刊登
publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/list', methods=["GET", "POST"])
def publish_list():
    orders = Orders.query.all()
    ids = ''
    names = ''
    for o in orders:
        names = names + ',' + o.title
        ids = ids + ',' + str(o.id)
    fee2 = Fee2.query.all()
    return render_template('publish/publish_list.html', fee2=fee2, names=names, ids=ids)


@publish_bp.route('/publish/add', methods=["POST"])
def publish_add():
    order_id = request.form.get('order_id')
    file = request.files.get('filename')
    f = Fee2(
    )
    f.fee = float(request.form.get('fee'))
    f.order_id = int(order_id)
    f.area = float(request.form.get('area'))
    f.feedate = request.form.get('feedate')
    f.pagename = request.form.get('pagename')
    f.status = '未审'

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
