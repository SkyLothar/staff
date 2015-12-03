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
    wx_user_id = prompt("wx_user_id")
    password = prompt_pass("password")

    datastore = app.extensions["security"].datastore
    user = datastore.find_user(wx_user_id=wx_user_id)
    if user is None:
        user = datastore.create_user(wx_user_id=wx_user_id, password=password)
        datastore.put(user)
    role = datastore.find_or_create_role("admin")
    datastore.add_role_to_user(user, role)
    datastore.commit()


if __name__ == "__main__":
    manager.app = app
    migrate = flask.ext.migrate.Migrate(app, db)
    manager.run()
