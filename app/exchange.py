# -*- coding: utf-8 -*-

import sys
import os
import datetime
import re
import urllib2

from urllib import urlencode
from xml.dom.minidom import parseString
from types import UnicodeType, DictType, ListType, TupleType, StringType, IntType, LongType, FloatType, BooleanType
from string import strip, upper, lower

#from flask import url_for, jsonify
from flask.ext.babel import gettext

from config import getReference, IsDebug, IsDeepDebug, IsUseEncoding, \
     default_encoding, default_unicode, default_print_encoding, default_path, \
     print_action, print_to, demo, errorlog, n_a
from wizard import _getListValue

BASE_URL = BASE_PATH = REFERENCE_PATH = HELPER_URL = ''

list_types = (ListType, TupleType,)
string_types = (UnicodeType, StringType,)

RECEIVED_ITEMS = ( \
    'documentDate',
    'documentNumber',
    'lineNumber',
    'priceTypeID',
    'userTypeID', 
    'userEmail', 
    'userName',
    'withoutRestriction',
)

SERVICE_ITEMS = ( \
    'constSavedImage',
    'cp_wizard_id',
    'constructCB000000000',
)

EOL = '\n'
EOT = '<br>\n'
EOS = '.'
XML_PREFIX = "<?xml"

CDATA = '<![CDATA['

# ------------------------
#   Шаблоны XML запросов
# ------------------------

REQUEST_XML_TEMPLATE = """
<?xml version="1.0"?>
<document xmlns:wms="http://www..ru/2008/wms" id="exchangeData" type="fieldsValue">
  <system id="-CIS" version="%(CIS)s"/>
  <task id="CALCHELPER" version="%(helperLoadedVersion)s"/>
  <description id="ExchangeContent" version="%(helperXMLVersion)s"/>
  <action>%(action)s</action>
  <countryID>%(countryID)s</countryID>
  <currency>%(currency)s</currency>
  <documentID>%(documentID)s</documentID>
  <documentDate>%(documentDate)s</documentDate>
  <documentNumber>%(documentNumber)s</documentNumber>
  <errorCode>0</errorCode>
  <errorDescription>%(n_a)s</errorDescription>
  <httpHost>%(helperHttpHost)s</httpHost>
  <httpReferer><![CDATA[%(helperHttpReferer)s]]></httpReferer>
  <lanquage id="%(currentUsedLocalization)s"/>
  <lineNumber>%(n_a)s</lineNumber>
  <orderEmail>%(orderEmail)s</orderEmail>
  <orderInfo>%(orderInfo)s</orderInfo>
  <pageLocation><![CDATA[%(helperPageLocation)s]]></pageLocation>
  <priceTypeID>%(priceTypeID)s</priceTypeID>
  <requestURI><![CDATA[%(helperRequestURI)s]]></requestURI>
  <regionID>%(regionID)s</regionID>
  <security>%(securityID)s</security>
  <sessionID>%(sessionID)s</sessionID>
  <total>0</total>
  <userAgent><![CDATA[%(helperUserAgent)s]]></userAgent>
  <userID>%(userID)s</userID>
  <userTypeID>%(userTypeID)s</userTypeID>
  <webResource>%(helperWebResource)s</webResource>
  <withoutDB>%(withoutDB)s</withoutDB>
  <withoutRestriction>%(withoutRestriction)s</withoutRestriction>
  <wizardID>%(wizardID)s</wizardID>
  <wizardName>%(wizardName)s</wizardName>
  %(content)s
</document>
"""

CONTENT_XML_V1_TEMPLATE = """
    %(parameters)s
    %(products)s
"""

PRODUCTS_XML_V1_TEMPLATE = """
    <products>
%s
    </products>
"""

PARAMETERS_XML_V1_TEMPLATE = """
    <parameters>
%s
    </parameters>
"""

CONTENT_XML_V2_TEMPLATE = """
    <products>
%s
    </products>
"""

