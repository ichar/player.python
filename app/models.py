# -*- coding: utf-8 -*-

import re
import time, pytz
from math import ceil

from app import db
from datetime import datetime
from config import \
     default_language_types, default_country_types, default_region_types, default_currency_names, default_rating_types, \
     default_encoding, default_unicode, default_print_encoding, errorlog, \
     valid_parameter_types, valid_parameter_names, valid_order_types, valid_order_names, n_a, print_to, \
     RATING_UNDEFINED, RATING_UP, RATING_EQUAL, RATING_DOWN, \
     DEFAULT_COUNTRY, DEFAULT_CURRENCY, CURRENCY_RATES, \
     ORDER_STANDARD, ORDER_CUSTOM, ORDER_DONE, \
     LOCAL_TZ, LOCAL_FULL_TIMESTAMP, LOCAL_EASY_TIMESTAMP, \
     parseServiceId, IsDebug
from sqlalchemy import func, asc, desc, and_, or_
from flask.ext.babel import gettext

ROLE_USER = 0
ROLE_ADMIN = 1

model_order_columns = ('title', 'document', 'option_update', 'option_cost', 'data', 'total',)
model_price_columns = ('locale', 'countryID', 'regionID', 'documentID', 'documentDate', 'priceTypeID', 'currency', 'total',)

empty_value = '...'

MAX_TITLE_WORD_LEN = 20

def out(x):
    return x.encode(default_print_encoding, 'ignore')

def cid(ob):
    return ob and ob.id is not None and str(ob.id) or empty_value

def cdate(date, fmt=LOCAL_FULL_TIMESTAMP):
    if date and date is not None:
        try:
            x = date.replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
        except:
            if IsDebug:
                print '>>> Invalid date: [%s]' % date
            raise
        return str(x.strftime(fmt))
    return empty_value

def tag(key, value, parameter=None, product=None):
    x = { 'key' : key }
    if parameter:
        m = re.search(r'(<parameter\s+.*id="%(key)s".*>(.*)</parameter>)' % x, value)
    elif product:
        m = re.search(r'(<product\s+.*id="%(key)s".*>(.*)</product>)' % x, value)
    else:
        m = re.search(r'(%(key)s>(.*)</%(key)s)' % x, value)
    return m and m.groups()

def clean(value):
    if not isinstance(value, unicode):
        value = value.decode(default_unicode, 'ignore')
    return value and re.sub(r'[\n\'\"\;\%\*]', '', value).strip() or ''

def worder(value, length=None):
    max_len = (not length or length < 0) and MAX_TITLE_WORD_LEN or \
        length
    words = value.split()
    s = ''
    changed = 0
    while len(words):
        word = words.pop(0).strip()
        if s:
            s += ' '
        if len(word) <= max_len:
            s += word
        else:
            s += word[:max_len]
            words.insert(0, word[max_len:])
            changed = 1
    return changed, s.strip()

##  ------------
##  Help Classes
##  ------------

class Pagination(object):
    #
    # Simple Pagination
    #
    def __init__(self, page, per_page, total, value, sql):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.value = value
        self.sql = sql

    @property
    def query(self):
        return self.sql

    @property
    def items(self):
        return self.value

    @property
    def current_page(self):
        return self.page

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def get_page_params(self):
        return (self.current_page, self.pages, self.per_page, self.has_prev, self.has_next, self.total,)

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        out = []
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    out.append(None)
                out.append(num)
                last = num
        return out

##  ==========================
##  Objects Class Construction
##  ==========================

class ExtClassMethods(object):
    """
        Abstract class methods
    """
    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print x

#   -------------------------------------------------------------- #
#       User.orders ->> Order    : Order.user -> User              #
#       Module.orders ->> Order  : Order.module -> Module          #
#       Module.items ->> Item    : Item.module -> Module           #
#       Parameter.items ->> Item : Item.parameter -> Parameter     #
#       Order.prices ->> Price   : Price.order -> Order            #
#   -------------------------------------------------------------- #

