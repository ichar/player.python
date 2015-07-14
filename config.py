# -*- coding: utf-8 -*-

import os
import sys
import codecs
import pytz
import datetime
import traceback

from flask.ext.babel import gettext
basedir = os.path.abspath(os.path.dirname(__file__))
errorlog = os.path.join(basedir.replace('\\htdocs\\player', ''), 'traceback.log')

from types import ListType, TupleType

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'storage', 'app.db')
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin@localhost/st1'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# For WSGI Web-server it should be True
IsConfiguratorsAbsolute = True

# Only permitted in Debug-mode
IsDebug = 0
IsDeepDebug = 0
IsDemo = 1
IsDBCheck = 0
IsUseEncoding = 1

default_encoding = 'cp1251'
default_unicode = 'utf8'
default_print_encoding = 'UTF-8' # sys.stdout.encoding
default_path = 'configurators'
n_a = 'n/a'

LOCAL_TZ = pytz.timezone('Europe/Moscow')
LOCAL_FULL_TIMESTAMP = '%d-%m-%Y %H:%M:%S'
LOCAL_EASY_TIMESTAMP = '%d-%m-%Y %H:%M'
UTC_EASY_TIMESTAMP = '%Y-%m-%d %H:%M'

COMMUNICATIONS = {
    'external' : 'External',
    'internal' : 'Internal'
}

default_communication = COMMUNICATIONS['external']

default_reference = 'dealer'

BASE_URL = ""
BASE_PATH = ""
REFERENCE_PATH = ""
HELPER_URL = ""

DOMAINS = { \
    'default' : 'localhost',
}

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
]

ansi = not sys.platform.startswith("win")

cr = '\n'

############################################################################################################################

def print_to(f, v, mode='a', request=None):
    items = type(v) not in (ListType, TupleType,) and [v] or v
    fo = open(f, mode=mode)
    for text in items:
        if IsDeepDebug:
            print text
        try:
            if request:
                fo.write('%s--> %s%s' % (cr, request.url, cr))
            fo.write(text)
            fo.write(cr)
        except Exception, error:
            pass
    fo.close()