PRODUCT_XML_V2_TEMPLATE = """
      <product id="%(option)s" type="NUMBER" unit="" price="n/a" value="1"%(default)s>%(content)s</product>
"""

PARAMETERS_XML_V2_TEMPLATE = """
        <parameters>
%s
        </parameters>
"""

OPTIONS_XML_V2_TEMPLATE = """
        <options>
%s
        </options>
"""

CONSTRUCT_XML_TEMPLATE = """%(indent)s<product id="%(code)s" type="NUMBER" unit="" price="%(n_a)s">%(value)s</product>"""

PRODUCT_XML_TEMPLATE = """%(indent)s<product id="%(code)s" type="%(type)s" unit="%(unit)s" price="%(price)s">%(value)s</product>"""

OPTION_XML_TEMPLATE = """%(indent)s<option id="%(code)s" type="%(type)s" unit="%(unit)s" price="%(price)s">%(value)s</option>"""

PARAMETER_XML_TEMPLATE = """%(indent)s<parameter id="%(cis)s"%(parent)s type="%(type)s" unit="%(unit)s" price="%(price)s">%(value)s</parameter>"""

############################################################################################################################

def getDOMTagValue(dom, tag):
    v = dom.getElementsByTagName(tag)
    return v and len(v) and v[0].toxml() or ''

def getDOMTagStrippedValue(dom, tag):
    v = getDOMTagValue(dom, tag)
    return v and re.sub(r'>\s*?<', '><', v.strip()) or ''

def getDOMItemValue(dom, tag, prefix=''):
    v = ''
    try:
        if dom:
            for item in dom.getElementsByTagName(tag):
                value = item.toxml()
                m = re.search(r'>(.*)<', value)
                if m:
                    if v:
                        v += EOT
                    v += ('%s %s' % (prefix, m.group(1))).strip()
    except:
        pass
    return v != n_a and v or ''

def _get_dom_value_by_key(key, x):
    r = re.compile(r'%s="(.*?)"' % key)
    m = re.search(r, x)
    return m and m.group(1) or ''

def getDOMProducts(dom, tag=None):
    items = []
    if not dom:
        return items
    keys = ('id', 'article', 'title', 'type', 'price', 'unit', 'vid',)

    try:
        for item in dom.getElementsByTagName(tag or 'product'):
            x = item.toxml()
            #values = dict(zip(keys, map(lambda x:'', xrange(0,len(keys)))))
            values = dict(zip(keys, ['']*len(keys)))
            for key in keys:
                values[key] = _get_dom_value_by_key(key, x)
            m = re.search(r'>(.*)<', x)
            if m:
                values['value'] = m.group(1)
            items.append(values)
    except:
        pass
    return items

def getDOMParameters(dom, with_guid=False):
    giud = re.compile(r'\w{8,}?-\w{4,}?-\w{4,}?-\w{4,}?-\w{12,}?')
    items = []
    if not dom:
        return items
    keys = ('id', 'parent', 'price', 'type', 'unit', 'value',)
    try:
        for item in dom.getElementsByTagName('parameter'):
            x = item.toxml()
            values = dict(zip(keys, ['']*len(keys)))
            for key in keys:
                values[key] = _get_dom_value_by_key(key, x)
            m = re.search(r'>(.*)<', x)
            if m:
                values['value'] = m.group(1)
            if re.search(giud, values['id']) and not with_guid:
                continue
            items.append(values)
    except:
        pass
    return items

def getDOMErrors(dom, tag='error', prefix=''):
    v = ''
    try:
        if dom:
            for item in dom.getElementsByTagName(tag):
                value = item.toxml()
                m = re.search(r'>(.*)<', value)
                if m:
                    value = m.group(1)
                    if re.search(r'id:\s+construct[\w]*', value):
                        continue
                    if value.strip()[-1:] != EOS:
                        value += EOS
                    if v:
                        v += EOT
                    v += ('%s %s' % (prefix, value)).strip()
    except:
        pass
    return v != n_a and v or ''