class User(db.Model, ExtClassMethods):
    """
        Пользователь
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    title = db.Column(db.Unicode(120))
    role = db.Column(db.SmallInteger, default=ROLE_USER)

    userID = db.Column(db.String(32), index=True, unique=True)
    userTypeID = db.Column(db.String(10))
    orderEmail = db.Column(db.String(120))

    orders = db.relationship('Order', backref=db.backref('user'), lazy='dynamic')

    def __init__(self, login, title=None, email=None):
        self.userID = login
        self.title = not title and '' or title
        self.email = not email and '' or email
        self.reg_date = datetime.utcnow()

    def __repr__(self):
        return '<User %s:%s%s>' % (cid(self), str(self.userID), self.title and ' '+out(self.title) or '')

class Module(db.Model, ExtClassMethods):
    """
        Модуль
    """
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    m1 = db.Column(db.Boolean(), default=True)
    m2 = db.Column(db.Boolean(), default=True)

    wizardID = db.Column(db.String(40), index=True, unique=True)
    wizardName = db.Column(db.Unicode(120))
    DUS = db.Column(db.String(12))

    orders = db.relationship('Order', backref=db.backref('module'), cascade="all, delete-orphan", lazy='dynamic')
    
    items = db.relationship('Item', backref=db.backref('module'), cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, wizard, title=None):
        self.wizardID = wizard
        self.wizardName = not title and '' or title
        self.reg_date = datetime.utcnow()

    def __repr__(self):
        return '<Module %s:%s%s>' % (cid(self), str(self.wizardID), self.wizardName and ' '+out(self.wizardName) or '')

    def get_dus_number(self):
        m = re.search(r'DUS-([\d-]+)', self.DUS or '')
        return m and m.group(1) or '' 

class Parameter(db.Model, ExtClassMethods):
    """
        Параметр
    """
    __tablename__ = 'parameters'

    id = db.Column(db.Integer, primary_key=True)
    CIS = db.Column(db.String(40), index=True, unique=True)
    ptype = db.Column(db.SmallInteger, default=0)
    unit = db.Column(db.String(3))

    items = db.relationship('Item', backref=db.backref('parameter'), cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, cis, typ, **kw):
        self.CIS = cis
        self.ptype = typ in valid_parameter_types and typ or valid_parameter_types[0]
        self.unit = kw.get('unit') or n_a

    def __repr__(self):
        return '<Parameter %s[%s]:%s %s>' % (cid(self), self.CIS, sorted(valid_parameter_names.keys())[self.ptype], self.unit)

class Item(db.Model, ExtClassMethods):
    """
        Параметр модуля
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)

    parameter_id = db.Column(db.Integer, db.ForeignKey('parameters.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))

    def __init__(self, parameter, module):
        self.parameter = parameter
        self.module = module

    def __repr__(self):
        return '<Item %s[%s]: %s>' % (cid(self), self.parameter.CIS, self.module.wizardID)

    @staticmethod
    def print_item_by_key(key):
        for p, i in db.session.query(Parameter, Item).join(Item) \
                .filter(Parameter.CIS.like(key+'%')) \
                .order_by(Parameter.CIS) \
                .all():
            print '%s:%s' % (p.CIS, i.module.wizardID)

class Order(db.Model, ExtClassMethods):
    """
        Комплектация (заказ) пользователя
    """
    __tablename__ = 'orders'
    
    _max_title_len = 1200

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))

    code = db.Column(db.String(10), index=True)
    document = db.Column(db.String(40), index=True, default='')
    otype = db.Column(db.SmallInteger, default=0)
    title = db.Column(db.Unicode(_max_title_len))
    total = db.Column(db.Integer, index=True, nullable=False, default=0)
    data = db.Column(db.Text)

    current_price = db.Column(db.String(20), default='')
    rating = db.Column(db.Enum(*default_rating_types))

    option_update = db.Column(db.Boolean(), default=False)
    option_cost = db.Column(db.Boolean(), default=False)

    prices = db.relationship('Price', backref=db.backref('order', lazy='joined'), cascade="all, delete, delete-orphan", lazy='dynamic')

    def __init__(self, user, module, otype, columns=None):
        self.user = user
        self.module = module
        self.otype = otype in valid_order_types and otype or ORDER_STANDARD
        self.rating = RATING_UNDEFINED
        self.set_attrs(columns)
        #if otype == ORDER_STANDARD:
        self.code = Order.generate_custom_code(user, module, otype)
        self.reg_date = datetime.utcnow()

    def __repr__(self):
        return '<Order %s[%s]:%s %s %s%s>' % (cid(self), str(self.user.userID), self.otype, str(self.code), str(self.module.wizardID), 
            self.title and ' '+out(self.title) or '')

    def _data(self, value=None, coding=None):
        if value is None:
            value = self.data 
        if not coding or coding == 'decode':
            # utf8 -> unicode
            if not isinstance(value, unicode):
                value = value.decode(default_unicode, 'ignore')
        else:
            # unicode -> utf8
            if isinstance(value, unicode):
                value = value.encode(default_unicode, 'ignore')
        return value

    def set_attrs(self, columns=None):
        changed = False
        if columns:
            for key in model_order_columns:
                value = columns.get(key)
                if key.startswith('option'):
                    value = value and True or False
                elif key == 'data':
                    value = self._data(value or '')
                elif key == 'total':
                    value = self.get_total(value, columns.get('currency'))
                elif key == 'title':
                    value = self.get_title(value)
                elif key == 'document' and not value:
                    value = ''
                setattr(self, key, value)
                changed = True
        if changed:
            self.reg_date = datetime.utcnow()

    @staticmethod
    def get_total(value, currency):
        default_rate = 1.0
        if value:
            if currency not in default_currency_names:
                currency = DEFAULT_CURRENCY
            rate = CURRENCY_RATES[currency] or default_rate
        else:
            value = 0
            rate = default_rate
        return int(float(value) * rate * 100)

    @staticmethod
    def get_title(value):
        changed, value = worder(value)
        try:
            if len(value) > Order._max_title_len:
                value = value[:Order._max_title_len]
        except:
            value = gettext('Error: Order value is too long or has invalid data type!')
        return value

    @staticmethod
    def generate_current_price(price, currency=DEFAULT_CURRENCY):
        x = str(price)
        return '%s.%s %s' % (x[0:-2], x[-2:], currency in default_currency_names and currency or DEFAULT_CURRENCY)

    @staticmethod
    def generate_custom_code(user, module, otype=ORDER_CUSTOM):
        if user and module:
            query = db.session.query(Order.code).filter_by(user=user, module=module)
            if otype in valid_order_types:
                query = query.filter_by(otype=otype).order_by(desc(Order.code))
            else:
                query = query.filter(Order.code != '').order_by(desc(Order.code))
                otype = ORDER_CUSTOM
            codes = query.first()

            code = codes and len(codes) and codes[0] or 0
            dus = module.get_dus_number()
            dus = len(dus) > 2 and dus[0:3] or '000'
            index = code and (int(code[6:]) + 1) or 1
            code = '%s-%s-%04d' % ('SCO'[otype], dus, index)
        else:
            if otype is None:
                otype = ORDER_CUSTOM
            code = '%s-000-%04d' % ('SCO'[otype], 1)
        return code

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print '%s: Data:%s CurrentPrice:[%s] Rating:%s' % (x, x.data and len(x.data) or 0, str(x.current_price), str(x.rating))

    @classmethod
    def print_price(cls):
        for x in db.session.query(Order).order_by(desc(Order.total)).all():
            print '%05d: Data:%s Total:[%s] CurrentPrice:[%s] Rating:%s' % ( \
                x.id, x.data and len(x.data) or 0, str(x.total), str(x.current_price), str(x.rating)
            )

    @staticmethod
    def on_changed_title(target, value, oldvalue, initiator):
        pass

    @staticmethod
    def on_changed_price(target, value, oldvalue, initiator):
        try:
            price, currency = value.split()
        except:
            price = value
            currency = None
        target.total = Order.get_total(price, currency)

