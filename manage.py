# -*- coding: utf-8 -*-
from app import create_app, db
import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Role, Permission, Post


app = create_app(os.environ.get('CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db=db)


def make_shell_context():
    return dict(
        app=app,
        db=db, User=User, Role=Role, Permission=Permission,
        Post=Post
    )


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """
    :summary: 运行测试用例命令
    :return:
    """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