def getURLInfo(url, item=None):
    m = re.search(r'(http([s]?)://([\w\.\:\-\_]+)/)([\w\.\&\=\?\-\_]*)', url)
    host, ssl, host_name, app_name = m and m.groups() or ('', '', '', '',)
    if not item:
        return host, ssl, host_name, app_name
    else:
        if item == 'host':
            return host
        elif item == 'ssl':
            return ssl and True or False
        elif item == 'host_name':
            return host_name
        elif item == 'app_name':
            return app_name
        else:
            return ''

def _session_exists(session):
    return session['session'] and session['session'] != n_a and True or False

def data_encode(x, is_clear=None):
    return x

def data_decode(x, is_clear=None):
    return x

def cleanHtml(value):
    return value and re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', value)) or ''

def _create_request_attrs(action, request, session, **kw):
    """
        Create Request XML attrs dictionary.

        Arguments (**kw):
            content - products/parameters tags
            dom     - DOM object
            title   - title of the calculation (from DB)
            page    - page(script) name: log
            url     - Web-Service Domain URL

        Returns:
            attrs   - Dictionary (requested items)
    """
    form = request.form

    host, ssl, host_name, app_name = getURLInfo(kw.get('url') or request.url)
    locale = session.get('locale', 'rus')
    wizard = form.get('wizardID') or '' # or session.get('session') or ''

    # -----------
    # Request URI
    # -----------
    helperHttpHost = getURLInfo(form.get('host', None) or host, item='host_name')
    helperHttpReferer = form.get('helperHttpReferer', None) or host

    host = getURLInfo(request.url, 'host')

    page = kw.get('page') or ''

    # -----------------------------
    # Order Info tag from the Title
    # -----------------------------
    title = kw.get('title', '')

    orderInfo = title and re.sub(r':\s+', '::', re.sub(r',\s+', '||', title)) or ''

    # ----------------
    # Request XML Tags
    # ----------------
    attrs = {
        'CIS'              : '1',
        'action'                  : action,
        'countryID'               : form.get('countryID', None) or n_a,
        'currency'                : form.get('currency', None) or n_a,
        'orderEmail'              : form.get('orderEmail', None) or n_a,
        'orderInfo'               : form.get('orderInfo', None) or n_a,
        'priceTypeID'             : form.get('priceTypeID', None) or n_a,
        'regionID'                : form.get('regionID', None) or n_a,
        'userID'                  : form.get('userID', None) or n_a,
        'userTypeID'              : form.get('userTypeID', None) or n_a,
        'currentUsedLocalization' : upper(locale),
        'documentID'              : form.get('documentID', None) or n_a,
        'documentNumber'          : n_a,
        'documentDate'            : n_a,
        'errorCode'               : '',
        'errorDescription'        : '',
        'helperDefaultName'       : '',
        'helperWebResource'       : host,
        'helperHttpHost'          : helperHttpHost,
        'helperHttpReferer'       : helperHttpReferer,
        'helperPageLocation'      : '%s%s?wizard=%s&locale=%s' % (host, page, wizard, locale),
        'helperRequestURI'        : request.url,
        'helperUserAgent'         : request.user_agent,
        'helperLoadedVersion'     : form.get('helperLoadedVersion', None) or '2',
        'helperModelVersion'      : form.get('helperModelVersion', ''),
        'helperXMLVersion'        : kw.get('version') or '1',
        'helperVersion'           : form.get('helperVersion', ''),
        'securityID'              : data_decode(session.get('security') or form.get('securityID'), True) or n_a,
        'sessionID'               : data_decode(session.get('session') or form.get('sessionID'), True) or n_a,
        'total'                   : '',
        'withoutDB'               : form.get('withoutDB', None) or 'true',
        'withoutRestriction'      : form.get('withoutRestriction', None) or 'false',
        'wizardID'                : wizard,
        'wizardName'              : cleanHtml(form.get('wizardName') or session.get('name') or ''),
        'orderInfo'               : orderInfo,
        'content'                 : kw.get('content') or '',
        'n_a'                     : n_a,
    }

    return attrs

