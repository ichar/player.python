#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app, db
from flask.ext.script import Manager, Shell
from config import setup_console, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy import func, asc, desc, and_, or_

from app.models import Pagination, User, Module, Parameter, Item, Order, Price, print_all, log, statistics, get_log, print_log, \
     model_order_columns, model_price_columns, custom_orders, price_region_test, \
     tag, clean, worder

from migrate.versioning import api
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict( \
            app=app, db=db,
            Pagination=Pagination, func=func, asc=asc, desc=desc, and_=and_, or_=or_,
            User=User, Module=Module, Parameter=Parameter, Item=Item, Order=Order, Price=Price, 
            model_order_columns=model_order_columns, model_price_columns=model_price_columns,
            print_all=print_all, log=log, statistics=statistics, get_log=get_log, print_log=print_log, 
            tag=tag, clean=clean, worder=worder, custom_orders=custom_orders,
            price_region_test=price_region_test,
    )
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

setup_console()

if __name__ == '__main__':
    manager.run()
