from sqlalchemy.sql import func
from app import db
from app.models import Basecls
from werkzeug.security import generate_password_hash, check_password_hash


#用户表
class Users(db.Model,Basecls):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20))
    status = db.Column(db.String(10))
    notes = db.Column(db.String(250))
    group_id=db.Column(db.Integer, default=0)
    passwd=db.Column(db.String(128))
    updatetime= db.Column(db.DateTime, default=func.now())

    #校验密码,返回的是True或者False
    def check_password(self, password):
        return check_password_hash(self.passwd, password)

    #使用的是sha256算法加密
    def set_password(self, value):
        self.passwd = generate_password_hash(value)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "username": self.username,
            "status": self.status,
            "updatetime": self.updatedate.strftime("%Y-%m-%d %H:%M")
        }
        return resp_dict


#用户部门表
class Groups(db.Model):
    __tablename__ = 'usergroup'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    groupname = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20))
    status = db.Column(db.String(10))
    notes = db.Column(db.String(250))
    flag=db.Column(db.Float,default=0)


#日志
class Logs(db.Model,Basecls):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default=0)
    type = db.Column(db.String(20))
    ip = db.Column(db.String(20))
    notes = db.Column(db.String(250))
