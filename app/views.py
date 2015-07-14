# -*- coding: utf-8 -*-

import re
import datetime
import random

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, make_response
from flask.ext.babel import gettext

from app import app, db, babel
from config import COMMUNICATIONS, LANGUAGES, CURRENCIES, IsDebug, IsDeepDebug, default_communication, valid_action_types, n_a, \
     getCountryID, getRegionID, getUserID, \
     parseServiceId, getRegion, getCountry, getClient, isAuthorized, setReference, errorlog, demo, \
     print_exception, print_action, print_to, \
     UTC_EASY_TIMESTAMP
from wizard import set_platform, getPage, IsMobile, IsAndroid, IsiOS, IsiPad, IsIE, IsMSIE, IsSeaMonkey, \
     IsChrome, IsFirefox, IsSafari, IsOpera
from exchange import data_encode, send, receive, getURLInfo, getXml, getDOMItemValue, getDOMErrors, \
     cleanHtml, getRequestXML
from dbase import register, getLogVisibleHeaders, getLogImages, getLogTotal, getLogPage, getLogItem, \
     getStatisticsVisibleHeaders, getStatictics, removeLogItem
from version import get_version

##

def getTime():
    return datetime.datetime.now().strftime(UTC_EASY_TIMESTAMP)

def _validate(key, value):
    if key == 'locale':
        return value and value in LANGUAGES and value or 'rus'
    return value

@babel.localeselector
def get_locale():
    key = _validate('locale', request.args.get('locale'))
    return LANGUAGES.has_key(key) and LANGUAGES.get(key)[0] or DEFAUL_LANGUAGE

def before(f):
    def wrapper(mode, **kw):
        set_platform(agent=request.user_agent)
        if not (request and request.user_agent) or IsMSIE():
            return make_response(render_template('noie.html'))
        return f(mode, **kw)
    return wrapper

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def _ext():
    document = request.form.get('documentID') or ''
    country = request.form.get('countryID') or ''
    region = request.form.get('regionID') or ''
    if region:
        region = parseServiceId(region)
    user = request.form.get('userName')
    return index_with_logger(COMMUNICATIONS['external'], document, region, country, user)

@app.route('/index.html', methods = ['GET'])
def _int():
    return index_with_logger(COMMUNICATIONS['internal'])

def index_with_logger(mode, document=None, region=None, country=None, user=None):
    try:
        return index(mode, document=document, region=region, country=country, user=user)
    except:
        print_exception()
        raise

def _make_platform(wizard, locale, user, debug=None):
    agent = request.user_agent
    browser = agent.browser
    os = agent.platform
    root = '%s/' % request.script_root

    referer = request.form.get('helperHttpReferer') or request.form.get('refererURI') or request.form.get('helperURI') or ''
    close = request.form.get('closeURI') or request.form.get('refererURI') or request.form.get('helperURI') or ''

    links = {
        'calculate' : '/?wizard=%s&locale=%s' % (wizard, locale),
        'cancel' : '/?wizard=%s&locale=%s' % (wizard, locale),
        'referer' : referer,
        'close' : close,
    }

    if IsIE():
        version = agent.version.split('.')[0]
        if version < '6':
            version = '6'
    elif IsSeaMonkey():
        version = ''
    else:
        version = agent.version

    authorized = isAuthorized(user)
    css = '%s' % ( \
        IsMobile() and (IsChrome() and '.android.' or '.mobile.') or 
        IsIE(10) and '.ie10.' or 
        IsOpera() and '.opera.' or 
        IsFirefox() and '.firefox.' or 
        '.'
    )

    is_default = 1 or os in ('ipad', 'android',) and browser in ('safari', 'chrome',) and 1 or 0 
    is_frame = not IsMobile() and 1 or 0

    platform = '[os:%s, browser:%s (%s), css:%s, %s %s%s%s%s]' % ( \
        os, 
        browser, 
        version, 
        css, 
        locale, 
        authorized and ' authorized' or '', 
        is_default and ' default' or ' flex',
        is_frame and ' frame' or '', 
        debug and ' debug' or '',
    )

    kw = { \
        'agent'          : agent.string,
        'browser'        : browser, 
        'os'             : os, 
        'root'           : root, 
        'referer'        : referer, 
        'links'          : links, 
        'version'        : version, 
        'authorized'     : authorized, 
        'css'            : css, 
        'is_frame'       : is_frame, 
        'platform'       : platform,
        'style'          : { 'default' : is_default },
        'screen'         : request.form.get('screen') or '',
        'scale'          : request.form.get('scale') or '',
    }

    return kw

