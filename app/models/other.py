from sqlalchemy.sql import func
from app import db
from app.models import Basecls

#附件
class Files(Basecls):
    __tablename__ = 'files'

    notes = db.Column(db.Strign(250))
    status = db.Column(db.String(10))
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    order_id=db.Column(db.Integer, default=0)
    iuser_id=db.Column(db.Integer, default=0)
    cuser_id=db.Column(db.Integer, default=0)

#附件
class Reports(Basecls):
    __tablename__ = 'reports'

    title = db.Column(db.Strign(250))
    iuser_id = db.Column(db.Integer, default=0)
    filename=db.Column(db.String(200))
    path=db.Column(db.String(20))
    type = db.Column(db.String(20))