def getRequestContent(dom, version=None):
    """
        Returns products/parameters items from DOM for current HelperXMLVersion.
    """
    helperXMLVersion = '1'

    if not version:
        x = dom.getElementsByTagName('description')[0]
        if x and x.hasAttribute('version'):
            helperXMLVersion = x.getAttribute('version') or helperXMLVersion

    _print_item(helperXMLVersion, 'helperXMLVersion')

    if helperXMLVersion == '2':
        # -------------
        # XML VERSION 2
        # -------------
        products = []
        parameters = []

        keys = 'abcde'

        for i, product in enumerate(dom.getElementsByTagName('product')):
            is_default = product.hasAttribute('default') and product.getAttribute('default') == '1' and True or False
            key = not is_default and keys[i] or ''

            for option in getDOMProducts(product, tag='option'):
                if key:
                    option['id'] = '%s:%s' % (key, option['id'])
                products.append(option)

            for parameter in getDOMParameters(product, False):
                if key:
                    parameter['id'] = '%s:%s' % (key, parameter['id'])
                parameters.append(parameter)

    else:
        # -------------
        # XML VERSION 1
        # -------------

        products = getDOMProducts(dom)
        parameters = getDOMParameters(dom, False)

    return products, parameters

def getRequestXML(action, request, session, data=None, dom=None, title=None, page=None, url=None):
    """
        Generate XML from DB.
        Get XML-Items and DOM from **kw (DB), generate XML and return it to the caller.

        Arguments:
            action  - 303|304|307 for Log
            request - form.data
            session - current session
            kw      - Data (Data Dictionary made by receive) and DOM-object.

        Returns:
            data    - XML (String).
    """
    if not data or not dom:
        return ''

    print_action(action, 'Exchange.getRequestXML')

    form = request.form

    level0 = ' '*6
    level1 = ' '*8
    level2 = ' '*10

    helperXMLVersion = form.get('helperXMLVersion', None) or '1'

    # unicode -> utf8
    if title and not isinstance(title, unicode):
        title = title.decode(default_unicode, 'ignore')

    content = ''

    if helperXMLVersion == '1':
        # -------------
        # XML VERSION 1
        # -------------

        products = ''
        for x in data['products']:
            x['indent'] = level1
            x['code'] = x['id']
            x['price'] = n_a
            if x['unit'] == n_a:
                x['unit'] = ''
            products += (products and EOL or '')+(PRODUCT_XML_TEMPLATE % x)

        parameters = ''
        for x in data['parameters']:
            x['indent'] = level1
            x['cis'] = x['id']
            if x['parent']:
                x['parent'] = ' parent="%s"' % x['parent']
            x['price'] = n_a
            if x['unit'] == n_a:
                x['unit'] = ''
            parameters += (parameters and EOL or '')+(PARAMETER_XML_TEMPLATE % x)

        content = CONTENT_XML_V1_TEMPLATE % {
            'products'   : (PRODUCTS_XML_V1_TEMPLATE % products).strip(),
            'parameters' : (PARAMETERS_XML_V1_TEMPLATE % parameters).strip(),
        }
        
        check = (products or parameters) and 1 or 0

    else:
        # -----------------------
        # XML VERSION 2 and other
        # -----------------------

        content = \
            re.sub(r'\n\s+<parameter\s+id="\w{8,}?-\w{4,}?-\w{4,}?-\w{4,}?-\w{12,}?".*?\/(parameter)?>', r'',
            re.sub(r'\s+(article|title)=".*?"', '', 
            re.sub(r'price=".*?"', 'price="%s"' % n_a, 
            getDOMTagValue(dom, 'products'))))

        check = 1

    _print_xml(content, 'XML Content')

    attrs = _create_request_attrs(action, request, session, content=content, version=helperXMLVersion, 
        title=title, page=page, url=url) #, url=HELPER_URL

    return check, (REQUEST_XML_TEMPLATE % attrs).strip() # data

