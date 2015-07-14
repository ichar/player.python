# -*- coding: utf-8 -*-

import re
from datetime import datetime

from app import db
from flask.ext.babel import gettext
from flask import current_app

from config import COMMUNICATIONS, LANGUAGES, CURRENCIES, IsDebug, IsDeepDebug, IsDBCheck, default_encoding, default_unicode, \
     ORDER_STANDARD, ORDER_CUSTOM, ORDER_DONE, \
     RATING_UNDEFINED, RATING_UP, RATING_EQUAL, RATING_DOWN, \
     DEFAULT_LOG_MODE, DEFAULT_PER_PAGE, \
     LOCAL_EASY_TIMESTAMP, \
     getReference, print_to, print_action, valid_action_types, valid_parameter_names, valid_order_types, \
     valid_order_names, errorlog, n_a
from exchange import getDOMItemValue, getDOMErrors, getDOMParameters
from models import User, Module, Parameter, Item, Order, Price, model_order_columns, model_price_columns, \
     cdate, get_log_headers, log, get_statistics_headers, statistics

BASE_URL = BASE_PATH = REFERENCE_PATH = HELPER_URL = ''

RESTRITED_ATTRS = ('document',)

IsError = False

def print_db_state():
    app = current_app._get_current_object()
    if IsDeepDebug:
        print ''
        print '$$$ DB: %s' % app.config['SQLALCHEMY_DATABASE_URI']

def _add(ob):
    if IsDebug:
        print '>>> Add %s' % ob
    db.session.add(ob)

def _delete(ob):
    if IsDebug:
        print '>>> Delete %s' % ob
    db.session.delete(ob)

def _commit(check_session=True):
    if IsError:
        if IsDebug:
            print '>>> Error'
        return
    if check_session:
        if not (db.session.new or db.session.dirty or db.session.deleted):
            if IsDebug:
                print '>>> No data to commit: new[%s], dirty[%s], deleted[%s]' % ( \
                    len(db.session.new), len(db.session.dirty), len(db.session.deleted))
            return
    try:
        db.session.commit()
    except Exception, error:
        db.session.rollback()
        if IsDebug:
            print '>>> Commit Error: %s' % error
        print_to(errorlog, str(error))
    if IsDebug:
        print '>>> OK'

def get_item(dom, attrs, id):
    return attrs.get(id) or id not in RESTRITED_ATTRS and getDOMItemValue(dom, id)

def get_columns(dom, attrs, model_columns):
    columns = {}
    for key in model_columns:
        columns[key] = get_item(dom, attrs, key)
    return columns

def get_order(id=None, code=None, **kw):
    order = None
    if id:
        order = Order.get_by_id(id)
    elif code:
        user = kw.get('user')
        module = kw.get('module')
        if user and module:
            order = Order.query.filter_by(user=user, module=module, code=code).first()
    return order    

