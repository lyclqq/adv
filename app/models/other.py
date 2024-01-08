from app import db
from app.models import Basecls


#附件
class Files(db.Model,Basecls):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)


#报表
class Reports(db.Model,Basecls):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250))
    iuser_id=db.Column(db.Integer, default=0)
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    type = db.Column(db.String(20))

#历史统计数据
class History(db.Model,Basecls):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    type = db.Column(db.String(10))
    fee=db.Column(db.Float,default=0)
    fee_date=db.Column(db.Date)