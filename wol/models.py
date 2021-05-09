from peewee import *
from playhouse.flask_utils import FlaskDB

from .doc_utils import exclude_parent_attrs

__all__ = ['db', 'Credentials', 'Target', 'WakeUpSchedule']

db = FlaskDB()


class Credentials(db.Model):
    username = CharField()
    password = CharField(null=True)
    pkey = TextField(null=True)


class Target(db.Model):
    name = CharField()
    host = CharField(null=True)
    mac = CharField(null=True)
    wol_port = IntegerField(null=True)
    credentials = ForeignKeyField(Credentials, backref='targets', null=True)


class WakeUpSchedule(db.Model):
    enabled = BooleanField(default=True)
    target = ForeignKeyField(Target, backref='wakeup_schedules')
    # TODO: schedule settings


def init_db():
    db.database.create_tables([Credentials, Target, WakeUpSchedule])


for model in (Credentials, Target, WakeUpSchedule):
    exclude_parent_attrs(model, ('id',))
