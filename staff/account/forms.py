from flask_security.forms import Form, NextFormMixin
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

from ..ext import db
from ..ldap import ldap

from .models import User


class LDAPLoginForm(Form, NextFormMixin):
    username = StringField("用户名")
    password = PasswordField("密码")
    submit = SubmitField("登入")

    def validate(self):
        if not super(LDAPLoginForm, self).validate():
            return False

        username = self.username.data.strip()
        if not username:
            self.username.errors.append("USER NAME NOT PROVIDED")
            return False

        password = self.password.data.strip()
        if not password:
            self.password.errors.append("PASSWORD NOT PROVIDED")
            return False

        if not ldap.check_password(username, password):
            self.password.errors.append("INVALID PASSWORD")

        self.user = User.find_or_create(username=username)

        if db.session.new or self.user.is_active:
            return True
        else:
            self.username.errors.append("ACCOUNT IS DISABLED")
            return False


class CreateUserForm(Form):
    username = StringField("用户名", validators=[DataRequired()])

    surname = StringField("姓", validators=[DataRequired()])
    given_name = StringField("名", validators=[DataRequired()])

    password = PasswordField("密码", validators=[DataRequired()])

    def validate(self):
        if not super(CreateUserForm, self).validate():
            return False
        username = self.username.data.strip()
        if ldap.is_user_exists(username):
            self.username.errors.append(
                "user[{0}] already exists".format(username)
            )
            return False
        return True
