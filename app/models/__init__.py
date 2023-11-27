from sqlalchemy.sql import func
from app import db

class Basecls(db.Model):

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    create_datetime = db.Column(db.DateTime, default=func.now())