def _make_keywords():
    return ( \
        # --------------
        # Error Messages
        # --------------
        "'Execution error':'%s'" % gettext('Execution error'),
        "'Missing parameters':'%s'" % gettext('Any parameters should be selected before the culculating.'),
        "'Session is expired':'%s'" % ( \
            gettext('Session is expired notification')+
            '<br>'+
            gettext('You will be redirected to the passage of the authorization procedure.')
        ),
        "'System is not available':'%s'" % ( \
            gettext('System is not available now.')+
            '<br>'+
            gettext('You will be redirected to the passage of the authorization procedure.')+
            '<br><br>'+
            gettext('We apologize for any inconvenience.')
        ),
        # -------
        # Buttons
        # -------
        "'Calculate':'%s'" % gettext('Calculate'),
        "'Cancel':'%s'" % gettext('Cancel'),
        "'Confirm':'%s'" % gettext('Confirm'),
        "'Reject':'%s'" % gettext('Decline'),
        "'OK':'%s'" % gettext('OK'),
        # ----
        # Help
        # ----
        "'All':'%s'" % gettext('All'),
        "'Base article':'%s'" % gettext('Base article'),
        "'Calculating autoupdate':'%s'" % gettext('Automatically update the calculations'),
        "'Calculate the cost':'%s'" % gettext('Calculate the cost'),
        "'Calculator':'%s'" % gettext('Calculator'),
        "'Cancel search':'%s'" % gettext('Cancel search'),
        "'Caption':'%s'" % gettext('Caption'),
        "'Close':'%s'" % gettext('Close'),
        "'Close page':'%s'" % gettext('Close page'),
        "'Code':'%s'" % gettext('Code'),
        "'Commands':'%s'" % gettext('Commands'),
        "'Complete name':'%s'" % gettext("Complete name"),
        "'Collapse form groups':'%s'" % gettext('Collapse form groups'),
        "'Custom':'%s'" % gettext('Custom'),
        "'Custom code':'%s'" % gettext('Custom code'),
        "'Data not found!':'%s'" % gettext('Data not found!'),
        "'Done':'%s'" % gettext('Done'),
        "'Go back':'%s'" % gettext('Go back'),
        "'Help':'%s'" % gettext('Help'),
        "'Help information':'%s'" % gettext('Help information'),
        "'Helper keypress guide':'%s'" % gettext('Helper keypress guide'),
        "'Expand form groups':'%s'" % gettext('Expand form groups'),
        "'Forward search':'%s'" % gettext('Forward search'),
        "'Full screen':'%s'" % gettext('Full screen'),
        "'Icon Toolbar':'%s'" % gettext('Icon Toolbar'),
        "'Load selected order':'%s'" % gettext('Load selected order'),
        "'Make an order':'%s'" % gettext('Make an order'),
        "'Monitor price changes':'%s'" % gettext('Monitor price changes'),
        "'No data...':'%s'" % gettext('No data...'),
        "'Open Calculate form':'%s'" % gettext('Open Calculate form'),
        "'Open Log page':'%s'" % gettext('Open Log page'),
        "'Open Order form':'%s'" % gettext('Open Order form'),
        "'Open Price statistics':'%s'" % gettext('Open Price statistics'),
        "'Open Save form':'%s'" % gettext('Open Save form'),
        "'Open Search panel':'%s'" % gettext('Open Search panel'),
        "'Options':'%s'" % gettext('Options'),
        "'Order confirmation form':'%s'" % gettext('Order confirmation form'),
        "'Order log':'%s'" % gettext('Order log'),
        "'Order type':'%s'" % gettext('Order type'),
        "'Price article':'%s'" % gettext('Price article'),
        "'Save confirmation form':'%s'" % gettext('Save confirmation form'),
        "'Search':'%s'" % gettext('Search'),
        "'Search context':'%s...'" % gettext('Search context'),
        "'Search Icon buttons':'%s'" % gettext('Search Icon buttons'),
        "'Standard':'%s'" % gettext('Standard'),
        "'System information':'%s'" % gettext('System information'),
        "'Total':'%s'" % gettext('Total'),
        # --------------------
        # Flags & Simple Items
        # --------------------
        "'error':'%s'" % gettext('error'),
        "'yes':'%s'" % gettext('Yes'),
        "'no':'%s'" % gettext('No'),
        "'n_a':'%s'" % n_a,
        "'true':'%s'" % 'true',
        "'false':'%s'" % 'false',
        # ------------------------
        # Miscellaneous Dictionary
        # ------------------------
        "'confirmation request':'%s'" % gettext("Type the following operation result:"),
        "'cost form':'%s'" % gettext('Cost notification form'),
        "'cost':'%s'" % gettext('The cost'),
        "'client':'%s'" % gettext('Client'),
        "'':'%s'" % gettext(''),
        "'estimated cost':'%s'" % gettext("The cost is estimated."),
        "'not calculated':'%s'" % gettext('not calculated'),
        "'not found':'%s'" % gettext('not found'),
        "'no client':'%s'" % gettext('unauthorized client'),
        "'order form':'%s'" % gettext('Order notification form'),
        "'order confirmation':'%s'" % gettext('Are you really going to create an order?'),
        "'ordered success':'%s'" % gettext('Successfully created.'),
        "'ordered fail':'%s'" % gettext("The order was not created by the error."),
        "'please confirm':'%s.'" % gettext('Please, confirm'),
        "'product version':'%s'" % gettext('Product Version'),
        "'save form':'%s'" % gettext('Save notification form'),
        "'save confirmation':'%s'" % gettext('Are you really going to save changes of the order?'),
        "'saved success':'%s'" % gettext('Successfully saved.'),
        "'saved fail':'%s'" % gettext("The order was not saved by the error."),
        "'shortcut version':'%s'" % get_version('shortcut'),
    )

