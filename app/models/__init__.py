from sqlalchemy.sql import func
from app import db


class Basecls(object):

    create_datetime = db.Column(db.DateTime, default=func.now())

