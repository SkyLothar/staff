def init_app(app):
    from . import models


def init_admin():
    from ..ext import admin, db, AuthModelView
    from .models import User, Role

    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Role, db.session))