db.event.listen(Order.title, 'set', Order.on_changed_title)
db.event.listen(Order.current_price, 'set', Order.on_changed_price)

class Price(db.Model, ExtClassMethods):
    """
        Стоимость комплектации
    """
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id')) #, ondelete='CASCADE'

    locale = db.Column(db.Enum(*default_language_types))
    countryID = db.Column(db.Enum(*default_country_types))
    #regionID = db.Column(db.Enum(*default_region_types))
    regionID = db.Column(db.String(9))
    #region = db.Column(db.String(9))
    documentID = db.Column(db.String(20))
    documentDate = db.Column(db.String(20))
    priceTypeID = db.Column(db.String(9))
    currency = db.Column(db.Enum(*default_currency_names))
    total = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, order, columns=None):
        self.order = order
        self.currency = DEFAULT_CURRENCY
        if columns:
            for key in model_price_columns:
                value = columns.get(key)
                if key == 'total':
                    value = int(float(value) * 100)
                elif key in ('regionID', 'priceTypeID',):
                    value = parseServiceId(value)
                elif key == 'countryID':
                    value = value in default_country_types and value or value == n_a and DEFAULT_COUNTRY or value
                setattr(self, key, value)
        self.reg_date = datetime.utcnow()

    def __repr__(self):
        return '<Price %s:%s %s %s>' % (cid(self), cdate(self.reg_date), self.total, self.currency)

    def get_price(self):
        return '%.2f %s' % (self.total/100.0, self.currency)

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print '%s: %s %s' % (x, str(x.order.code), x.get_price())

