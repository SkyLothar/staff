from .ext import db

__all__ = ["create_app", "db"]


def create_app(config):
    from flask import Flask
    app = Flask(__name__)
    app.config.from_pyfile(config)

    db.init_app(app)

    from .ext import admin
    # init admin
    admin.init_app(app)

    from .ldap import ldap
    ldap.init_app(app)

    from . import account

    account.init_app(app)

    from .signals import after_boot
    after_boot.send(app)
    return app
