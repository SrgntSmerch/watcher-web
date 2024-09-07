"""Peewee migrations -- 001_migrate.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    
    @migrator.create_model
    class BaseModel(pw.Model):
        id = pw.AutoField()

        class Meta:
            table_name = "basemodel"

    @migrator.create_model
    class Event(pw.Model):
        type = pw.CharField(max_length=255)
        date = pw.DateField()
        time = pw.TimeField()
        status = pw.CharField(default='init', max_length=255)

        class Meta:
            table_name = "event"

    @migrator.create_model
    class Detection(pw.Model):
        mode = pw.CharField(default='generic', max_length=255)
        type = pw.CharField(max_length=255)
        confidence = pw.SmallIntegerField()
        x1 = pw.SmallIntegerField()
        x2 = pw.SmallIntegerField()
        y1 = pw.SmallIntegerField()
        y2 = pw.SmallIntegerField()
        relation = pw.ForeignKeyField(column_name='relation_id', field='id', model=migrator.orm['event'])

        class Meta:
            table_name = "detection"

    @migrator.create_model
    class Media(pw.Model):
        file = pw.TextField()
        type = pw.CharField(max_length=255)
        relation = pw.ForeignKeyField(column_name='relation_id', field='id', model=migrator.orm['event'])

        class Meta:
            table_name = "media"


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
    migrator.remove_model('media')

    migrator.remove_model('detection')

    migrator.remove_model('event')

    migrator.remove_model('basemodel')