##  =======================
##  Public custom functions
##  =======================

def print_all():
    print 'Users:'
    User.print_all()
    print 'Modules:'
    Module.print_all()
    print 'Parameters:'
    Parameter.print_all()
    print 'Items:'
    Item.print_all()
    print 'Orders:'
    Order.print_all()
    print 'Prices:'
    Price.print_all()

def log(mode=1, n=1, size=None, **kw):
    user = kw.get('user')
    module = kw.get('module')
    otype = kw.get('otype')
    context = clean(kw.get('context') or '')
    sort = kw.get('sort')

    per_page = size or 10

    if mode == 1:
        query = db.session.query( \
            Order.id, 
            Order.reg_date, 
            Order.otype, 
            Order.code, 
            Order.document, 
            Order.title, 
            Order.current_price,
            Order.rating,
            Order.option_update,
            Order.option_cost
        )
    else:
        query = Order.query
        
    if user:
        query = query.filter_by(user=user)
    if module:
        query = query.filter_by(module=module)
    if otype in valid_order_types:
        query = query.filter_by(otype=otype)
    if context:
        c = '%' + context + '%'
        
        keys = ('code', 'document', 'title', 'data',)
        conditions = []

        for key in keys:
            conditions.append(getattr(Order, key).ilike(c))
        query = query.filter(or_(*conditions))

    if sort:
        if sort == 'ID':
            query = query.order_by(desc(Order.id))
        elif sort == 'TOTAL-DESC':
            query = query.order_by(desc(Order.total))
        elif sort == 'TOTAL-ASC':
            query = query.order_by(asc(Order.total))
        elif sort == 'DATE-DESC':
            query = query.order_by(desc(Order.reg_date))
        elif sort == 'DATE-ASC':
            query = query.order_by(asc(Order.reg_date))
        elif sort == 'CUSTOM-CODE-DESC':
            query = query.order_by(desc(Order.code))
        elif sort == 'CUSTOM-CODE-ASC':
            query = query.order_by(asc(Order.code))
        else:
            query = query.order_by(Order.id)
    else:
        query = query.order_by(desc(Order.reg_date))

    if not (user and module) and kw.get('check'):
        if mode == 1:
            return Pagination(n, per_page, 0, [], query)
        else:
            return None
    elif mode == 1:
        total = query.count()
        offset = per_page*(n-1)
        if offset > 0:
            query = query.offset(offset)
        query = query.limit(per_page)
        items = query.all()
        return Pagination(n, per_page, total, items, query)
    else:
        return query.paginate(n, per_page=per_page, error_out=False)

def get_log_headers():
    return [ \
        ('id', 'reg_date', 'otype', 'code', 'document', 'title', 'current_price', 'rating', 'option_update', 'option_cost'), 
        (
            {
                'id'      : 'row',
                'name'    : gettext('#'), 
                'title'   : gettext('Number'),
                'value'   : '%(num)s',
                'visible' : 1,
            },
            {
                'id'      : 'reg_date',
                'name'    : gettext('Date'), 
                'title'   : gettext('Order date'),
                'value'   : '<div><span class="date">%(cdate)s</span></div>',
                'visible' : 1,
            },
            {
                'id'      : 'otype',
                'name'    : gettext('Type'),
                'title'   : gettext('Type of order'),
                'value'   : '<div><span class="otype %(updatable)s">%(otype)s</span></div>',
                'visible' : 1,
            },
            {
                'id'      : 'code',
                'name'    : '', 
                'title'   : gettext('Order code'),
                'visible' : 0,
            },
            {
                'id'      : 'document',
                'name'    : '', 
                'title'   : gettext('Order document'),
                'visible' : 0,
            },
            {
                'id'      : 'title',
                'name'    : gettext('Complete name'), 
                'title'   : '',
                'value'   : '<div><span class="code">%(code)s</span><p class="title">%(title)s</p></div>',
                'visible' : 1,
            },
            {
                'id'      : 'current_price',
                'name'    : gettext('Price'),
                'title'   : gettext('Price information'),
                'value'   : '<div><span class="price">%(price)s</span><br><span class="currency">%(currency)s</span></div>',
                'visible' : 1,
            },
            {
                'id'      : 'rating',
                'name'    : '',
                'title'   : gettext('Rating'),
                'visible' : 0,
            },
            {
                'id'      : 'show',
                'name'    : '',
                'title'   : gettext('Rating'),
                'value'   : '<div><img class="rating" src="%(root)s/static/images/%(image)s" alt="%(rating)s" title="%(show_title)s"></div>',
                'visible' : 1,
            },
        ),
        {
            'sort' : {'id':'sort_icon', 'src':'/static/images/sort.png', 'alt':'', 'title':gettext('Sort by')},
        }
    ]

