from flask.ext.security import UserMixin, RoleMixin

from ..ext import db
from ..mixin import BasicMixin


roles_users = db.Table(
    "roles_users", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"))
)


class Role(db.Model, BasicMixin, RoleMixin):
    __tablename__ = "role"

    name = db.Column(db.Unicode(255), unique=True, nullable=False)
    description = db.Column(db.Unicode(255))

    def __str__(self):
        return str(self.name)


class User(db.Model, BasicMixin, UserMixin):
    __tablename__ = "user"

    wx_user_id = db.Column(
        db.Unicode(255), nullable=False, unique=True, index=True
    )
    password = db.Column(db.Unicode(255))

    name = db.Column(db.Unicode(255))
    avatar = db.Column(db.Unicode(1024))
    email = db.Column(db.Unicode(255))
    comment = db.Column(db.UnicodeText)

    gitlab_account_id = db.Column(
        db.Integer,
        db.ForeignKey("gitlab_account.id")
    )
    gitlab_account = db.relationship(
        "GitlabAccount",
        uselist=False, backref="user"
    )

    active = db.Column(db.Boolean, default=False)
    # confirmable SECURITY_CONFIRMABLE
    confirmed_at = db.Column(db.DateTime)
    # trackable SECURITY_TRACKABLE
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.Unicode(255))
    current_login_ip = db.Column(db.Unicode(255))
    login_count = db.Column(db.Integer, default=0)

    roles = db.relationship(
        Role, secondary=roles_users,
        backref=db.backref("users", lazy="dynamic")
    )

    def __str__(self):
        return "{0}".format(self.name or self.wx_user_id)

    @classmethod
    def create(cls, wx_user_id):
        user = cls.query.filter_by(wx_user_id=wx_user_id).first()
        if user is None:
            user = cls(wx_user_id=wx_user_id)
            db.session.add(user)
        return user