def setRequestContent(form, indent, templates, key='', is_default=None):
    def isItemValid(cis, key, is_default=None):
        if is_default:
            return ':' not in cis or cis.startswith(key)
        else:
            return cis.startswith(key+':')

    check = 0

    index, parameters = _getListValue(form.get('parameters'))
    x = []
    p = []
    for (id, cis, typ, title, value, unit, code) in parameters:
        if key and not isItemValid(cis, key, is_default):
            continue
        if ':' in cis:
            cis = cis[2:]
        if len(cis) == 11 and (cis.startswith('CB') or cis.isdigit()):
            p.append((cis, typ, unit, value))
            continue
        item = {'indent':indent, 'id':id, 'cis':cis, 'type':typ, 'unit':unit, 'value':value, 'code':code, 'price':n_a, 'parent':''}
        if typ == 'LIST':
            if ':' in value:
                value = value.split(':')[1]
            item['parent'] = ' parent="%s" ' % cis
            item['cis'] = '%s_%s' % (cis, value)
            item['type'] = 'BOOLEAN'
            item['value'] = 'true'
        if isinstance(item['value'], basestring) and typ == 'STRING':
            item['value'] = re.sub(r'<[\w\\]+>', r'', item['value'])
        x.append(templates[0] % item)
        if cis not in SERVICE_ITEMS:
            check = 1
    parameters = EOL.join(x)

    index, margins = _getListValue(form.get('margins'))
    x = []
    for (code, typ, unit, value) in margins + p:
        if key and not isItemValid(code, key, is_default):
            continue
        if ':' in code:
            code = code[2:]
        item = {'indent':indent, 'code':code, 'type':typ, 'unit':unit, 'value':value, 'price':n_a}
        x.append(templates[1] % item)
        if code not in SERVICE_ITEMS:
            check = 1
    products = EOL.join(x)

    return check, parameters, products

def setRequestXML(action, request, session):
    """
        Generate XML from the WEB-form.
        Get XML-Items and DOM from **kw (WEB-form), generate XML and return it to the caller.

        Arguments:
            action  - 203|204|207 for Internal/External
            request - form.data (product/parameters/options)
            session - current session.

        Returns:
            data    - XML (String).
    """
    form = request.form

    print_action(action, 'Exchange.setRequestXML')

    level0 = ' '*6
    level1 = ' '*8
    level2 = ' '*10

    helperXMLVersion = form.get('helperXMLVersion', None) or '1'

    if helperXMLVersion == '2':
        # -------------
        # XML VERSION 2
        # -------------
        products = []

        for key in 'abcde':
            option = form.get('options[%s]' % key, None)
            if not option:
                break
            if IsDebug:
                print '--> option[%s]:%s' % (key, option)

            is_default = key == 'a' and True or False
            product = {
                'option'  : option,
                'default' : is_default and ' default="1"' or '',
                'content' : ''
            }

            check, parameters, options = setRequestContent(form, level2, (PARAMETER_XML_TEMPLATE, OPTION_XML_TEMPLATE,), key, is_default)
            
            #product['parameters'] = parameters.strip() and level1 + (PARAMETERS_XML_V2_TEMPLATE % parameters).strip() or ''
            #product['options'] = options.strip() and level1 + (OPTIONS_XML_V2_TEMPLATE % options).strip() or ''

            product['content'] = \
                (options.strip() and EOL+level1+(OPTIONS_XML_V2_TEMPLATE % options).strip() or '') + \
                (parameters.strip() and EOL+level1+(PARAMETERS_XML_V2_TEMPLATE % parameters).strip() or '')

            if product['content']:
                product['content'] += EOL+level0

            products.append(level0 + (PRODUCT_XML_V2_TEMPLATE % product).strip())

        content = CONTENT_XML_V2_TEMPLATE % EOL.join(products)

    else:
        # -----------------------
        # XML VERSION 1 (DEFAULT)
        # -----------------------
        check, parameters, products = setRequestContent(form, level1, (PARAMETER_XML_TEMPLATE, PRODUCT_XML_TEMPLATE,))

        if form.get('defaultConstruct', None) and form.get('defaultConstructCount', None):
            products = CONSTRUCT_XML_TEMPLATE % {'indent':level1, 'code':form['defaultConstruct'], 'value':form['defaultConstructCount'], 'n_a':n_a} + \
                EOL + products

        content = CONTENT_XML_V1_TEMPLATE % {
            'products'   : (PRODUCTS_XML_V1_TEMPLATE % products).strip(),
            'parameters' : (PARAMETERS_XML_V1_TEMPLATE % parameters).strip(),
        }

    attrs = _create_request_attrs(action, request, session, content=content, version=helperXMLVersion)

    return check, (REQUEST_XML_TEMPLATE % attrs).strip()

