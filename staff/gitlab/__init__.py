def init_app(app):
    from . import models
    from . import config
    config.base_url = app.config["GITLAB_BASE_URL"]
    config.appid = app.config["GITLAB_APPID"]
    config.secret = app.config["GITLAB_SECRET"]
    config.callback = app.config["GITLAB_CALLBACK"]
    return models


def init_admin():
    from ..ext import admin, db, AuthModelView
    from .models import GitlabAccount

    admin.add_view(AuthModelView(GitlabAccount, db.session))
