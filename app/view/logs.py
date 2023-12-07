from flask import Blueprint, render_template, session
from app.models.system import Logs

# 日志
log_bp = Blueprint('log', __name__)


@log_bp.route('/log/list', methods=["GET", "POST"])
def log_list():
    if session.get('user_id'):
        userid = int(session.get('user_id'))
        logs = Logs.query.filter(Logs.user_id == userid).all()
        return render_template('log/log_list.html', logs=logs)
    else:
        return render_template('log/log_list.html')
