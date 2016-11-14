from flask.ext.security import UserMixin, RoleMixin

from ..ext import db
from ..ldap import ldap
from ..mixin import BasicMixin


roles_users = db.Table(
    "roles_users", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"))
)


class Role(db.Model, BasicMixin, RoleMixin):
    __tablename__ = "role"

    name = db.Column(db.Unicode(63), unique=True, nullable=False)

    def __str__(self):
        return str(self.name)


class User(db.Model, BasicMixin, UserMixin):
    __tablename__ = "user"

    username = db.Column(db.Unicode(63), unique=True, index=True)

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
        return "{0}".format(self.name)

    def verify(self, password):
        return ldap.check_password(self.name, password)