def _make_exchange(mode, locale, country, region, user, document=None):
    return { \
        'communication' : request.form.get('helperCommunicationType', mode) or default_communication,
        'sessionID'     : data_encode(request.form.get('sessionID') or ''),
        'securityID'    : data_encode(request.form.get('securityID') or ''),
        'userID'        : getUserID(request.form.get('userID')),
        'userTypeID'    : request.form.get('userTypeID', ''),
        'userLogin'     : request.form.get('userLogin', ''),
        'userPswd'      : request.form.get('userPswd', ''),
        'httpHost'      : request.form.get('httpHost', ''),
        'webResource'   : request.form.get('webResource', ''),
        'documentID'    : document or n_a,
        'countryID'     : country or n_a,
        'regionID'      : region or n_a,
        'WebServiceURL' : request.form.get('WebServiceURL', ''),
        'currencyID'    : request.form.get('currencyID', ''),
        'priceTypeID'   : request.form.get('priceTypeID', ''),
        'countryName'   : request.form.get('countryName') or getCountry(country),
        'regionName'    : request.form.get('regionName') or getRegion(region),
        'clientName'    : getClient(user, locale),
    }

def _make_page(wizard, locale, init_only=False):
    if not wizard:
        flash('Note! The argument "wizard" should be presented.')
        page = None
    else:
        page = getPage(wizard, locale, agent=request.user_agent, init_only=init_only, keywords={ \
            'Yes'   : gettext('Yes'),
            'Count' : gettext('Count'),
            'Value' : '...',
        })
    return page

@before
def index(mode, **kw):
    host = request.form.get('host') or request.form.get('helperURI') or request.host_url
    debug = request.args.get('debug') == '1' and True or False
    demo(request.args.get('demo'), request=request)

    setReference(host, debug)

    wizard = request.args.get('wizard', 'BillGateDUS120') #'StreetGateDUS210'
    locale = _validate('locale', request.args.get('locale'))

    country = kw.get('country')
    region = kw.get('region')
    user = kw.get('user')
    document = kw.get('document')

    exchange = _make_exchange(mode, locale, country, region, user, document)

    page = _make_page(wizard, locale, init_only=False)

    kw = _make_platform(wizard, locale, user, debug)

    kw['extra'] = { \
        'selected_action' : request.form.get('selected_action') or 'null',
        'selected_item'   : request.form.get('selected_item') or 'null',
    }

    forms = ('index', 'log',)

    keywords = _make_keywords()

    session['communication'] = exchange['communication']
    session['session'] = exchange['sessionID']
    session['security'] = exchange['securityID']
    session['browser'] = kw['browser']
    session['locale'] = locale
    session['wizard'] = wizard
    session['name'] = page and page.get_title(False) or ''

    kw.update({ \
        'title'    : gettext('Helper Configurator Main Page'),
        'host'     : host,
        'wizard'   : wizard,
        'locale'   : locale, 
        'exchange' : exchange, 
        'keywords' : keywords, 
        'forms'    : forms, 
        'page'     : page,
    })

    if IsDebug:
        print '$$$'
        print '%s: %s %s %s %s session:[%s]' % (getTime(), host, wizard, locale, exchange['clientName'], exchange['sessionID'])
        print '%s: %s %s communication:[%s]' % (getTime(), kw['browser'], kw['agent'], exchange['communication'])
        print '%s: %s demo:%s' % (getTime(), kw['platform'], demo())

    return respond(template='index.html', debug=debug, **kw)

