from peewee import *
from playhouse.flask_utils import FlaskDB 

from app import app

__all__ = ['db', 'Credentials', 'Target', 'WakeUpSchedule']


db = FlaskDB(app)


class Credentials(db.Model):
    username = CharField()
    password = CharField(null=True)
    pkey = TextField(null=True)


class Target(db.Model):
    host = CharField(null=True)
    mac = CharField(null=True)
    wol_port = IntegerField(null=True)
    credentials = ForeignKeyField(Credentials, backref='targets', null=True)


class WakeUpSchedule(db.Model):
    enabled = BooleanField(default=True)
    target = ForeignKeyField(Target, backref='wakeup_schedules')
    # TODO: расписание
