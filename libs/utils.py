from datetime import datetime
from uuid import uuid4
from sqlalchemy import inspect


def generate_id():
    id = str(uuid4())
    return id


def now():
    return datetime.now()


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
