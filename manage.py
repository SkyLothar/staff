#!/usr/bin/env python

import os

import flask.ext.migrate

from flask.ext.script import Manager

from staff import create_app, db

__curdir__ = os.path.realpath(os.path.dirname(__file__))
config_path = os.path.join(__curdir__, "config.cfg")

manager = Manager()
manager.add_command("db", flask.ext.migrate.MigrateCommand)


if __name__ == "__main__":
    app = create_app(config_path)
    manager.app = app
    migrate = flask.ext.migrate.Migrate(app, db)
    manager.run()
