from app import db
from app.models import Basecls
from sqlalchemy import or_, and_, not_
from flask import current_app
from sqlalchemy.sql import func

#客户表
class Customers(db.Model,Basecls):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.String(250))
    status = db.Column(db.String(10))
    orders = db.relationship('Orders', backref='customer', lazy='dynamic')

 #分页查询，支持多关键字
    def search_customers(self,keywords,page=1):
        pagerows=current_app.config['PAGEROWS']
        if keywords is None:
            pagination = Customers.query.order_by(Customers.id.desc()).paginate(page,per_page=pagerows)
        else:
            keys=keywords.split(',')
            pagination = Customers.query.filter(Customers.name.in_(keys)).order_by(Customers.id.desc()).paginate(page,per_page=pagerows)
        return pagination

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
    wordcount=db.Column(db.Integer, default=0)
    publiccount=db.Column(db.Integer, default=0)
    area = db.Column(db.Float, default=0)
    name = db.Column(db.String(200))
    notes = db.Column(db.Text)
    cutomer_id=db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    group_id=db.Column(db.Integer, db.ForeignKey('usergroup.id'), nullable=False)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)
    contract_date=db.Column(db.Date)
    ordernumber=db.Column(db.String(200))
    update_datetime=db.Column(db.DateTime, default=func.now())

    #分页查询，支持多关键字
    def search_orders(self,keywords,status='全部',page=1):
        pagerows=current_app.config['PAGEROWS']

        if keywords is None:
            if status =='全部':
                pagination = Orders.query.order_by(Orders.id.desc()).paginate(page,per_page=pagerows)
            else:
                pagination = Orders.query.filter( Orders.status == status).order_by(
                    Orders.id.desc()).paginate(page, per_page=pagerows)
            return pagination
        keys=keywords.split(',')

        if status =='全部':
            pagination = Orders.query.filter(Orders.name.in_(keys)).order_by(Orders.id.desc()).paginate(page,per_page=pagerows)
        else:
            pagination = Orders.query.filter(Orders.name.in_(keys),Orders.status==status).order_by(Orders.id.desc()).paginate(page, per_page=pagerows)

        return pagination
