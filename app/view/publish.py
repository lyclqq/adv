from flask import Blueprint, render_template, request

from app.models.bill import Fee2

# 刊登
publish_bp = Blueprint('publish', __name__)


@publish_bp.route('/publish/list', methods=["GET", "POST"])
def publish_list():
    fee2 = Fee2.query.all()
    return render_template('publish/publish_list.html', fee2=fee2)


@publish_bp.route('/p/i', methods=["GET", "POST"])
def index():
    return render_template('index24.html')