def statistics(mode=1, **kw):
    order = kw.get('order')
    sort = kw.get('sort')

    if mode == 1:
        query = db.session.query(Price)
    else:
        query = Price.query
        
    if order:
        query = query.filter_by(order=order)

    if sort:
        if sort == 'ID':
            query = query.order_by(desc(Price.id))
        elif sort == 'TOTAL-DESC':
            query = query.order_by(desc(Price.total))
        elif sort == 'TOTAL-ASC':
            query = query.order_by(asc(Price.total))
        elif sort == 'DATE-DESC':
            query = query.order_by(desc(Price.reg_date))
        elif sort == 'DATE-ASC':
            query = query.order_by(asc(Price.reg_date))
        else:
            query = query.order_by(Price.id)
    else:
        query = query.order_by(desc(Price.reg_date))

    total = query.count()
    items = [ \
        (
            ob.id,
            ob.reg_date, 
            ob.documentID,
            ob.documentDate,
            ob.priceTypeID,
            ob.currency,
            ob.total,
            ob.get_price(), 
        )
        for ob in query.all()]

    return (total, order and order.id, items, query)

def get_statistics_headers():
    return [ \
        ('id', 'reg_date', 'documentID', 'documentData', 'priceTypeID', 'currency', 'total', 'price'), 
        (
            {
                'id'      : 'row',
                'name'    : gettext('#'), 
                'title'   : gettext('Number'),
                'value'   : '%(num)s',
                'visible' : 1,
            },
            {
                'id'      : 'reg_date',
                'name'    : gettext('Date'),
                'title'   : gettext('Date'),
                'value'   : '<div><span class="date">%(cdate)s</span></div>',
                'visible' : 1,
            },
            {
                'id'      : 'currency',
                'name'    : '',
                'title'   : gettext('Currency'),
                'visible' : 0,
            },
            {
                'id'      : 'total',
                'name'    : '',
                'title'   : gettext('Total'),
                'visible' : 0,
            },
            {
                'id'      : 'price',
                'name'    : gettext('Price'),
                'title'   : gettext('Price'),
                'value'   : '<div><span class="price">%(price)s</span></div>',
                'visible' : 1,
            },
        ),
        {
            'sort' : {'id':'sort_icon', 'src':'/static/images/sort.png', 'alt':'', 'title':gettext('Sort by')},
        }
    ]

def get_log(mode, n=1, size=None, **kw):
    return [(x.id, x.reg_date, x.otype, x.code, x.title, x.current_price, x.rating,) for x in log(mode, n, size, **kw).items]

def print_log(mode, n=1, size=None, **kw):
    page = log(mode, n, size, **kw)
    print 'Total:%s Page:%s[%s] Per_page:%s Next:%s Prev:%s' % ( \
        page.total, page.page, page.pages, page.per_page, page.has_next, page.has_prev,
    )
    for ob in page.items:
        print ob

def custom_orders(user_id=None, not_user_id=None, otype=None):
    query = db.session.query(Order)
    if user_id:
        query = query.filter(Order.user_id==user_id)
    if not_user_id:
        query = query.filter(Order.user_id!=not_user_id)
    if otype:
        query = query.filter(Order.otype==otype)
    return query.order_by(desc(Order.reg_date)).all()

def price_region_test(regionID=None):
    columns = {
        'locale':'rus', 
        'countryID':'RU', 
        'regionID':regionID or 'CB0000013', 
        'documentID':'', 
        'documentDate':'', 
        'priceTypeID':'000000014', 
        'currency':'RUR', 
        'total':100,
    }
    order = Order.get_by_id(1)
    price = Price(order, columns)
    error = None
    try:
        db.session.commit()
    except Exception, error:
        db.session.rollback()
    return price.id, error and str(error) or 'OK'