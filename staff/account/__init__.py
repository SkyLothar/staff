from ..signals import after_boot


def init_app(app):
    from . import models
    from .api import api
    from .forms import LDAPLoginForm

    from ..ext import db, security

    from flask_security import SQLAlchemyUserDatastore

    datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, datastore, login_form=LDAPLoginForm)

    app.register_blueprint(api)


@after_boot.connect
def init_admin(app):
    from ..ext import admin, db, AuthModelView
    from .models import User, Role

    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Role, db.session))
