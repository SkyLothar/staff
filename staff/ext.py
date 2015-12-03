from flask import request, url_for, redirect
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, current_user


admin = Admin(name="staff", template_mode="bootstrap3")
db = SQLAlchemy()
cache = Cache()
security = Security()


class AuthModelView(ModelView):
    column_exclude_list = ["created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]

    def is_accessible(self):
        return current_user.has_role("admin")

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("security.login", next=request.url))
