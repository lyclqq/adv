from flask import Blueprint, render_template, request, url_for, redirect
from app import db
from app.models.system import Systeminfo

system_info_bp = Blueprint('system_info', __name__)


@system_info_bp.route('info/show', defaults={"edit": 0})
@system_info_bp.route('info/show/<int:edit>')
def info_show(edit):
    si = Systeminfo.query.first()
    return render_template('system_info/info_show.html', si=si, edit=edit)


@system_info_bp.route('info/update', methods=["POST"])
def info_update():
    sid = request.form.get('id')
    si = Systeminfo.query.filter(Systeminfo.id == sid).first()
    si.propor = float(request.form.get('propor'))
    db.session.add(si)
    db.session.commit()
    return redirect(url_for('system_info.info_show'))


@system_info_bp.route('info/get', methods=["GET"])
def info_get():
    si = Systeminfo.query.first()
    m = si.systemmonth.strftime("%Y-%m")
    re = '{"result":"' + m + '"}'
    return re