@app.route('/log', methods = ['GET', 'POST'])
def log_with_logger():
    if not request.referrer:
        return redirect(url_for('_ext', _method='GET', **request.args)) # values , _external=True

    try:
        return log(0)
    except:
        print_exception()
        raise

@before
def log(mode, **kw):
    host = request.form.get('host') or request.form.get('helperURI') or request.host_url
    debug = request.args.get('debug') == '1' and True or False
    demo(request.args.get('demo'), request=request)

    setReference(host, debug)

    mode = request.form.get('helperCommunicationType', session.get('communication'))
    wizard = request.args.get('wizard', request.form.get('wizardID', session.get('wizard')))
    locale = _validate('locale', request.form.get('currentLocale', session.get('locale')))

    country = request.form.get('countryID', n_a)
    region = request.form.get('regionID', n_a)
    user = request.form.get('userID', n_a)

    exchange = _make_exchange(mode, locale, country, region, user=request.form.get('clientName', n_a))
    exchange['wizard'] = wizard

    page = _make_page(wizard, locale, init_only=True)

    kw = _make_platform(wizard, locale, user, debug)

    kw['links']['close'] = re.sub(r'index|log(?i)', '', request.referrer or request.url)

    kw['extra'] = { \
        'log_headers'        : getLogVisibleHeaders(),
        'statistics_headers' : getStatisticsVisibleHeaders(),
        'images'             : getLogImages(),
    }

    forms = ('load', 'search',)

    keywords = _make_keywords()

    kw.update({ \
        'title'    : gettext('Helper Configurator Order Log Page'),
        'host'     : host,
        'wizard'   : wizard,
        'locale'   : locale, 
        'exchange' : exchange, 
        'keywords' : keywords, 
        'forms'    : forms, 
        'page'     : page,
    })

    return respond('log.html', debug, **kw)

def respond(template='', debug=None, **kw):
    locale = kw.get('locale', '')
    host = kw.get('host', '')
    exchange = kw.get('exchange', {})
    keywords = kw.get('keywords', {})
    page = kw.get('page', None)

    response = make_response(render_template(template, \
        # ------------------
        # Communication Mode
        # ------------------
        authorized = kw['authorized'],
        external   = exchange['communication'] == COMMUNICATIONS['external'],
        internal   = exchange['communication'] == COMMUNICATIONS['internal'],
        exchange   = exchange,
        language   = get_locale(),
        # -------------
        # Client System
        # -------------
        agent      = kw['agent'],
        platform   = kw['platform'],
        locale     = locale,
        host       = host,
        os         = kw['os'],
        browser    = IsIE() and 'ie' or kw['browser'],
        version    = request.args.get('_v', '') or kw['version'] or '',
        css        = kw['css'],
        screen     = kw['screen'],
        scale      = kw['scale'],
        style      = kw['style'],
        is_frame   = kw['is_frame'],
        is_demo    = demo(),
        # -----------------
        # Page & Properties
        # -----------------
        title      = kw.get('title'),
        name       = page and page.get_title() or gettext('Helper Configurator Main Page'),
        article    = page and page.get_article() or '',
        image      = page and page.get_image() or '',
        root       = kw['root'],
        loader     = '/loader?locale=%s%s' % (locale, debug and '&debug=1' or ''),
        referer    = kw['referer'],
        base       = page and page.get_base() or '',
        uri        = page and page.get_uri() or {},
        forms      = kw['forms'],
        document   = '',
        price      = gettext(n_a),
        links      = kw['links'],
        keywords   = keywords,
        page       = page,
        # -------------
        # Extra entries
        # -------------
        extra      = kw.get('extra', None),
    ))
    #response.headers['content-length'] = str(len(response.data)+419)
    return response

@app.route('/loader', methods = ['GET', 'POST'])
def loader_with_logger():
    #
    # Codes of action:
    #   100 - confirmation for an order
    #   203 - base calculation
    #   204 - custom calculation
    #   205 - save of state
    #   206 - finalize (internal)
    #   207 - order
    #   208 - close of session
    #   209 - cancel (Flash only)
    #   210 - continue (Flash only)
    #   301 - load log page
    #   302 - load selected log item content
    #   303 - load and refresh saved calculation
    #   304 - custom calculation (log+db)
    #   305 - price statistics
    #   307 - order (log+db)
    #   308 - remove log item
    #
    try:
        return loader()
    except:
        #traceback.print_exc(file=open(errorlog, 'a'))
        print_exception()
        raise

