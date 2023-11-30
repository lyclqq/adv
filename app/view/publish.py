from flask import Blueprint, render_template

from app.models.bill import Fee2

publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/list', methods=["GET", "POST"])
def publish_list():
    fee2 = Fee2.query.all()
    return render_template('publish/publish_list.html', fee2=fee2)