def register(action, dom, attrs):
    """
        Register XML-response in DB. Get items form DOM and clear XML. 
        Valid actions: 203|204|205|207.

        Arguments:
            dom     - DOM object
            attrs   - Dictionary (requested items: action, data (XML), selected_item, custom_code and another...)

        Returns:
            data    - Dictionary (next_custom_code)
    """
    print_db_state()

    IsError = False

    print_action(action, 'DBase.Register')

    # ----
    # User
    # ----
    userID = get_item(dom, attrs, 'userID')
    user = userID and User.query.filter_by(userID=userID).first()
    if not user:
        user = User(userID, title=get_item(dom, attrs, 'userName'), email=getDOMItemValue(dom, 'orderEmail'))
        _add(user)

    # ------
    # Module
    # ------
    wizardID = get_item(dom, attrs, 'wizardID')
    module = wizardID and Module.query.filter_by(wizardID=wizardID).first()
    if not module:
        module = Module(wizardID, title=re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', get_item(dom, attrs, 'wizardName'))))
        m = re.search(r'.*(DUS-[\d-]*)', module.wizardName)
        if m:
            module.DUS = m.group(1)
        _add(module)

    # ------------------
    # Parameters & Items
    # ------------------
    for n, x in enumerate(getDOMParameters(dom, False)):
        parameter = Parameter.query.filter_by(CIS=x['id']).first()
        if not parameter:
            parameter = Parameter(x['id'], valid_parameter_names.get(x['type'].upper()), unit=x['unit'])
            _add(parameter)

        item = Item.query.filter_by(parameter=parameter, module=module).first()
        if not item:
            item = Item(parameter, module)
            _add(item)

    # ---------------------
    # Order & Prices & Data
    # ---------------------
    if action not in valid_action_types:
        IsError = True
        otype = -1

    id = get_item(dom, attrs, 'selected_item')
    code = get_item(dom, attrs, 'custom_code')

    IsAddOrder = False
    IsUpdateOrder = False
    custom_code = ''
    order = None

    if IsError:
        pass

    # ----------------------------------------------
    # Get Order item from DB and update or add a new
    # ----------------------------------------------
    elif action == '203':
        if not id:
            otype = ORDER_STANDARD
            order = Order.query.filter_by(user=user, module=module, otype=otype).first()
        else:
            order = get_order(id, None)
            custom_code = order and order.code
            otype = -1
    elif action == '204':
        otype = ORDER_CUSTOM
        order = get_order(id, code, user=user, module=module)
    elif action == '205':
        otype = ORDER_CUSTOM
        #order = get_order(None, code, user=user, module=module)
    elif action == '207':
        otype = ORDER_DONE
    else:
        otype = -1

    if IsDebug:
        print '>>> Order: %s %s %s' % (order, str(code), str(id))

    if otype in valid_order_types:
        price_columns = get_columns(dom, attrs, model_price_columns)

        if not attrs.get('title'):
            attrs['title'] = gettext(valid_order_names[otype])

        if not order:
            order = Order(user, module, otype, get_columns(dom, attrs, model_order_columns))

            #if otype == ORDER_DONE:
            #    order.code = Order.generate_custom_code(user, module, otype=ORDER_DONE)
            #elif otype == ORDER_CUSTOM:
            #    order.code = get_item(dom, attrs, 'custom_code') or \
            #        Order.generate_custom_code(user, module, otype=otype)

            IsAddOrder = True
        else:
            if action in ('203','207'):
                pass
            elif action == '204':
                if order.option_update:
                    order.data = order._data(get_item(dom, attrs, 'data'))
                    IsUpdateOrder = True
            elif action == '205':
                order.set_attrs(get_columns(dom, attrs, model_order_columns))
                IsUpdateOrder = True

        current_price = Order.generate_current_price(int(float(price_columns['total']) * 100), \
            price_columns['currency'])

        if IsAddOrder:
            last_price = ''
            order.current_price = current_price
        else:
            last_price = order.current_price
            if order.otype in (ORDER_STANDARD, ORDER_CUSTOM,):
                order.current_price = current_price
                order.rating = order.current_price < last_price and RATING_DOWN or \
                               order.current_price > last_price and RATING_UP or \
                               RATING_EQUAL
            else:
                order.rating = current_price > last_price and RATING_DOWN or \
                               current_price < last_price and RATING_UP or \
                               RATING_EQUAL

        if IsDebug:
            print '>>> Current price: %s %s %s' % (last_price, order.current_price, order.rating)

        if order and IsAddOrder:
            _add(order)

        if order and (IsAddOrder or (order.option_cost and last_price != current_price)):
            _add(Price(order, price_columns))

    # ----------
    # Save to DB
    # ----------
    _commit(IsUpdateOrder and True or False)

    # ---------------------
    # Get data for response
    # ---------------------
    data = {}
    next_custom_code = Order.generate_custom_code(user, module)

    if action in ('203','204','205',):
        if order:
            data['title'] = order.title
            data['custom_code'] = order.code or custom_code
            data['next_custom_code'] = order.option_update and order.code or next_custom_code
            data['option_update'] = order.option_update
            data['option_cost'] = order.option_cost
        else:
            data['next_custom_code'] = next_custom_code
            data['custom_code'] = custom_code

    return data

def getLogVisibleHeaders():
    return [x for x in get_log_headers()[1] if x.get('visible')]

def getLogImages():
    return get_log_headers()[2]

def getLogTotal(attrs, force=None):
    """
        Get Log rows count filtered by optional user, module, order type.

        Arguments:
            attrs   - attributes (userID, wizardID, otype)

        Filter by (attrs):
            userID  - user ID
            wizardID- wizard ID
            otype   - order type (Config.valid_order_types)

        Returns:
            total   - page items count
    """
    print_db_state()

    userID = attrs.get('userID', None)
    user = userID and User.query.filter_by(userID=userID).first()

    if IsDebug and userID:
        print '>>> User[%s]: %s' % (userID, user and user.userID == userID and 'OK' or 'invalid!')

    wizardID = attrs.get('wizardID', None)
    module = wizardID and Module.query.filter_by(wizardID=wizardID).first()

    if IsDebug and wizardID:
        print '>>> Module[%s]: %s' % (wizardID, module and module.wizardID == wizardID and 'OK' or 'invalid!')

    otype = int(attrs.get('otype', 0))

    if IsDebug and otype in valid_order_types:
        print '>>> Order type[%s]: %s' % (otype, valid_order_names[otype])

    query = Order.query

    if user:
        query = query.filter_by(user=user)
    if module:
        query = query.filter_by(module=module)
    if otype:
        query = query.filter_by(otype=otype)

    if user and module or force:
        total = query.count()
    else:
        total = 0

    print_action(total, 'DBase.getLogTotal')

    return total

def getLogPage(action, request, session):
    """
        Get Log page from DB by selected number filtered by requested userID and wizardID.

        Arguments:
            action  - 301
            request - form (page, per_page, userID, wizardID)
            session - current session

        Filter by (attrs):
            userID  - user ID
            wizardID- wizard ID
            otype   - order type (Config.valid_order_types)
            context - search context

        Returns:
            exchange_error, exchange_message - exchange error info
            data    - Pagination object from DB models
            items   - page column items
    """
    print_db_state()

    form = request.form

    print_action(action, 'DBase.GetLogPage')

    exchange_message = ''
    exchange_error = 0
    data = None

    page = int(form.get('page', 0)) or 1
    per_page = int(form.get('per_page', 0)) or DEFAULT_PER_PAGE

    sort = form.get('sort') or ''

    userID = form.get('userID', None)
    user = userID and User.query.filter_by(userID=userID).first()

    if IsDebug and userID:
        print '>>> User[%s]: %s' % (userID, user and user.userID == userID and 'OK' or 'invalid!')

    wizardID = form.get('wizardID', None)
    module = wizardID and Module.query.filter_by(wizardID=wizardID).first()

    if IsDebug and wizardID:
        print '>>> Module[%s]: %s' % (wizardID, module and module.wizardID == wizardID and 'OK' or 'invalid!')

    otype = int(form.get('otype', -1))

    if IsDebug and otype in valid_order_types:
        print '>>> Order type[%s]: %s' % (otype, valid_order_names[otype])

    context = form.get('search_context', None)

    if IsDebug and context:
        print '>>> Search context: [%s]' % context

    data = log(DEFAULT_LOG_MODE, page, per_page, user=user, module=module, otype=otype, context=context, check=IsDBCheck, sort=sort)

    items = []
    headers = get_log_headers()
    line_in_page = 0 #(page-1) * per_page

    for row in data.items:
        x = dict(zip(headers[0], row))
        line_in_page += 1

        s = x['document'] or ''
        if s and s.startswith('#'):
            x['document'] = s[1:].strip()

        x['root'] = '%s' % request.script_root
        x['image'] = '%s-16.png' % ( \
            x['rating'] == RATING_UP and 'up' or x['rating'] == RATING_DOWN and 'down' or 
            x['rating'] == RATING_EQUAL and 'equal' or 'undef')
        x['num'] = line_in_page
        x['cdate'] = cdate(x['reg_date'], fmt=LOCAL_EASY_TIMESTAMP)
        x['price'], x['currency'] = x['current_price'].split()
        x['code'] = x['otype'] == ORDER_DONE and x['document'] or x['code']
        x['updatable'] = x['option_update'] and 'updatable' or x['option_cost'] and 'cost' or 'fixed'

        for n, column in enumerate(headers[1]):
            x['%s_title' % column['id']] = column['title']

        items.append([x['id'], [ column.has_key('value') and (column['value'] % x) or x[column['id']]
            for n, column in enumerate(headers[1])
                if column.get('visible') ]
        ])

    return (exchange_error, exchange_message, data, items)

def getLogItem(action, request, session):
    """
        Get Log item from DB by selected log item's ID.

        Arguments:
            action  - 302|303|304|307
            request - form (selected_item)
            session - current session

        Returns:
            exchange_error, exchange_message - exchange error info
            id      - parsed ID of selected_item
            data    - XML (Order.data)
    """
    form = request.form

    print_action(action, 'DBase.GetLogItem')

    exchange_message = ''
    exchange_error = 0
    order = None

    id = form.get('selected_item', None)

    if IsDebug:
        print '>>> Selected LogItem ID: [%s]' % id

    if id:
        order = Order.get_by_id(id)
    else:
        exchange_message = '%s: <id>' % gettext('Missing argument')
        exchange_error = -10

    return (exchange_error, exchange_message, id, order)

def getStatisticsVisibleHeaders():
    return [x for x in get_statistics_headers()[1] if x.get('visible')]

def getStatictics(action, request, session):
    """
        Get Price items from DB by selected log item's ID.

        Arguments:
            action  - 305
            request - form (selected_item)
            session - current session

        Returns:
            exchange_error, exchange_message - exchange error info
            id      - parsed ID of selected_item
            data    - XML (Order.data)
    """
    form = request.form

    print_action(action, 'DBase.GetLogStatistics')

    exchange_message = ''
    exchange_error = 0
    response = None
    order = None

    id = form.get('selected_item', None)

    if IsDebug:
        print '>>> Selected LogItem ID: [%s]' % id

    if id:
        order = Order.get_by_id(id)
    else:
        exchange_message = '%s: <id>' % gettext('Missing argument')
        exchange_error = -10

    total, order_id, data, query = statistics(DEFAULT_LOG_MODE, order=order)

    items = []
    headers = get_statistics_headers()
    line_in_page = 0

    for row in data:
        x = dict(zip(headers[0], row))
        line_in_page += 1

        x['root'] = '%s' % request.script_root
        x['num'] = line_in_page
        x['cdate'] = cdate(x['reg_date'], fmt=LOCAL_EASY_TIMESTAMP)

        for n, column in enumerate(headers[1]):
            x['%s_title' % column['id']] = column['title']

        items.append([x['id'], [ column.has_key('value') and (column['value'] % x) or x[column['id']]
            for n, column in enumerate(headers[1])
                if column.get('visible') ]
        ])

    return (exchange_error, exchange_message, id, total, items)

def removeLogItem(action, request, session):
    """
        Remove Log item from DB by selected log item's ID.

        Arguments:
            action  - 308
            request - form (selected_item)
            session - current session

        Returns:
            exchange_error, exchange_message - exchange error info
    """
    form = request.form

    print_action(action, 'DBase.RemoveLogItem')

    exchange_message = ''
    exchange_error = 0

    IsDone = False

    id = form.get('selected_item', None)

    if id:
        order =get_order(id)
        if order and order.otype not in (ORDER_STANDARD, ORDER_DONE):
            _delete(order)
            _commit(True)

            IsDone = True
    else:
        exchange_message = 'Error %s: <%s>' % (gettext('Missing argument'), id)
        exchange_error = -10

    if IsDebug:
        if IsDone and not exchange_error:
            print '>>> Removed LogItem ID: [%s]' % id
        elif exchange_error:
            print '>>> [%s] %s' % (exchange_error, exchange_message)
        else:
            print '>>> [%s] %s' % (id, gettext('Cannot be removed'))

    return getLogPage(action, request, session)