def loader():
    if not request.form.get('wizardID'):
        return ''

    host = request.form.get('host')
    debug = request.args.get('debug') == '1' and True or False
    demo(request.form.get('demo'), request=request)

    setReference(host, debug)

    if IsDebug:
        start = datetime.datetime.now()
        print '--> Started at %s' % start.strftime('%H:%M:%S:%f')

    wizard = request.form.get('wizardID') or session.get('wizard')
    action = request.form.get('action') or '204'
    check = request.form.get('check') or ''

    communication = request.form.get('helperCommunicationType') or default_communication
    locale = request.form.get('currentUsedLocalization') or session.get('locale')

    exchange_error = 0

    if IsDebug:
        print '--> action: [%s]' % action
        print '--> communication: [%s]' % communication
        print '--> demo: [%s]' % demo()
        print '--> host: [%s]' % host
        print '--> wizard: [%s]' % wizard

    response = {}

    if not (action and action in valid_action_types):
        return ''

    IsChecked = True

    if not isAuthorized(request.form.get('userID')):
        exchange_error = -4
        exchange_message = gettext('Sorry, you are not authorized.')

        IsChecked = False

    if IsChecked and action in ('207','307') and demo() and not _check(wizard, check):
        exchange_error = -5
        exchange_message = gettext('Sorry, the confirmation code is invalid.')+'<br>'+gettext('Please, try more.')

        IsChecked = False

    if action in ('301','302','303','304','305','307','308',):

        if IsChecked:
            # -------------------------------------------------------------------------------------
            # Get Data from DB (XML:data, DOM:dom, parsed XML-Items:items or Log-page content:data)
            # -------------------------------------------------------------------------------------
            response = respond_log(action)

        if not (response and response.get('data')):
            pass

        elif action in ('303','304','307',):
            requested_action = str(int(action)-100)

            # --------------------------------------------------
            # Get XML (update tags for a new request to Service)
            # --------------------------------------------------
            check, data = getRequestXML(requested_action, request, session, data=response.get('items'), dom=response.get('dom'), 
                title=response.get('title'), page='log',
                url=host)

            # ----------------------------------------
            # Send request to Service and get response
            # ----------------------------------------
            response = respond_external(requested_action, data=data, id=response.get('id'))
            response['action'] = action

            # -------------------------------------------------------------
            # Get Data Dictionary (!!!) from response to send to Controller
            # -------------------------------------------------------------
            if action == '303':
                dom, data = receive(action, request, session, data=response.get('data'))
                response['data'] = data

            response['dom'] = None
            response['items'] = None

        else:
            # --------------------------------------
            # Remove DOM from response to Controller
            # --------------------------------------
            response['dom'] = None
            response['items'] = None

    elif communication == COMMUNICATIONS['external'] or not communication:
        if IsDebug:
            print '--> check: [%s] = %s' % (check, IsChecked)

        if action == '100':
            # -------------------
            # Validate the action
            # -------------------
            if not demo():
                response = {'x1' : None, 'x2' : None, 'op' : None}
            else:
                response = _set_checker(wizard)
        
        elif action in ('203','204','205',):
            # ---------------------------------------------------------------
            # Send External request to Service and get response (calculation)
            # ---------------------------------------------------------------
            response = respond_external(action)
        
        elif action in ('207',) and IsChecked:
            # ---------------------------------------------------------
            # Send External request to Service and get response (order)
            # ---------------------------------------------------------
            response = respond_external(action)

        if response:
            response['data'] = ''

    elif communication == COMMUNICATIONS['internal']:
        if action == '100':
            # -------------------
            # Validate the action
            # -------------------
            response = {'x1' : None, 'x2' : None, 'op' : None}

        elif action in ('203','204','205','206',):
            # -------------------------------------------------
            # Send Internal request to Service and get response
            # -------------------------------------------------
            response = respond_internal(action)

    if not response:
        response = { \
            'action'            : action,
            'op'                : '',
            # -------------------------------
            # Not authorized or check invalid
            # -------------------------------
            'exchange_error'    : exchange_error, 
            'exchange_message'  : exchange_message,
            'error_code'        : '',
            'error_description' : '',
            'errors'            : '',
            # -----------------
            # Results (no data)
            # -----------------
            'price'             : '',
            'data'              : '',
        }            

    if IsDebug:
        finish = datetime.datetime.now()
        t = finish - start
        print '--> Finished at %s' % finish.strftime('%H:%M:%S:%f')
        print '--> Spent time: %s sec' % ((t.seconds*1000000+t.microseconds)/1000000)

    return jsonify(response)

