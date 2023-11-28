from sqlalchemy.sql import func
from app import db
from app.models import Basecls

#合同金额
class Fee1(db.Model,Basecls):
    __tablename__ = 'fee1'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    fee=db.Column(db.Float,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#己刊登金额
class Fee2(db.Model,Basecls):
    __tablename__ = 'fee2'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    fee=db.Column(db.Float,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    area = db.Column(db.Float, default=0)
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    pagename = db.Column(db.String(30))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#己开发票金额
class Fee3(db.Model,Basecls):
    __tablename__ = 'fee3'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    fee=db.Column(db.Float,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#己到帐金额
class Fee4(db.Model,Basecls):
    __tablename__ = 'fee4'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    fee=db.Column(db.Float,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#己发绩效金额
class Fee5(db.Model,Basecls):
    __tablename__ = 'fee5'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    fee=db.Column(db.Float,default=0)
    prize=db.Column(db.Float,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#字数
class Wordnumbers(db.Model,Basecls):
    __tablename__ = 'wordnumbers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feedate = db.Column(db.DateTime, default=func.now())
    wordnumber=db.Column(db.Integer,default=0)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)
    type=db.Column(db.String(10))