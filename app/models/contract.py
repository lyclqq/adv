from app import db
from app.models import Basecls


#客户表
class Customers(db.Model,Basecls):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))


#合同表
class Orders(db.Model,Basecls):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(10))
    Fee11=db.Column(db.Float,default=0)
    Fee21 = db.Column(db.Float, default=0)
    Fee31 = db.Column(db.Float, default=0)
    Fee41 = db.Column(db.Float, default=0)
    Fee51 = db.Column(db.Float, default=0)
    Fee61 = db.Column(db.Float, default=0)
    Fee22 = db.Column(db.Float, default=0)
    Fee42 = db.Column(db.Float, default=0)
    Fee52=db.Column(db.Float,default=0)
    Fee62 = db.Column(db.Float, default=0)
    wordnumber=db.Column(db.Integer,default=0)
    wordnumber = db.Column(db.Integer, default=0)
    wordcount=db.Column(db.Integer, default=0)
    publiccount=db.Column(db.Integer, default=0)
    area = db.Column(db.Float, default=0)
    name = db.Column(db.String(200))
    notes = db.Column(db.Text)
    cutomer_id=db.Column(db.Integer, default=0)
    group_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)
    contract_date=db.Column(db.Date)