def getXml(action, request, session):
    # -------------------------
    # Get XML from the WEB-form
    # --------------------------
    check, xml = setRequestXML(action, request, session)

    if IsDeepDebug:
        print '--> XML Request:'
        try:
            print xml
        except:
            print xml.encode(default_unicode, 'ignore')
        print ''

    return xml.encode(default_unicode, 'ignore')

def _print_form(form):
    if not IsDeepDebug:
        return
    print '--> Loader Attributes:'
    print ''
    for key in sorted(form.keys(), cmp=lambda x,y: cmp(x.lower(), y.lower())):
        value = form.get(key)
        if key in ('margins', 'options', 'parameters',):
            lines = ['%s:' % key] + value.split(';')
        else:
            lines = ['%s:[%s]' % (key, value)]
        for line in lines:
            try:
                print line
            except:
                print line.encode(default_unicode, 'ignore')
    print ''

def _print_xml(xml, title):
    if not IsDeepDebug:
        return
    print '--> %s:' % title
    print ''
    try:
        if isinstance(xml, unicode):
            print xml
        else:
            # utf8 -> unicode
            print xml.decode(default_unicode, 'ignore')
    except Exception, error:
        print 'Encode error [%s]' % error
    print ''

def _print_item(value, title):
    if not IsDebug:
        return
    print '--> %s: %s' % (title, value)

def _print_products(items):
    if not IsDeepDebug:
        return
    print ''
    print '--> XML Products: %s' % len(items)
    print ''
    for n, item in enumerate(items):
        #x = '#%02d %s' % (n, 'id:%(id)s type:%(type)s price:%(price)s unit:%(unit)s vid:%(vid)s value:[%(value)s]' % item)
        x = '#%02d %s' % (n, (' '.join([x+':%('+x+')s' for x in item.keys()])) % item)
        try:
            print x
        except:
            print x.encode(default_unicode, 'ignore')

def _print_parameters(items):
    if not IsDeepDebug:
        return
    print ''
    print '--> XML Parameters: %s' % len(items)
    print ''
    for n, item in enumerate(items):
        #x = '#%02d %s' % (n, 'id:%(id)s parent:%(parent)s type:%(type)s unit:%(unit)s value:[%(value)s]' % item)
        x = '#%02d %s' % (n, (' '.join([x+':%('+x+')s' for x in item.keys()])) % item)
        try:
            print x
        except:
            print x.encode(default_unicode)
    print ''

