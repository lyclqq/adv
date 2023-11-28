from sqlalchemy.sql import func
from app import db
import click
class Basecls(object):

    create_datetime = db.Column(db.DateTime, default=func.now())

