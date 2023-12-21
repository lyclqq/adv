from flask import Blueprint, render_template, session
from app.models.system import Logs, Users

# 日志
log_bp = Blueprint('log', __name__)

pagesize = 15


@log_bp.route('/log/list/<int:page>', methods=["GET", "POST"])
def log_list(page):
    q = Logs.query
    if session.get('user_id'):
        userid = int(session.get('user_id'))
        q = q.filter(Logs.user_id == userid)
    pagination = q.order_by(Logs.create_datetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    udict = get_user_dict()
    return render_template('log/log_list.html', pagination=pagination, udict=udict)


def get_user_dict():
    d = dict()
    us = Users.query.all()
    for u in us:
        d[u.id] = u.username
    return d
