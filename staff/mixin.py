from .ext import db
from .utils import utcnow


class BasicMixin(object):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=utcnow,
        onupdate=utcnow
    )

    @classmethod
    def find_or_create(cls, **kwargs):
        if kwargs:
            item = cls.query.filter_by(**kwargs).first()
            if item is None:
                item = cls(**kwargs)
                db.session.add(item)
            return item
        raise ValueError("parameter is empty!")
