from peewee import *
from playhouse.db_url import connect

from .doc_utils import exclude_parent_attrs

__all__ = ['db', 'Credentials', 'Target']

db = DatabaseProxy()


class DbModel(Model):
    class Meta:
        database = db


class Credentials(DbModel):
    username = CharField()
    password = CharField(null=True)
    pkey = TextField(null=True)


class Target(DbModel):
    name = CharField()
    host = CharField(null=True)
    mac = CharField(null=True)
    wol_port = IntegerField(null=True)
    credentials = ForeignKeyField(Credentials, backref='targets', null=True)


def connect_db(url: str):
    db.initialize(connect(url))


def init_db():
    db.create_tables([Credentials, Target])


for model in (Credentials, Target):
    exclude_parent_attrs(model, ('id',))
