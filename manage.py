from flask_script import Manager, Shell
from app import app, db
import psycopg2
from flask_migrate import Migrate, MigrateCommand
import os

manager = Manager(app)


migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    db.create_all()


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
