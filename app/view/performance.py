from flask import Blueprint

# 绩效
performance_bp = Blueprint('performance', __name__)


@performance_bp.route('/performance/list', methods=["GET", "POST"])
def performance_list():
    return '2222'