def _random(min, max):
    return ('00'+str(random.randint(min, max)))[-2:]

def _set_checker(wizard):
    _min = 1
    _max = 20
    x1 = _random(_min, _max)
    x2 = -1
    while x2 == -1 or x2 == x1:
        x2 = _random(_min, _max)
    x1, x2 = (max(x1, x2), min(x1, x2))
    op = random.randint(0, 1) and '+' or '-'

    checker_id = 'checker:%s' % wizard
    checker_value = '%s:%s:%s' % (x1, x2, op)

    if IsDebug:
        print '--> set session checker: [%s, %s]' % (checker_id, checker_value)

    session[checker_id] = checker_value

    return { \
        'x1' : x1,
        'x2' : x2,
        'op' : op,
    }

def _check(wizard, value):
    if len(value) == 0:
        return False

    checker_id = 'checker:%s' % wizard
    checker_value = session.get(checker_id)

    if IsDebug:
        print '--> get session checker: [%s, %s]' % (checker_id, checker_value)

    try:
        x1, x2, op = checker_value.split(':')
        x1 = int(x1)
        x2 = int(x2)
        result = int(value)
    except:
        return False
    if op == '+':
        return x1+x2 == result and True or False
    if op == '-':
        return x1-x2 == result and True or False
    return False

def _demo_price(action):
    return 0, '', float(1000)*random.random(), 'USD'

def _demo_order(action):
    return action == '207' and ('ABC' + str(int(float(1000000)*random.random())), getTime(), ) or ('', '',)

def _order(dom):
    number = getDOMItemValue(dom, 'documentNumber')
    date = getDOMItemValue(dom, 'documentDate')

    if IsDebug:
        print '--> Number: [%s]' % number
        print '--> Date: [%s]' % date

    return { 'number' : number, 'date' : date, }

def respond_internal(action, **kw):
    exchange_error = 0
    exchange_message = ''
    error_code = ''
    error_description = ''
    response = {}
    dom = None
    data = ''
    currency = ''
    order_number = ''
    order_date = ''

    print_action(action, 'Respond.Internal')

    op = request.form.get('op') or kw.get('op')

    if IsDebug:
        print '--> op: [%s]' % op

    if not op:
        pass

    elif op == 'get':
        # --------------------------------------------------------------
        # Generate and Send XML to Service (from WEB-form to JavaScript)
        # --------------------------------------------------------------
        data = getXml(action, request, session)
        errors = []

    elif op == 'set':
        # -----------------------------------------------
        # Receive XML from Service (loaded by JavaScript)
        # -----------------------------------------------
        dom, data = receive(action, request, session, **kw)

        if demo():
            exchange_error, exchange_message, total, currency = _demo_price(action)
            order_number, order_date = _demo_order(action)
        else:
            total = float(getDOMItemValue(dom, 'total'))
            currency = CURRENCIES.get(getDOMItemValue(dom, 'currency'), gettext('undefined'))
            error_code = getDOMItemValue(dom, 'errorCode').strip()
            error_description = getDOMItemValue(dom, 'errorDescription')

        errors = getDOMErrors(dom) or ''

        if IsDebug:
            print '--> Total: %s %s' % (total, currency)

        total = '%.2f' % total or ''
        price = '%s %s' % (total, currency) or ''

    return { \
        'action'            : action,
        'op'                : op,
        # --------------
        # Service Errors
        # --------------
        'exchange_error'    : exchange_error, 
        'exchange_message'  : exchange_message,
        'error_code'        : error_code,
        'error_description' : error_description,
        'errors'            : errors,
        # ---
        # IDs
        # ---
        'countryID'         : getDOMItemValue(dom, 'countryID') or '',
        'regionID'          : getDOMItemValue(dom, 'regionID') or '',
        'userID'            : getUserID(getDOMItemValue(dom, 'userID')),
        # --------------
        # Client Details
        # --------------
        'country_name'      : getDOMItemValue(dom, 'countryName') or getCountry(getDOMItemValue(dom, 'countryID')),
        'region_name'       : getDOMItemValue(dom, 'regionName') or getRegion(getDOMItemValue(dom, 'regionID')),
        'client_name'       : getClient(getDOMItemValue(dom, 'userName')),
        # ------------------------------
        # Results (Price & XML-Response)
        # ------------------------------
        'price'             : price,
        'data'              : data,
    }

