from .ext import db

__all__ = ["create_app", "db"]


def create_app(config):
    from os import environ

    from flask import Flask, render_template
    app = Flask(__name__)
    app.config.from_pyfile(config)

    app.config.update({
        key: val
        for key, val in environ.items()
        if key.startswith("STAFF") and key.isupper()
    })
    db.init_app(app)

    from .ext import admin, cache, security
    # init admin
    admin.init_app(app)
    # init cache
    cache.init_app(app)
    # init security
    from .account.models import User, Role
    from flask.ext.security import SQLAlchemyUserDatastore, login_required
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore)

    from . import account, wechat, gitlab

    account.init_app(app)
    wechat.init_app(app)
    gitlab.init_app(app)

    account.init_admin()
    wechat.init_admin()
    gitlab.init_admin()

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