def receive(action, request, session, **kw):
    """
        Receive XML from **kw (DB) or requested WEB-form, parse DOM and XML-Items and return its to the caller.
        From **kw(data) or requested WEB-form XML is ready.

        Arguments:
            action  - 203|204|205|206 for Internal, 303 for Log
            request - form.data (XML, Internal)
            session - current session
            kw      - data (XML, DB).

        Returns:
            dom     - DOM object
            data    - Data Dictionary (XML-Items).
    """
    error = None
    dom = None

    print_action(action, 'Exchange.Receive')

    form = request.form

    _print_form(form)

    data = kw.get('data') or form.get('data') or ''

    # unicode -> utf8
    if isinstance(data, unicode):
        data = data.encode(default_unicode, 'ignore')

    data = data.strip()

    if data and data.startswith(CDATA):
        data = data[9:-3]

    try:
        dom = parseString(data)
    except Exception, error:
        msg = '--> Invalid XML content!'
        # ---------------
        # Unvalid XML DOM
        # ---------------
        print_to(errorlog, [msg, data], request=request)
        #traceback.print_exc(file=open(errorlog, 'a'))
        raise

    items = {}
    for key in RECEIVED_ITEMS:
        items[key] = getDOMItemValue(dom, key)

    products, parameters = getRequestContent(dom) #, form.get('helperXMLVersion', None)

    items['products'] = products
    if kw.get('products_sorted'):
        #items['products'].sort(cmp=lambda x,y: cmp(x['id'], y['id']))
        #items['products'].reverse()
        import operator
        items['products'].sort(key=operator.itemgetter('id'), reverse=True)

    _print_products(items['products'])

    items['parameters'] = parameters

    _print_parameters(items['parameters'])

    return dom, items

def send(action, request, session, **kw):
    """
        Get XML from **kw or build it from the WEB-form, and send request to the External WEB-Service.
        WEB-form parameters are Helper tags: products, parameters and other.
        From **kw(data) XML is ready.

        Arguments:
            action  - 203|204|205|206 for External
            request - form (Helper tags)
            session - current session
            kw      - data (XML).

        Returns:
            exchange_error, exchange_message - exchange error info
            dom     - DOM object
            data    - XML (response of WEB-Service).
    """
    global BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL
    BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL = getReference()

    exchange_error = 0
    exchange_message = ''
    response = None
    error = None
    data = None
    dom = None

    print_action(action, 'Exchange.Send')

    form = request.form

    _print_form(form)

    if kw and 'data' in kw and kw.get('data'):
        data = kw['data']
        check = 1
    else:
        check, data = setRequestXML(action == '205' and '204' or action, request, session, **kw)

    _print_item(check, 'ready')

    if not check:
        # ----------------------------------
        # Request is not ready, data missing
        # ----------------------------------
        pass

    else:
        _print_xml(data, 'XML Request')

        url = HELPER_URL

        _print_item(url, 'URL')

        # unicode -> utf8
        if isinstance(data, unicode):
            data = data.encode(default_unicode, 'ignore')

        query = data.strip()

        # -----------------------
        # Send request to Service
        # -----------------------
        request = urllib2.Request( \
            url=url, 
            data=urlencode({'queryDocument':query}), 
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        data = None

        try:
            response = urllib2.urlopen(request)
            data = response.read()

        except Exception, error:
            exchange_message = '%s [%s]' % (gettext('No connection!'), url)
            # -----------------------
            # Server connection error
            # -----------------------
            exchange_error = -1

        if exchange_error and demo():
            # --------------------------------------------------
            # Only for demo purposes, web-service is unavailable
            # --------------------------------------------------
            return (0, exchange_message, parseString(query), query,)

        elif data and XML_PREFIX in data:
            # --------------
            # Response is OK
            # --------------
            data = data.replace(data[0:data.find(XML_PREFIX)], '').strip()

        elif not exchange_error:
            # --------------------------------------------
            # No XML Response (error from the application)
            # --------------------------------------------
            exchange_error = -2

        _print_xml(data, 'XML Response')

        try:
            # ---------
            # Parse DOM
            # ---------
            if not exchange_error and data:
                dom = parseString(data)

        except Exception, error:
            exchange_message = gettext('Not valid response!'),
            # ---------------
            # Unvalid XML DOM
            # ---------------
            exchange_error = -3

        if exchange_error and data and isinstance(data, str):
            data = re.sub(r'.*\n(.*)', r'\1', data)

        if exchange_error or error:
            _print_item(str(error).decode(default_encoding, 'ignore'), 'Error[%s]' % exchange_error)
        else:
            _print_item(exchange_error, 'OK')

    return exchange_error, exchange_message, dom, data