def print_exception():
    print_to(errorlog, '>>> %s:%s' % (datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
    traceback.print_exc(file=open(errorlog, 'a'))

def print_action(action, module):
    if IsDeepDebug:
        print ''
    if IsDebug or IsDeepDebug:
        print '$$$ %s: %s' % (module, action)

def setup_console(sys_enc=default_unicode):
    global ansi
    reload(sys)
    
    try:
        if sys.platform.startswith("win"):
            import ctypes
            enc = "cp%d" % ctypes.windll.kernel32.GetOEMCP()
        else:
            enc = (sys.stdout.encoding if sys.stdout.isatty() else
                        sys.stderr.encoding if sys.stderr.isatty() else
                            sys.getfilesystemencoding() or sys_enc)

        sys.setdefaultencoding(sys_enc)

        if sys.stdout.isatty() and sys.stdout.encoding != enc:
            sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')

        if sys.stderr.isatty() and sys.stderr.encoding != enc:
            sys.stderr = codecs.getwriter(enc)(sys.stderr, 'replace')
    except:
        pass

def demo(x=None, request=None):
    pass

def get_domain(url):
    try:
        import re
        _re_domain = re.compile(r'^(http[s]?)://(.*)\.(.*)\.(ru|com|cz)[/]?$')
        m = url and _re_domain.search(url)
        return m and m.groups()
    except:
        return None

def setReference(url, debug=None):
    global BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL
    host = get_domain(url)
    test = ''

    if IsDemo:
        if DOMAINS.get('demo'):
            protocol = 'http'
            reference = ''
            test = ''
            domain = DOMAINS['demo']
        else:
            protocol = 'https'
            reference = not debug and ('%s/' % default_reference) or ''
            test = 'test'
            domain = DOMAINS['ru']
    else:
        if host and len(host) > 3:
            protocol = host[0]
            reference = '%s/' % default_reference
            domain = DOMAINS[host[3]] or DOMAINS['default']
        else:
            protocol = 'http'
            reference = ''
            domain = DOMAINS['default']

        if debug:
            test = domain != DOMAINS['default'] and 'test' or ''
            reference = ''

    x = {'domain':domain, 'test':test, 'protocol':protocol, 'reference':reference}

    HELPER_URL = HELPER_URL % x
    BASE_URL = BASE_URL % x
    BASE_PATH = BASE_PATH % x
    REFERENCE_PATH = REFERENCE_PATH % x

def getReference():
    return (BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL,)

#   -------------
#   Default types
#   -------------

DEFAULT_LOG_MODE = 1
DEFAULT_PER_PAGE = 10

# action types
valid_action_types = ('100','203','204','205','206','207','208','209','210','301','302','303','304','305','307','308',)

# exchange parameter types
TYPE_BOOLEAN = 0
TYPE_NUMBER = 1
TYPE_STRING = 2

valid_parameter_types = (TYPE_BOOLEAN, TYPE_NUMBER, TYPE_STRING,)

valid_parameter_names = { \
    'BOOLEAN' : TYPE_BOOLEAN, 
    'NUMBER'  : TYPE_NUMBER, 
    'STRING'  : TYPE_STRING,
}

# order types
ORDER_STANDARD = 0
ORDER_CUSTOM = 1
ORDER_DONE = 2

valid_order_names = { \
    ORDER_STANDARD : 'Standard Calculation',
    ORDER_CUSTOM   : 'Custom Calculation',
    ORDER_DONE     : 'Custom Order',
}

valid_order_types = sorted(valid_order_names.keys())

# ratings mnomonics
RATING_UNDEFINED = 'N'
RATING_UP = 'U'
RATING_EQUAL = 'E'
RATING_DOWN = 'D'

valid_rating_names = {
    RATING_UNDEFINED : 'Undefined',
    RATING_UP        : 'Up',
    RATING_EQUAL     : 'Equal',
    RATING_DOWN      : 'Down',
}

DEFAULT_RATING = 'N'

default_rating_types = sorted(valid_rating_names.keys())

# available languages
LANGUAGES = {
    'eng': ('en', 'English',),
    'rus': ('ru', 'Русский',),
    'cze': ('cs', 'Čeština',),
    'pol': ('pl', 'Polski',),
    'deu': ('de', 'Deutsch',),
    'lat': ('lt', 'Latvijas',),
    'fin': ('fi', 'Suomalainen',),
    'chi': ('zh', '中忟蟢',),
}

DEFAUL_LANGUAGE = 'ru'

default_language_types = sorted(LANGUAGES.keys())

CURRENCIES = {
    '008' : 'ALL', 
    '974' : 'BYR', 
    '124' : 'CAD', 
    '156' : 'CNY', 
    '203' : 'CZK', 
    '978' : 'EUR',
    '348' : 'HUF', 
    '392' : 'JPY', 
    '398' : 'KZT', 
    '985' : 'PLN',
    '840' : 'USD',
    '980' : 'UAH',
    '643' : 'RUR',
}

DEFAULT_CURRENCY = 'USD'

default_currency_types = sorted(CURRENCIES.keys())

default_currency_names = [CURRENCIES[x] for x in default_currency_types]

CURRENCY_RATES = {
    'ALL' : 1.0, 
    'BYR' : 1.0, 
    'CAD' : 1.0, 
    'CNY' : 1.0, 
    'CZK' : 1.0, 
    'EUR' : 1.0/0.8, 
    'HUF' : 1.0, 
    'JPY' : 1.0, 
    'KZT' : 1.0, 
    'PLN' : 1.0, 
    'USD' : 1.0, 
    'UAH' : 1.0/25, 
    'RUR' : 1.0/52,
}

DEFAULT_COUNTRY = 'RU'

COUNTRIES = {
    'AD' : 'АНДОРРА',
    'AE' : 'ОБЪЕДИНЕННЫЕ АРАБСКИЕ ЭМИРАТЫ',
    'AF' : 'АФГАНИСТАН',
    'AG' : 'АНТИГУА И БАРБУДА',
    'AI' : 'АНГИЛЬЯ',
    'AL' : 'АЛБАНИЯ',
    'AM' : 'АРМЕНИЯ',
    'AN' : 'НИДЕРЛАНДСКИЕ АНТИЛЫ',
    'AO' : 'АНГОЛА',
    'AQ' : 'АНТАРКТИДА',
    'AR' : 'АРГЕНТИНА',
    'AS' : 'АМЕРИКАНСКОЕ САМОА',
    'AT' : 'АВСТРИЯ',
    'AU' : 'АВСТРАЛИЯ',
    'AW' : 'АРУБА',
    'AZ' : 'АЗЕРБАЙДЖАН',
    'BA' : 'БОСНИЯ И ГЕРЦЕГОВИНА',
    'BB' : 'БАРБАДОС',
    'BD' : 'БАНГЛАДЕШ',
    'BE' : 'БЕЛЬГИЯ',
    'BF' : 'БУРКИНА-ФАСО',
    'BG' : 'Bulgaria',
    'BH' : 'БАХРЕЙН',
    'BI' : 'БУРУНДИ',
    'BJ' : 'БЕНИН',
    'BM' : 'БЕРМУДЫ',
    'BN' : 'БРУНЕЙ-ДАРУССАЛАМ',
    'BO' : 'БОЛИВИЯ',
    'BR' : 'БРАЗИЛИЯ',
    'BS' : 'БАГАМЫ',
    'BT' : 'БУТАН',
    'BV' : 'ОСТРОВ БУВЕ',
    'BW' : 'БОТСВАНА',
    'BY' : 'БЕЛАРУСЬ',
    'BZ' : 'БЕЛИЗ',
    'CA' : 'КАНАДА',
    'CC' : 'КОКОСОВЫЕ (КИЛИНГ) ОСТРОВА',
    'CD' : 'КОНГО, ДЕМОКРАТИЧЕСКАЯ РЕСПУБЛИКА',
    'CF' : 'ЦЕНТРАЛЬНО-АФРИКАНСКАЯ РЕСПУБЛИКА',
    'CG' : 'КОНГО',
    'CH' : 'ШВЕЙЦАРИЯ',
    'CI' : 'КОТ Д\'ИВУАР',
    'CK' : 'ОСТРОВА КУКА',
    'CL' : 'ЧИЛИ',
    'CM' : 'КАМЕРУН',
    'CN' : 'КИТАЙ',
    'CO' : 'КОЛУМБИЯ',
    'CR' : 'КОСТА-РИКА',
    'CU' : 'КУБА',
    'CV' : 'КАБО-ВЕРДЕ',
    'CX' : 'ОСТРОВ РОЖДЕСТВА',
    'CY' : 'КИПР',
    'CZ' : 'Czech Republic',
    'DE' : 'Germany',
    'DJ' : 'ДЖИБУТИ',
    'DK' : 'Denmark',
    'DM' : 'ДОМИНИКА',
    'DO' : 'ДОМИНИКАНСКАЯ РЕСПУБЛИКА',
    'DZ' : 'АЛЖИР',
    'EC' : 'ЭКВАДОР',
    'EE' : 'ЭСТОНИЯ',
    'EG' : 'ЕГИПЕТ',
    'EH' : 'ЗАПАДНАЯ САХАРА',
    'ER' : 'ЭРИТРЕЯ',
    'ES' : 'Spain',
    'ET' : 'ЭФИОПИЯ',
    'FI' : 'Suomi',
    'FJ' : 'ФИДЖИ',
    'FK' : 'ФОЛКЛЕНДСКИЕ ОСТРОВА (МАЛЬВИНСКИЕ)',
    'FM' : 'МИКРОНЕЗИЯ, ФЕДЕРАТИВНЫЕ ШТАТЫ',
    'FO' : 'ФАРЕРСКИЕ ОСТРОВА',
    'FR' : 'France',
    'GA' : 'ГАБОН',
    'GB' : 'United Kingdom',
    'GD' : 'ГРЕНАДА',
    'GE' : 'ГРУЗИЯ',
    'GF' : 'ФРАНЦУЗСКАЯ ГВИАНА',
    'GG' : 'ГЕРНСИ',
    'GH' : 'ГАНА',
    'GI' : 'ГИБРАЛТАР',
    'GL' : 'ГРЕНЛАНДИЯ',
    'GM' : 'ГАМБИЯ',
    'GN' : 'ГВИНЕЯ',
    'GP' : 'ГВАДЕЛУПА',
    'GQ' : 'ЭКВАТОРИАЛЬНАЯ ГВИНЕЯ',
    'GR' : 'ГРЕЦИЯ',
    'GS' : 'ЮЖНАЯ ДЖОРДЖИЯ И ЮЖНЫЕ САНДВИЧЕВЫ ОСТРОВА',
    'GT' : 'ГВАТЕМАЛА',
    'GU' : 'ГУАМ',
    'GW' : 'ГВИНЕЯ-БИСАУ',
    'GY' : 'ГАЙАНА',
    'HK' : 'ГОНКОНГ',
    'HM' : 'ОСТРОВ ХЕРД И ОСТРОВА МАКДОНАЛЬД',
    'HN' : 'ГОНДУРАС',
    'HR' : 'ХОРВАТИЯ',
    'HT' : 'ГАИТИ',
    'HU' : 'Hungary',
    'ID' : 'ИНДОНЕЗИЯ',
    'IE' : 'ИРЛАНДИЯ',
    'IL' : 'ИЗРАИЛЬ',
    'IM' : 'ОСТРОВ МЭН',
    'IN' : 'ИНДИЯ',
    'IO' : 'БРИТАНСКАЯ ТЕРРИТОРИЯ В ИНДИЙСКОМ ОКЕАНЕ',
    'IQ' : 'ИРАК',
    'IR' : 'ИРАН, ИСЛАМСКАЯ РЕСПУБЛИКА',
    'IS' : 'ИСЛАНДИЯ',
    'IT' : 'Italy',
    'JE' : 'ДЖЕРСИ',
    'JM' : 'ЯМАЙКА',
    'JO' : 'ИОРДАНИЯ',
    'JP' : 'ЯПОНИЯ',
    'KE' : 'КЕНИЯ',
    'KG' : 'КИРГИЗИЯ',
    'KH' : 'КАМБОДЖА',
    'KI' : 'КИРИБАТИ',
    'KM' : 'КОМОРЫ',
    'KN' : 'СЕНТ-КИТС И НЕВИС',
    'KP' : 'КОРЕЯ, НАРОДНО-ДЕМОКРАТИЧЕСКАЯ РЕСПУБЛИКА',
    'KR' : 'КОРЕЯ, РЕСПУБЛИКА',
    'KW' : 'КУВЕЙТ',
    'KY' : 'ОСТРОВА КАЙМАН',
    'KZ' : 'КАЗАХСТАН',
    'LA' : 'ЛАОССКАЯ НАРОДНО-ДЕМОКРАТИЧЕСКАЯ РЕСПУБЛИКА',
    'LB' : 'ЛИВАН',
    'LC' : 'СЕНТ-ЛЮСИЯ',
    'LI' : 'ЛИХТЕНШТЕЙН',
    'LK' : 'ШРИ-ЛАНКА',
    'LR' : 'ЛИБЕРИЯ',
    'LS' : 'ЛЕСОТО',
    'LT' : 'Lietuva',
    'LU' : 'ЛЮКСЕМБУРГ',
    'LV' : 'Latvija',
    'LY' : 'ЛИВИЙСКАЯ АРАБСКАЯ ДЖАМАХИРИЯ',
    'MA' : 'МАРОККО',
    'MC' : 'МОНАКО',
    'MD' : 'МОЛДОВА, РЕСПУБЛИКА',
    'ME' : 'ЧЕРНОГОРИЯ',
    'MG' : 'МАДАГАСКАР',
    'MH' : 'МАРШАЛЛОВЫ ОСТРОВА',
    'MK' : 'РЕСПУБЛИКА МАКЕДОНИЯ',
    'ML' : 'МАЛИ',
    'MM' : 'МЬЯНМА',
    'MN' : 'МОНГОЛИЯ',
    'MO' : 'МАКАО',
    'MP' : 'СЕВЕРНЫЕ МАРИАНСКИЕ ОСТРОВА',
    'MQ' : 'МАРТИНИКА',
    'MR' : 'МАВРИТАНИЯ',
    'MS' : 'МОНТСЕРРАТ',
    'MT' : 'МАЛЬТА',
    'MU' : 'МАВРИКИЙ',
    'MV' : 'МАЛЬДИВЫ',
    'MW' : 'МАЛАВИ',
    'MX' : 'МЕКСИКА',
    'MY' : 'МАЛАЙЗИЯ',
    'MZ' : 'МОЗАМБИК',
    'NA' : 'НАМИБИЯ',
    'NC' : 'НОВАЯ КАЛЕДОНИЯ',
    'NE' : 'НИГЕР',
    'NF' : 'ОСТРОВ НОРФОЛК',
    'NG' : 'НИГЕРИЯ',
    'NI' : 'НИКАРАГУА',
    'NL' : 'Netherlands',
    'NO' : 'Norway',
    'NP' : 'НЕПАЛ',
    'NR' : 'НАУРУ',
    'NU' : 'НИУЭ',
    'NZ' : 'НОВАЯ ЗЕЛАНДИЯ',
    'OM' : 'ОМАН',
    'PA' : 'ПАНАМА',
    'PE' : 'ПЕРУ',
    'PF' : 'ФРАНЦУЗСКАЯ ПОЛИНЕЗИЯ',
    'PG' : 'ПАПУА-НОВАЯ ГВИНЕЯ',
    'PH' : 'ФИЛИППИНЫ',
    'PK' : 'ПАКИСТАН',
    'PL' : 'Poland',
    'PM' : 'СЕН-ПЬЕР И МИКЕЛОН',
    'PN' : 'ПИТКЕРН',
    'PR' : 'ПУЭРТО-РИКО',
    'PS' : 'ПАЛЕСТИНСКАЯ ТЕРРИТОРИЯ, ОККУПИРОВАННАЯ',
    'PT' : 'ПОРТУГАЛИЯ',
    'PW' : 'ПАЛАУ',
    'PY' : 'ПАРАГВАЙ',
    'QA' : 'КАТАР',
    'RE' : 'РЕЮНЬОН',
    'RO' : 'РУМЫНИЯ',
    'RS' : 'Serbian',
    'RU' : 'РОССИЯ',
    'RW' : 'РУАНДА',
    'SA' : 'САУДОВСКАЯ АРАВИЯ',
    'SB' : 'СОЛОМОНОВЫ ОСТРОВА',
    'SC' : 'СЕЙШЕЛЫ',
    'SD' : 'СУДАН',
    'SE' : 'Swedish',
    'SG' : 'СИНГАПУР',
    'SH' : 'СВЯТАЯ ЕЛЕНА',
    'SI' : 'СЛОВЕНИЯ',
    'SJ' : 'ШПИЦБЕРГЕН И ЯН МАЙЕН',
    'SK' : 'СЛОВАКИЯ',
    'SL' : 'СЬЕРРА-ЛЕОНЕ',
    'SM' : 'САН-МАРИНО',
    'SN' : 'СЕНЕГАЛ',
    'SO' : 'СОМАЛИ',
    'SR' : 'СУРИНАМ',
    'ST' : 'САН-ТОМЕ И ПРИНСИПИ',
    'SV' : 'ЭЛЬ-САЛЬВАДОР',
    'SY' : 'СИРИЙСКАЯ АРАБСКАЯ РЕСПУБЛИКА',
    'SZ' : 'СВАЗИЛЕНД',
    'TC' : 'ОСТРОВА ТЕРКС И КАЙКОС',
    'TD' : 'ЧАД',
    'TF' : 'ФРАНЦУЗСКИЕ ЮЖНЫЕ ТЕРРИТОРИИ',
    'TG' : 'ТОГО',
    'TH' : 'ТАИЛАНД',
    'TJ' : 'ТАДЖИКИСТАН',
    'TK' : 'ТОКЕЛАУ',
    'TL' : 'ТИМОР-ЛЕСТЕ',
    'TM' : 'ТУРКМЕНИЯ',
    'TN' : 'ТУНИС',
    'TO' : 'ТОНГА',
    'TR' : 'ТУРЦИЯ',
    'TT' : 'ТРИНИДАД И ТОБАГО',
    'TV' : 'ТУВАЛУ',
    'TW' : 'ТАЙВАНЬ (КИТАЙ)',
    'TZ' : 'ТАНЗАНИЯ, ОБЪЕДИНЕННАЯ РЕСПУБЛИКА',
    'UA' : 'УКРАИНА',
    'UG' : 'УГАНДА',
    'UM' : 'МАЛЫЕ ТИХООКЕАНСКИЕ ОТДАЛЕННЫЕ ОСТРОВА СОЕДИНЕННЫХ ШТАТОВ',
    'US' : 'U.S.A.',
    'UY' : 'УРУГВАЙ',
    'UZ' : 'УЗБЕКИСТАН',
    'VA' : 'ПАПСКИЙ ПРЕСТОЛ (ГОСУДАРСТВО - ГОРОД ВАТИКАН)',
    'VC' : 'СЕНТ-ВИНСЕНТ И ГРЕНАДИНЫ',
    'VE' : 'ВЕНЕСУЭЛА',
    'VG' : 'ВИРГИНСКИЕ ОСТРОВА, БРИТАНСКИЕ',
    'VI' : 'ВИРГИНСКИЕ ОСТРОВА, США',
    'VN' : 'ВЬЕТНАМ',
    'VU' : 'ВАНУАТУ',
    'WF' : 'УОЛЛИС И ФУТУНА',
    'WS' : 'САМОА',
    'YE' : 'ЙЕМЕН',
    'YT' : 'МАЙОТТА',
    'ZA' : 'ЮЖНАЯ АФРИКА',
    'ZM' : 'ЗАМБИЯ',
    'ZW' : 'ЗИМБАБВЕ',
}

default_country_types = sorted(('RU', 'EN', 'CZ', 'DE', 'FI', 'KZ', 'BY', 'UA', 'TJ', 'TM', 'UZ',))
    
REGIONS = {
    '000000001' : 'Москва',
}

default_region_types = sorted(REGIONS.keys())
