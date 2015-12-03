#!/usr/bin/env python

import os

import flask.ext.migrate

from flask.ext.script import Manager, prompt, prompt_pass

from staff import create_app, db

__curdir__ = os.path.realpath(os.path.dirname(__file__))
config_path = os.path.join(__curdir__, "config.cfg")

app = None
if os.path.isfile(config_path):
    app = create_app(config_path)

manager = Manager()
manager.add_command("db", flask.ext.migrate.MigrateCommand)


@manager.command
def superuser():
    from staff.utils import get_uid
    email = prompt("email")
    password = prompt_pass("password")

    datastore = app.extensions["security"].datastore
    user = datastore.find_user(email=email)
    if user is None:
        user = datastore.create_user(email=email, wx_user_id=get_uid())
        datastore.put(user)

    user.password = password
    role = datastore.find_or_create_role("admin")
    datastore.add_role_to_user(user, role)
    datastore.commit()


if __name__ == "__main__":
    manager.app = app
    migrate = flask.ext.migrate.Migrate(app, db)
    manager.run()