def respond_external(action, **kw):
    exchange_error = 0
    exchange_message = ''
    error_code = ''
    error_description = ''
    errors = ''
    response = {}
    dom = None
    data = ''
    total = ''
    price = ''
    currency = ''
    document = ''
    order_number = ''
    order_date = ''

    print_action(action, 'Respond.External')

    locale = request.form.get('currentUsedLocalization') or ''
    wizard = request.form.get('wizardID') or ''

    try:
        # -------------------------------------
        # Get DOM and XML response from Service
        # -------------------------------------
        exchange_error, exchange_message, dom, data = send(action, request, session, **kw)

        if demo():
            exchange_error, exchange_message, total, currency = _demo_price(action)
            order_number, order_date = _demo_order(action)
        elif exchange_error:
            total = 0.0
        elif dom is not None:
            total = float(getDOMItemValue(dom, 'total') or '0')
            currency = CURRENCIES.get(getDOMItemValue(dom, 'currency'), gettext('undefined'))
            error_code = getDOMItemValue(dom, 'errorCode').strip()
            error_description = getDOMItemValue(dom, 'errorDescription')

            if action == '207':
                order = _order(dom)
                order_number = order.get('number', '')
                order_date = order.get('date', '')
        elif data:
            x = request.form.get('price')
            total = x and float(x.split()[0])*1.288726 or 0
    except:
        msg = '--> Send error!'
        print_to(errorlog, [msg, data], request=request)
        # ----------------------
        # Service Exchange Error
        # ----------------------
        if IsDeepDebug:
            print msg
        raise

    #print_to(errorlog, ['>>> Data:', data])

    IsValid = data and True or False

    if exchange_message and exchange_message == exchange_error:
        exchange_message = ''
    if error_description and error_description == error_code:
        error_description = ''

    # -----------------
    # Response is valid
    # -----------------

    if IsValid:
        errors = getDOMErrors(dom) or ''

        if IsDeepDebug:
            print errors

        if currency in ('undefined', n_a, '') or not total:
            if not exchange_message:
                if action == '203' and error_code in ('', '0',):
                    pass
                else:
                    exchange_message = gettext('Calculation is not performed.')
            IsValid = False

        total = IsValid and '%.2f' % total or ''
        price = IsValid and '%s %s' % (total, currency) or ''

        if IsDebug:
            print '--> Total: %s' % price

        document = order_number and ('# %s %s %s' % (order_number, gettext('at'), order_date)) or ''

    # -------------------------------------------
    # Make parameters and Register response in DB
    # -------------------------------------------

    attrs = { \
        'locale'            : locale,
        'selected_item'     : kw.get('id') or request.form.get('selected_item'),
        'title'             : request.form.get('title') or '',
        'document'          : document or action,
        'total'             : total,
        'currency'          : currency,
        'countryID'         : getCountryID(getDOMItemValue(dom, 'countryID'), locale),
        'regionID'          : getRegionID(getDOMItemValue(dom, 'regionID'), locale),
        'userID'            : getUserID(getDOMItemValue(dom, 'userID'), locale),
        'userName'          : getClient(getDOMItemValue(dom, 'userName'), locale),
        'wizardID'          : wizard,
        'wizardName'        : request.form.get('wizardName') or '',
        'custom_code'       : request.form.get('custom_code') or '',
        'option_update'     : request.form.get('option_update') or '',
        'option_cost'       : request.form.get('option_cost') or '',
        'data'              : data, #getDOMTagStrippedValue(dom, 'parameters'),
    }

    #print_to(errorlog, ['>>> Total:', total])

    if IsValid and action in ('203','204','205','207',): # and dom
        response = register(action, dom, attrs)

        if IsDeepDebug:
            print '>>> DB Response:%s' % response

    order = action == '205' and response.get('custom_code') or document

    return { \
        'action'            : action,
        'op'                : '',
        # --------------
        # Service Errors
        # --------------
        'exchange_error'    : exchange_error, 
        'exchange_message'  : exchange_message,
        'error_code'        : error_code,
        'error_description' : error_description,
        'errors'            : errors,
        # ---
        # IDs
        # ---
        'countryID'         : getDOMItemValue(dom, 'countryID') or '',
        'regionID'          : getDOMItemValue(dom, 'regionID') or '',
        'userID'            : attrs['userID'],
        # --------------
        # Client Details
        # --------------
        'country_name'      : getDOMItemValue(dom, 'countryName') or getCountry(getDOMItemValue(dom, 'countryID'), locale),
        'region_name'       : getDOMItemValue(dom, 'regionName') or getRegion(getDOMItemValue(dom, 'regionID'), locale),
        'client_name'       : attrs['userName'],
        # ----------
        # Order Info
        # ----------
        'document_number'   : order_number,
        'document_date'     : order_date,
        'order'             : order,
        # -------
        # DB Data
        # -------
        'total_log_rows'    : getLogTotal({'userID' : attrs['userID'], 'wizardID' : wizard}),
        'custom_code'       : response.get('custom_code', ''),
        'next_custom_code'  : response.get('next_custom_code', ''),
        'option_update'     : response.get('option_update', ''),
        'option_cost'       : response.get('option_cost', ''),
        'title'             : response.get('title', ''),
        # ------------------------------
        # Results (Price & XML-Response)
        # ------------------------------
        'price'             : price,
        'data'              : data,
    }

