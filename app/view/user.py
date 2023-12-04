from app.common import is_login
from flask import Blueprint,render_template,current_app,url_for,redirect,session,request,flash,g
from app import db
from app.models.system import Users
from app.forms.user import PwdForm


userView=Blueprint('user',__name__)

@userView.route('/editpwd',methods=["GET","POST"])
@is_login
def editpwd():
    form=PwdForm()
    form.username.data=session.get("username")
    if form.validate_on_submit():
        if form.password1.data==form.password2.data and len(form.password1.data)>5:
            userid=int(session.get('user_id'))
            user = Users.query.get(userid)
            user.set_password(form.password1.data)
            db.session.add(user)
            db.session.commit()
            flash('密码修改成功')
        else:
            flash('密码不能太短')
    return render_template('admin/pwd.html',form=form)