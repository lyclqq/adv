from flask import Blueprint

paid_bp = Blueprint('paid', __name__)


@paid_bp.route('/paid/list', methods=["GET", "POST"])
def paid_list():
    return '111111'
