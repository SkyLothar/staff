def init_app(app):
    from .api import api
    from . import models
    from . import config

    config.corpid = app.config["WECHAT_CORPID"]
    app.register_blueprint(api)


def init_admin():
    from ..ext import admin, db, AuthModelView
    from .models import WechatApp

    admin.add_view(AuthModelView(WechatApp, db.session))