def respond_log(action):
    exchange_error = 0
    exchange_message = ''

    page = None

    current_page, pages, per_page, has_prev, has_next, total, id = (0, 0, 0, False, False, 0, None)
    iter_pages = []
    order = None
    data = None
    dom = None
    items = None
    title = ''

    print_action(action, 'Respond.Log')

    locale = request.form.get('currentUsedLocalization') or ''

    try:
        # ----------------
        # Get Data from DB
        # ----------------
        if not action:
            pass
        elif action == '301':
            exchange_error, exchange_message, page, data = getLogPage(action, request, session)
        elif action == '305':
            exchange_error, exchange_message, id, total, data = getStatictics(action, request, session)
        elif action == '308':
            exchange_error, exchange_message, page, data = removeLogItem(action, request, session)
        else: #if action in ('302','303','304','307',):
            exchange_error, exchange_message, id, order = getLogItem(action, request, session)
    except:
        msg = '--> Database error!'
        # -------------
        # DB Log failed
        # --------------
        print_to(errorlog, msg, request=request)
        raise

    if not (action and action in valid_action_types):
        pass

    elif action in ('301','308',):
        # --------------------
        # Get Log-page content
        # --------------------
        if page:
            current_page, pages, per_page, has_prev, has_next, total = page.get_page_params()
            iter_pages = page.iter_pages()

        if IsDebug:
            print '--> LogPage[%s]: items:[%s] %s-%s-%s-%s iter:%s' % ( \
                current_page, len(data), pages, per_page, has_prev, has_next, iter_pages)
    
    elif action in ('302',):
        # ------------------------------
        # DOM and XML-Items (Dictionary)
        # ------------------------------
        dom, data = receive(action, request, session, data=order.data) #, products_sorted=True

        if IsDebug:
            print '--> LogPageItem[%s]: Data %s, Products %s, Parameters %s' % ( \
                id, len(order.data), len(data['products']), len(data['parameters']))
    
    elif action in ('303','304','307',):
        # ---------
        # Clean XML
        # ---------
        data = order.data #_data(coding='encode')

        # ------------------------------
        # DOM and XML-Items (Dictionary)
        # ------------------------------
        dom, items = receive(action, request, session, data=data)

        title = order.title

        if IsDebug:
            print '--> Loaded LogPageItem[%s]: Data %s, Products %s, Parameters %s' % ( \
                id, len(order.data), len(items['products']), len(items['parameters']))

    elif action in ('305',):

        if IsDebug:
            print '--> LogStatictics[%s]: Data %s' % ( \
                id, data and len(data), )

    if exchange_error:
        if IsDebug:
            print '--> ExchangeError[%s]: %s' % (exchange_error, exchange_message)

    return { \
        'action'            : action,
        'op'                : '',
        # --------------
        # Service Errors
        # --------------
        'exchange_error'    : exchange_error, 
        'exchange_message'  : exchange_message,
        # -----------------------------
        # Results (Log page parameters)
        # -----------------------------
        'id'                : id,
        'rows_on_page'      : len(data),
        'total'             : total,
        'page'              : current_page,
        'pages'             : pages,
        'per_page'          : per_page,
        'has_prev'          : has_prev, 
        'has_next'          : has_next,
        'iter_pages'        : iter_pages,
        # --------------------------
        # Results (Log page content)
        # --------------------------
        'custom_code'       : order and order.code or '',
        'title'             : title,
        'price'             : '',
        'data'              : data,
        'dom'               : dom,
        'items'             : items,
    }

