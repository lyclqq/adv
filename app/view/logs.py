from flask import Blueprint, render_template
from app.common import is_login
from app.models.system import Logs, Users

# 日志
log_bp = Blueprint('log', __name__)

pagesize = 15


# 列表页
@log_bp.route('/log/list/<int:page>', methods=["GET", "POST"])
@is_login
def log_list(page):
    q = Logs.query
    pagination = q.order_by(Logs.create_datetime.desc()).paginate(page=page, per_page=pagesize, error_out=False)
    return render_template('log/log_list.html', pagination=pagination)


# 查询用户信息
def get_user_dict():
    d = dict()
    us = Users.query.all()
    for u in us:
        d[u.id] = u.username
    return d
