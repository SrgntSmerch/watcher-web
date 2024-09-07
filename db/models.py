from peewee import (Model, CharField, TextField,
                    SmallIntegerField, PrimaryKeyField, DateField, TimeField, ForeignKeyField)

from db import db

class BaseModel(Model):
    """A base model that will use our MySQL database"""

    class Meta:
        database = db


class Event(BaseModel):
    id = PrimaryKeyField()
    type = CharField()
    date = DateField(index=True)
    time = TimeField()
    status = CharField(default='init')
    cleaned = DateField()
    source = CharField()


class Media(BaseModel):
    id = PrimaryKeyField()
    file = TextField()
    type = CharField()
    relation = ForeignKeyField(model=Event)


class Detection(BaseModel):
    id = PrimaryKeyField()
    mode = CharField(default='generic')
    type = CharField()
    confidence = SmallIntegerField()
    x1 = SmallIntegerField()
    x2 = SmallIntegerField()
    y1 = SmallIntegerField()
    y2 = SmallIntegerField()
    relation = ForeignKeyField(model=Event)