from uuid import uuid4
from datetime import datetime


def utcnow():
    return datetime.utcnow()


def get_uid():
    return uuid4().hex
