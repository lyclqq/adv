from sqlalchemy.sql import func
from app import db
from app.models import Basecls
from werkzeug.security import generate_password_hash, check_password_hash

#用户表
class Users(Basecls):
    __tablename__ = 'users'

    username = db.Column(db.String(20), nullable=False)
    type = db.Column(db.Strign(20))
    status = db.Column(db.String(10))
    notes = db.Column(db.Strign(250))
    group_id=db.Column(db.Integer, default=0)
    passwd=db.Column(db.String(128), nullable=False)
    updatetime= db.Column(db.DateTime, default=func.now())

    #校验密码,返回的是True或者False
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #使用的是sha256算法加密
    def set_password(self, value):
        self.password_hash = generate_password_hash(value)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "username": self.username,
            "status": self.status,
            "updatetime": self.updatedate.strftime("%Y-%m-%d %H:%M")
        }
        return resp_dict


#用户表
class Groups(Basecls):
    __tablename__ = 'groups'

    groupname = db.Column(db.String(20), nullable=False)
    type = db.Column(db.Strign(20))
    status = db.Column(db.String(10))
    notes = db.Column(db.Strign(250))
    flag=db.Column(db.Float,default=0)


