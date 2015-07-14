# -*- coding: utf-8 -*-

import sys
import os
import datetime
import urllib2
import xml.dom.minidom
import codecs
import re

from types import UnicodeType, DictType, ListType, TupleType, StringType, IntType, LongType, FloatType, BooleanType
from string import strip, upper, lower

from config import basedir, IsConfiguratorsAbsolute, IsDebug, IsDeepDebug, default_encoding, default_unicode, default_path, getReference, errorlog

BASE_URL = BASE_PATH = REFERENCE_PATH = HELPER_URL = ''

list_types = (ListType, TupleType,)
string_types = (UnicodeType, StringType,)

EOI = ',\n'
EOL = '\n'

_agent = None

def set_platform(agent=None):
    global _agent
    if agent:
        _agent = agent

def IsAndroid():
    return _agent.platform == 'android'
def IsiOS():
    return _agent.platform == 'ios'
def IsiPad():
    return _agent.platform == 'ipad'
def IsLinux():
    return _agent.platform == 'linux'

def IsChrome():
    return _agent.browser == 'chrome'
def IsFirefox():
    return _agent.browser == 'firefox'
def IsSafari():
    return _agent.browser == 'safari'
def IsOpera():
    return _agent.browser == 'opera' or 'OPR' in _agent.string

def IsIE(version=None):
    ie = _agent.browser in ('explorer', 'msie',)
    if not ie:
        return False
    elif version:
        return float(_agent.version) == version
    return float(_agent.version) < 10
def IsSeaMonkey():
    return _agent.browser == 'seamonkey'
def IsMSIE():
    return _agent.browser in ('explorer', 'ie', 'msie', 'seamonkey',)

def IsMobile():
    return IsAndroid() or IsiOS() or IsiPad()
def IsNotBootStrap():
    return IsIE(10) or IsAndroid()
def IsWebKit():
    return IsChrome() or IsFirefox() or IsOpera() or IsSafari()

def BrowserVersion():
    return _agent.version

_keywords = {}
_reference_units = {}

MAX_TITLE_LENGTH = 50

LOCALES = ('rus', 'eng', 'cze', 'chi', 'pol', 'deu', 'fin', 'lat',)

##  ======================================
##  Objects XML Loader and Class Generator
##  ======================================

TAG_ATTRS = ('class', 'id', 'name', 'min', 'max', 'step', 'size', 'style', 'script', 'extra', 'content', 'value', 'selected', 'title', 'title',)

# ----------------------
#   Шаблоны HTML-тегов
# ----------------------

TAG_TEMPLATES = \
{
    'page'          : 'section class="%(class)s" id="data-section"',
    'group'         : 'div class="%(class)s" id="group$%(id)s"',
    'caption'       : 'h3>%(content)s</h3',
    'fieldset'      : 'fieldset class="aligned" id="%(id)s"',
    'field'         : '',
    'br'            : 'br',
    'calc'          : 'span class="calculator" id="%(id)s__calc">&nbsp;</span',
    'combo'         : 'select class="field %(class)s" id="%(id)s" name="%(name)s" multiple size="5" %(style)s',
    'content'       : '%(content)s',
    'content-div'   : 'div>%(content)s</div',
    'content-span'  : 'span>%(content)s</span',
    'checkbox'      : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="checkbox" value="%(value)s" %(style)s%(extra)s><span></span',
    'div'           : 'div>%(content)s</div',
    'hidden'        : 'input id="%(id)s" type="hidden" value="%(value)s" %(extra)s',
    'img'           : 'img class="%(class)s" id="%(id)s" src="%(value)s"',
    'label'         : 'label class="%(class)s" for="%(id)s"',
    'list'          : '',
    'number'        : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="number" value="%(value)s" min="%(min)s" max="%(max)s" step="%(step)s" %(style)s%(extra)s',
    'nobr'          : 'nobr',
    'option'        : 'option value="%(value)s%(selected)s">%(content)s</option',
    'radiobutton'   : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="radio" value="%(value)s" %(selected)s %(style)s%(extra)s><span></span',
    'ral-color'     : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="number" value="%(value)s" min="%(min)s" max="%(max)s" step="%(step)s" %(script)s %(style)s%(extra)s><div class="ral-box" id="%(id)s_box"></div',
    'ral-color-calc': 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="number" value="%(value)s" min="%(min)s" max="%(max)s" step="%(step)s" %(script)s %(style)s%(extra)s><span class="calculator" id="%(id)s__calc">&nbsp;</span><div class="ral-box" id="%(id)s_box"></div',
    'range-10'      : 'input class="range-10" id="%(id)s_range" type="range" min="0" max="100" step="25" value="50" %(script)s><div class="range-box" id="%(id)s_box">50</div',
    'select'        : 'select class="field %(class)s" id="%(id)s" name="%(name)s" %(style)s%(extra)s',
    'slider'        : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="range" min="%(min)s" max="%(max)s" step="%(step)s" %(style)s%(extra)s',
    'span'          : 'span',
    'p'             : 'p>%(content)s</p',
    'spinbox'       : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="number" min="%(min)s" max="%(max)s" %(style)s%(extra)s',
    'string'        : 'input class="field %(class)s" id="%(id)s" name="%(name)s" type="text" value="%(value)s" %(style)s%(extra)s',
    'subtitle'      : 'div class="subtitle" id="%(id)s" %(style)s>%(content)s</div',
    'subvalue'      : 'div class="subvalue" id="%(id)s" %(style)s>%(content)s</div',
    'table'         : 'table class="container" border="0"',
    'tr'            : 'tr',
    'td'            : 'td',
    'textarea'      : 'textarea class="field %(class)s" id="%(id)s" name="%(name)s"',
    'title'         : 'label id="%(id)s_title" %(style)s>%(content)s</label', # for="%(id)s"
    'title-div'     : 'div class="label-%(class)s" id="%(id)s_title">%(content)s</div',
    'title-label'   : 'label for="%(id)s">%(content)s</label',
    'endcombo'      : '/select',
    'enddiv'        : '/div',
    'endgroup'      : '/div',
    'endfieldset'   : '/fieldset',
    'endlabel'      : '/label',
    'endnobr'       : '/nobr',
    'endoption'     : '/option',
    'endpage'       : '/section',
    'endselect'     : '/select',
    'endspan'       : '/span',
    'endtable'      : '/table',
    'endtextarea'   : '/textarea',
    'endtd'         : '/td',
    'endtr'         : '/tr',
}

# -------------------------------
#   Разделители списковых полей
# -------------------------------

LST_INDEX_DELIMETER = '##'
LST_VALUE_DELIMETER = ';'
LST_ITEM_DELIMETER  = '|'

# -------------------------------
#   Разделители форматирования
# -------------------------------

SPLITTER = '_'
FORMAT_SPLITTER = '::'

# --------------------
#   Шаблоны скриптов
# --------------------

SCRIPT_DECLARATIONS = """
<script type="text/javascript">
// Model CIS & Descriptions
// ------------------------
var cis = {
%(cis)s
};
var promptings = {
%(promptings)s
};

// Localized constants
// -------------------
%(constants)s

// Prompting images
// ----------------
var illustrations = {
%(illustrations)s
};

// Construction Fields Restrictions
// --------------------------------
var constructs = {
%(constructs)s
};

$ral_objects = {
%(colors)s
};
</script> 
"""

# -----------------------
#   Тип атрибута обмена
# -----------------------

TYPE_CONSTRUCT = 'CONSTRUCT'
TYPE_PROGRESS  = 'PROGRESS'
TYPE_PRODUCT   = 'PRODUCT'
TYPE_PARAMETER = 'PARAMETER'

##  ================
##  Helper Functions
##  ================

def _isNaN(value):
    try:
        return int(value) and False
    except:
        return True

def _parseHTMLStyle(style):
    s = style and style.strip() or ''
    if not s:
        return ''
    s = re.sub(r'fontSize:([\d]+)', r'font-size:\1px', s)
    s = re.sub('fontFamily', 'font-family', s)
    s = re.sub('fontStyle', 'font-style', s)
    s = re.sub('fontWeight', 'font-weight', s)
    s = re.sub('paddingTop', 'padding-top', s)
    s = re.sub('paddingLeft', 'padding-left', s)
    s = re.sub('paddingRight', 'padding-right', s)
    s = re.sub('paddingBottom', 'padding-bottom', s)
    if not s.endswith(';'):
        s += ';'
    return s

def _getSplittedName(id, last_index=0):
    if not SPLITTER in id:
        return id
    words = id.split(SPLITTER)
    if last_index >= 0 and last_index < len(words):
        return words[last_index]
    x = ''
    for i in range(len(words)+last_index):
        if i < 0 or i >= len(words):
            break
        if x:
            x += SPLITTER
        x += words[i]
    return x

def _getTypeOfCISItem(ob):
    if not ob.cis:
        return ''
    elif ob.cis.startswith('construct'):
        return TYPE_CONSTRUCT
    elif ob.kind in ('PROGRESS',):
        return TYPE_PROGRESS
    elif not _isNaN(ob.cis[2:]):
        return TYPE_PRODUCT
    else:
        return TYPE_PARAMETER

def _getCISAttrs(id, ob, form, groups, fields, force=''):
    format = ob.format and ob.format.split(FORMAT_SPLITTER)
    with_unit = False

    title = ''
    unit = ''
    group = ''
    subgroup = ''
    value = ''

    if force == "group":
        #
        # Заголовок группы/раздела
        #
        title = ob.group in groups and groups[ob.group].type == '1' and groups[ob.group].description

    elif force in ("subgroup", "subgroup-only",):
        #
        # Заголовок подгруппы/параметра
        #
        title = ob.subgroup in groups and groups[ob.subgroup].type == '2' and groups[ob.subgroup].description
        if not title and force != "subgroup-only":
            title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "group")

    elif force == "inherited":
        #
        # Поиск однокорневого идентификатора
        #
        key = _getSplittedName(id, -1)
        isUp = id[-3:] == '_up'
        #print 'id:%s, isUp:%s' % (id, isUp)
        start_with = getattr(ob, 'form_position', len(form))-1
        no_content = False
        l = len(key)

        for i in range(start_with, -1, -1):
            xid, xob = form[i]

            if title:
                if title[-1] == ':':
                    title = title[:-1]
                break

            if xob.type in ('ALERT', 'PICTURE',):
                continue

            if xid == key or xid.startswith(key): # and xid[l] not in ('_',)
                #print 'xid:%s' % xid
                no_content = xob.kind in ('POP-UP MENU', 'COMBOBOX',)
                if isUp:
                    if xob.kind == 'DISPLAY FIELD':
                        title = xob.type == 'STRING' and (xob.get_label() or xob.get_title()) or ''
                    elif xob.kind in ('POP-UP MENU', 'COMBOBOX', 'INPUT FIELD', 'CHECKBOX',):
                        title = xob.get_label()
                        #print 'label:[%s]' % title
                elif xob.kind != ob.kind:
                    title = xob.get_label() or not no_content and xob.get_value() or ''
                    #print '3: [%s]' % title

                if not type(title) in string_types or not title or (title and not title[0].isalnum()):
                    title = ''
                elif xob.unit:
                    unit = xob.unit
            #else:
            #    break
    else:
        if _getTypeOfCISItem(ob) == TYPE_PROGRESS:
            title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "subgroup")
            if not title:
                title = '[%s]' % ob.cis

        elif ob.kind in ('POP-UP MENU', 'COMBOBOX', 'INPUT AREA', 'RADIOBUTTON',):
            title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "inherited")

        elif ob.kind == 'CHECKBOX':
            title = ob.get_label()

        elif ob.kind in ('CONSTANT', 'INPUT FIELD',):
            title = ob.get_label()
            #print '1: [%s]' % title

            if not title and SPLITTER in ob.id:
                if _getSplittedName(ob.id, 1).lower() == 'count':
                    title = _keywords['Count']
                    with_unit = True
                elif _getSplittedName(ob.id, -1) != id:
                    title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "inherited")
                    #print '2: [%s]' % title
        else:
            title = ob.get_label() or ob.get_value() or ''

        if title and (re.match(r'^\(.*\)$', title.strip()) or format):
            x = title
            if format and 'G' in format:
                title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "group")
                title = '%s %s' % (title, x)
                x = title

            if not format or 'SG' in format:
                title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "subgroup-only")
                title = '%s %s' % (title, x)

        if not title:
            title, unit, group, subgroup, value = _getCISAttrs(id, ob, form, groups, fields, "subgroup")

    if title:
        if ob.type == 'BOOLEAN' and not value:
            if ob.kind == 'CHECKBOX':
                value = _keywords['Yes']
            elif ob.kind == 'RADIOBUTTON':
                value = ob.get_label()

    if (title or with_unit) and not unit and ob.unit:
        unit = ob.unit

    return (title, unit, group, subgroup, value,)

def _removeEOL(value):
    return re.sub(r'\n', r'<br>', value)

def _getListValue(value):
    x = value and value.split(LST_INDEX_DELIMETER)
    values = []
    index = 0
    if x and len(x) > 1:
        index = int(x[0].strip())
        for v in [v.strip() for v in x[1].split(LST_VALUE_DELIMETER)]:
            if not v:
                continue
            values.append(tuple(v.strip().split(LST_ITEM_DELIMETER)))
    return (index, values,)

def _make_min(b):
    b = re.sub(r'\/\/(.*)\n', '', b)
    b = re.sub(r'[\r]+', '', b)
    b = re.sub(r'\t', ' ', b)
    b = re.sub(r'\s+(\{|\}|\'|\"|\=)\s*', r'\1', b)
    #b = re.sub(r'if\s+(\()', r'if\1', b)
    #b = re.sub(r'\;\s+(if|var|else|return|function)', r';\1', b)
    #b = re.sub(r'\,\s+(\'|\")', r',\1', b)
    #b = re.sub(r'\s+(=|\?|:|>=|<=|>|<|\+|\-|\:|\*|\|\||&&|==)\s+', r'\1', b)
    b = re.sub(r'[\n]+', '', b)
    b = re.sub(r'\s+', ' ', b)
    return b

##  ==========================
##  Objects Class Construction
##  ==========================

class HTML(object):
    """
        Представление элемента управления страницы
    """
    def __init__(self): 
        self.default_tag = ''
        self.tags = ()
        #
        # Базовые атрибуты html-тега
        #
        self.html_class = ''
        self.html_name = ''
        self.html_id = ''
        self.html_value = ''
        #
        # Вспомогательные (необязательные) атрибуты html-тега
        #
        self.html_style = ''
        self.html_extra = ''
        #
        # Контент тега
        #
        self.html_content = ''
        self.indent = ''
        self.inline = False

    def is_valid(self):
        return self.default_tag and True or False

    def get_attrs(self):
        #return dict(zip(TAG_ATTRS, filter(None, [getattr(self, 'html_%s' % attr) for attr in TAG_ATTRS if hasattr(self, 'html_%s' % attr)])))
        return dict(zip(TAG_ATTRS, [getattr(self, 'html_%s' % attr, '') for attr in TAG_ATTRS]))

    def get_content(self, tag):
        return ''

    def get_value(self):
        return ''

    def get_style(self):
        return ''

    def get_template(self, tag, safe=None):
        self.html_content = self.get_content(tag)
        template = TAG_TEMPLATES.get(tag)
        if not template:
            return ''
        if tag != 'content':
            x1 = '<'
            x2 = '>'
        else:
            x1 = x2 = ''
        if not safe:
            return '%s%s%s%s%s' % (self.indent, x1, (template % self.get_attrs()).strip(), x2, not self.inline and EOL or '')
        else:
            return '%s%s%s' % (x1, (template % self.get_attrs()).strip(), x2)

    def html(self, tag=None):
        self.html_value = self.get_value()
        self.html_style = self.get_style()
        if tag is None:
            return self.is_valid() and ''.join([self.get_template(tag) for tag in filter(None, self.tags)]) or ''
        elif type(tag) in list_types:
            return ''.join([self.get_template(x) for x in tag]) or ''
        elif tag == 'content':
            return self.default_tag and self.get_template(self.default_tag, True) or ''
        else:
            if tag == 'title' and not self.get_content(tag): # and isinstance(self, DisplayField)
                return '&nbsp;'
            return self.get_template(tag, True)

class Page(HTML):
    """
        Модель страницы
    """
    def __init__(self, config, **kw):
        super(Page, self).__init__()

        self.config        = config                                 # Объект конфигурации модуля
        self.groups        = []                                     # Коллекция групп формы
        self.repository    = ()                                     # Репозитарий формы
        self.descriptions  = {}                                     # Словарь описаний
        self.constants     = None                                   # Группа (раздел) констант
        self.cis           = []                                     # Коллекция объектов обмена
        self.construct     = []                                     # Коллекция объектов контроля параметров комплектации

        self.default_image = 'images/default.jpg'                   # Иллюстрация по умолчанию
        self.browser = 'browser' in kw and kw['browser'] or ''      # Браузер клиента

        # -------- #
        #   HTML   #
        # -------- #
        self.tags = ('page', 'content', 'endpage',)
        #
        # Базовые атрибуты html-тега
        #
        self.html_class = 'pageClass'

    def __iter__(self):
        for i, group in enumerate(self.groups):
            if group.is_valid():
                yield group

    def scripts(self, id=None):
        if not id or id == 'declarations':
            level1 = ' '*4
            promptings = ["%s'%s':'%s'" % (level1, key, self.descriptions[key].get_description()) 
                for key in sorted(self.descriptions.keys()) if 
                    isinstance(self.descriptions[key], Description) and 
                    self.descriptions[key].label and 
                    self.descriptions[key].description
            ]
            illustrations = ["%s'%s':'%s'" % (level1, ob.id, ob.illustration) 
                for group in self 
                    for ob in group
                        if ob.illustration
            ]
            colors = ["%s'%s':%s" % (level1, ob.id, ob.current_value is None and 'null' or ob.get_value()) 
                for group in self 
                    for ob in group
                        if isinstance(ob, ColorInputField)
            ]
            cis = ["%s'%s':{'id':'%s', 'title':'%s', 'unit':'%s', 'code':'%s', 'value':'%s'}" % ( \
                    level1, 
                    ob.id, 
                    ob.cis, 
                    ob.cis_attrs['title'], 
                    ob.cis_attrs['unit'], 
                    ob.cis_attrs['code'],
                    ob.cis_attrs['value'],
                    #ob.cis_attrs['keys'],  #, 'keys':'%s'
                )
                for ob in sorted(self.cis, cmp=lambda x,y: cmp(x.id, y.id))
            ]
            constants = ["var %s = %s;" % (ob.id, _removeEOL(ob.get_html_value()))
                for ob in sorted(self.constants.constants, cmp=lambda x,y: cmp(x.id, y.id))
            ]
            # -------------------------------------
            # Construction Field Items Restrictions
            # -------------------------------------
            ids = set([ob.name.strip() for ob in self.construct if ob.enabled and ob.active(self.config.postfix)])
            obs = {}
            for id in sorted(ids):
                obs[id] = ','.join(["{'value':'%s', 'region':'%s', 'condition':'%s'}" % (
                            ob.value, 
                            ob.region or '', 
                            ob.condition or '',
                        ) for ob in self.construct if ob.enabled and ob.active(self.config.postfix) and ob.name == id]
                )
            constructs = ["%s'%s':[%s]" % (
                    level1, 
                    id, 
                    obs[id],
                )
                for id in ids
            ]
            # ==================            
            x = { \
                'promptings'    : EOI.join(promptings),
                'cis'           : EOI.join(cis),
                'constants'     : EOL.join(constants),
                'illustrations' : EOI.join(illustrations),
                'constructs'    : EOI.join(constructs),
                'colors'        : EOI.join(colors),
            }
            #raise 1
            return _make_min(SCRIPT_DECLARATIONS % x)
        else:
            return ''

    def is_valid(self):
        return self.groups and True or False

    def add(self, group):
        self.groups.append(group)
        if group.id == 'constants-group':
            self.constants = group

    def set_descriptions(self, descriptions):
        self.descriptions = descriptions

    def set_repository(self, repository):
        self.repository = repository

    def set_cis(self, cis):
        self.cis = cis

    def set_construct(self, construct):
        self.construct += construct

    def get_repository(self):
        x = len(self.repository) > 1 and self.repository[1] or {}
        return tuple([x[key] for key in sorted(x.keys()) if x[key].is_valid()])

    def get_base(self):
        return os.path.join(BASE_URL).replace("\\", '/')

    def get_uri(self):
        return { \
            'root' : os.path.join(BASE_URL, default_path+'/').replace("\\", '/'),
            'module' : os.path.join(BASE_URL, self.config.uri).replace("\\", '/'),
        }

    def get_title(self, safe=True):
        name = self.config and self.config.name or ''
        if len(name) > MAX_TITLE_LENGTH:
            words = name.split()
            x = ''
            for i, w in enumerate(words):
                if len(x)+len(w) > MAX_TITLE_LENGTH:
                    words.insert(i, '<br>')
                    break;
                x = '%s%s%s' % (x, x and ' ' or '', w)
            name = ' '.join(words)
        return safe and re.sub(r'(DUS\s?[\-\w]+)', r'<nobr>\1</nobr>', name) or name

    def get_article(self):
        name = self.config and self.config.name or ''
        m = re.search(r'(DUS\s?[\-\w]+)', name)
        if m:
            return m.group(1)
        x = name.split()
        if len(x) > 2:
            return ' '.join(x[-2:])
        else:
            return ''

    def get_image(self):
        return os.path.join(BASE_URL, self.config.uri, self.default_image).replace("\\", '/')

    def get_content(self, tag):
        self.indent = ''
        if tag == 'content':
            self.indent = ' '*2
            return ''.join([group.html() for group in self.groups])
        else:
            return ''

class Group(HTML):
    """
        Группа (раздел) элементов управления
    """
    def __init__(self, id, ob):
        super(Group, self).__init__()

        self.id            = id                                     # ID группы
        self.title         = ob.get_value()                         # Заголовок группы
        self.constants     = []                                     # Константы группы
        self.fields        = []                                     # Поля группы

        # -------- #
        #   HTML   #
        # -------- #
        self.tags = ('group', 'caption', 'fieldset', 'content', 'endfieldset', 'endgroup',)
        #
        # Базовые атрибуты html-тега
        #
        self.html_class = 'groupTitle'
        self.html_id = '%s' % self.id

        self.items =  {}

    def __iter__(self):
        for i, field in enumerate(self.fields):
            if field.is_valid():
                yield field

    def get(self, key):
        return self.items.get(key) or None

    def is_valid(self):
        return self.title and self.fields and True or False

    def add(self, field):
        if not field.is_visible():
            self.constants.append(field)
        else:
            self.fields.append(field)
        if field.id:
            self.items[field.id] = field

    def get_content(self, tag):
        self.indent = ' '*2
        if tag == 'caption':
            self.indent = ' '*4
            return self.title
        elif tag in ('fieldset', 'endfieldset',):
            self.indent = ' '*4
            return ''
        elif tag == 'content':
            self.indent = ' '*6
            return ''.join([field.html() for field in self.fieldset])
        else:
            return ''

class Config(object):
    """
        Объект конфигурации модуля
    """
    def __init__(self, id, value):
        self.id            = id                                     # ID модуля
        self.dus           = value.get('DusCode', None)             # Артикул
        self.uri           = value.get('URI', '')                   # Местоположение в файловой системе
        self.cc            = value.get('Cc', None)                  # Cc-Email
        self.xml_version   = value.get('XMLVersion', '1')           # Версия протокола обмена
        self.name          = value.get('HelperName', None)          # Наименования модуля
        self.currency      = value.get('defaultCurrencyID', '643')  # Код валюты
        self.postfix       = '000'                                  # Цифровой идентификатор модуля (DUS-XXX)

    def set_properties(self, value):
        self.name = value.get('HelperName', '').strip()
        if 'defaultCurrencyID' in value and value['defaultCurrencyID']:
            self.currency = value['defaultCurrencyID']
        m = re.search(r'(DUS-([\-\w]+))', self.dus)
        if m:
            self.postfix = m.group(2)

class Construct(object):
    """
        Объект блока контроля параметров комплектации
    """
    def __init__(self, id, value):
        self.id            = id                                     # ID модуля
        self.name          = value.get('Name', None)                # Наименование параметра (ID)
        self.enabled       = value.get('Enabled', None) == 'On'     # Статус ограничения (доступен/не доступен)
        self.value         = value.get('Value', None)               # Значения
        self.region        = value.get('Region', None)              # Регион
        self.condition     = value.get('Condition', None)           # Условие применения
        self.dus           = value.get('DusCode', None)             # Артикулы изделий

    def active(self, postfix):
        return (not self.dus or postfix in self.dus) and True or False

    def set_properties(self, value):
        self.name = value.get('Name', '').strip()

class Repository(HTML):
    """
        Справочная документация
    """
    def __init__(self, id, value):
        super(Repository, self).__init__()

        self.id            = id                                     # ID группы
        self.image         = value.get('image', None)               # Пиктограмма файла
        self.location      = value.get('location', None)            # Местоположение в файловой системе
        self.description   = value.get('description', None)         # Заголовок группы/подсказка

    def is_valid(self):
        return self.location and True or False

    def set_value(self, value):
        pass

    def get_value(self):
        return self.location

class Title(object):
    """
        Заголовок поля HTML-формы (слева)
    """
    def __init__(self, id, value):
        self.id            = id                                     # ID
        self.type          = value.get('TypeID', None)              # Тип группы
        self.description   = value.get('Description', None)         # Заголовок группы/поля

        self._stop = 0

    def set_value(self, value):
        pass

    def get_value(self):
        if self._stop:
            return None
        self._stop = 1
        return self.description or ''

    def get_description(self):
        return self.description

    def get_title(self):
        return self.description or ''

class Description(object):
    """
        Заголовок поля/подсказка HTML-формы (справа)
    """
    def __init__(self, id, value):
        self.id            = id                                     # ID
        self.label         = value.get('Label', None)               # Заголовок поля
        self.description   = value.get('Description', None)         # Подсказка

        self.current_value = None

    def set_value(self, value, **kw):
        self.current_value = value

    def get_value(self):
        #return self.current_value or self.label or self.description or ''
        if self.current_value is None:
            return ''
        else:
            return self.current_value or self.label or self.description or ''

    def get_label(self):
        return self.label or ''

    def get_description(self):
        return self.description or ''

    def get_title(self):
        return self.current_value or self.label or ''

class ListDataType(object):
    """
        Тип данных для списковых полей
    """
    def __init__(self):
        pass

    def set_list_value(self, value=None, constants=None):
        if not value and constants:
            ob = None
            if self.id.endswith('Material_List'):
                ob = constants.get('listTypeOfMaterial');
            elif self.id.endswith('_List'):
                ob = constants.get('list%s' % self.id.split('_')[0])
            if ob:
                self.current_value = ob.get_value()
                self.values = ob.values
            return
        index, self.values = _getListValue(value)
        self.current_value = {'index':index, 'values':self.values}

    def get_list_value(self):
        value = u'%s%s' % (self.current_value['index'], LST_INDEX_DELIMETER)
        for item in self.values:
            value += u'%s%s' % (LST_ITEM_DELIMETER.join(item), LST_VALUE_DELIMETER)
        return value

    def get_list_ids(self):
        try:
            return self.values and tuple([item[0] for item in self.values]) or []
        except:
            return []

    def get_html_content(self):
        if not self.current_value:
            return ''
        options = []
        for items in [v for v in self.current_value['values']]:
            if len(items) > 1:
                option = TAG_TEMPLATES.get('option') % {'value':items[0], 'content':items[1], 'selected':''}
            elif len(items) > 0:
                option = TAG_TEMPLATES.get('option') % {'content':items[0], 'selected':''}
            options.append('<%s>' % option)

        return EOL.join(options)

    def max_size(self):
        #return self.values and max([len(x[1].encode(default_unicode, 'ignore')) for x in self.values]) or 0
        return self.values and max([len(x[1]) for x in self.values]) or 0

class Field(HTML):
    """
        Абстактный класс описания поля HTML-формы
    """
    def __init__(self, id, value):
        super(Field, self).__init__()

        self.id            = id                                     # ID
        self.cis           = value.get('ID', None)                  # ID обмена
        self.kind          = value.get('Kind', None)                # Разновидность элемента управления
        self.type          = value.get('Type', None)                # Тип данных
        self.group         = value.get('GroupID', None)             # Раздел полей
        self.subgroup      = value.get('SubGroupID', None)          # Подраздел
        self.format        = value.get('Format', None)              # Формат поля
        self.unit          = value.get('UnitID', None)              # Единицы измерения
        self.illustration  = value.get('Illustration', None)        # Иллюстрация (вспомогательное изображение)
        self.style         = value.get('Style', None)               # Стиль оформления
        self.icon          = value.get('Icon', None)                # Пиктограмма

        self.comment       = {}                                     # Комментарий
        self.title         = None                                   # Объект заголовка
        self.description   = None                                   # Объект описания
        self.current_value = None                                   # Значение по умолчанию

        # -------- #
        #   HTML   #
        # -------- #
        self.default_tag = self.type and self.type.lower()
        self.tags = ('title', self.default_tag,)
        #
        # Базовые атрибуты html-тега
        #
        self.html_class = 'field'
        self.html_name = '%s' % self.id
        self.html_id = '%s' % self.id
        self.html_size = ''
        #
        # Стили html-тега
        #
        self.style = _parseHTMLStyle(self.style)

        # --------------- #
        # Атрибуты обмена #
        # --------------- #
        self.cis_attrs = {'title' : '', 'type' : '', 'unit' : '', 'code' : '', 'value':''}

    def __repr__(self):
        return self.id or ''

    def has_title(self):
        return True

    def is_valid(self):
        return self.type and True or False

    def is_visible(self):
        return True

    def is_implemented(self):
        return True

    def set_value(self, value, **kw):
        self.current_value = value

    def get_value(self):
        return self.current_value or ''

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title and self.title.get_value()

    def set_description(self, description):
        self.description = description

    def get_label(self):
        return self.description and self.description.get_label()

    def get_description(self):
        return self.description and self.description.get_description()

    def get_unit(self):
        return self.unit and '(%s)' % _reference_units.get(self.unit) or ''

    def get_style(self):
        return self.style and 'style="%s"' % self.style

    def get_content(self, tag):
        self.indent = ' '*6
        if tag.startswith('title'):
            x = self.get_label() or ''
            unit = self.get_unit()
            if unit:
                x += '%s%s' % (x and ' ' or '', unit)
            return x
        elif tag == self.default_tag:
            return self.get_value() or '' #&nbsp;
        return ''

class InputField(Field):
    """
        Поле для ввода строковых и числовых данных: input type="text|number|data...".
    """
    def __init__(self, id, value):
        super(InputField, self).__init__(id, value)

        self.html_step = 1
        self.html_min = 0
        self.html_max = 0

    def set_value(self, value, **kw):
        self.tags = ['title', self.default_tag]

        if not self.type or self.type == 'STRING':
            self.current_value = value or ''
            self.html_class = 'string'
        elif self.type == 'NUMBER':
            self.current_value = value and value.isdigit() and int(value) or 0
            self.html_class = 'number'
            if self.format:
                x = self.format.split(FORMAT_SPLITTER)
                ln = 1
                if len(x) > 1:
                    ln = int(x[1].split('.')[0])
                    self.html_max = '9'*ln
                    self.html_size = ln
                if IsIE():
                    width = (ln==1 and 8 or ln<3 and 14 or ln<5 and 30 or 8*ln-2)
                elif IsSeaMonkey():
                    width = (ln==1 and 8 or ln<3 and 16 or ln<5 and 32 or 8*ln)
                else:
                    width = (ln==1 and 26 or ln<3 and 16*ln+2 or ln<5 and 12*4 or ln<8 and 12*ln+2 or 10*ln) - \
                        (IsNotBootStrap() and 15 or 0) + (IsWebKit() and 5 or 0)
                self.style += 'width:%spx;' % width
            self.html_min = kw.get('min') or 0
        elif self.type == 'SLIDER':
            self.current_value = value and value.isdigit() and int(value) or 0
            self.html_class = 'slider'
            self.html_min = kw.get('min', 1)
            self.html_max = kw.get('max', 10)
        elif self.type == 'SPINBOX':
            self.current_value = value and value.isdigit() and int(value) or 0
            self.html_class = 'spinbox'
            self.html_min = kw.get('min', 0)
            self.html_max = kw.get('max', 9999)
        else:
            self.type = None

        self.tags.append('br')

    def get_value(self):
        if self.type == 'NUMBER':
            return self.current_value or 0
        elif self.type == 'STRING':
            return self.current_value or ''
        else:
            super(InputField, self).get_value()

    def html(self, tag=None):
        tag_mapping = { \
            'title' : 'title-div', 
        }
        if self.type == 'NUMBER':
            tag_mapping['content'] = ('number', 'calc',)
        return super(InputField, self).html(tag in tag_mapping and tag_mapping[tag] or tag)

class RangedInputField(InputField):
    """
        Счетчик с управляемым шагом (input+slider)
    """
    def __init__(self, id, value):
        super(RangedInputField, self).__init__(id, value)
        self.html_script = 'onchange="rangeStep(\'%s\', this.value);"' % id
        self.html_step = 50

    def is_implemented(self):
        return not IsAndroid() and (IsChrome() or IsSafari() or IsLinux())

    def html(self, tag=None):
        tag_mapping = { \
            'title' : 'title-div', 
            'content' : ('number', 'calc', 'range-10',),
        }
        return super(RangedInputField, self).html(tag in tag_mapping and tag_mapping[tag] or tag)

class ColorInputField(InputField):
    """
        Поле ввода кода RAL (цвет)
    """
    def __init__(self, id, value):
        super(ColorInputField, self).__init__(id, value)
        self.html_script = '%s=%s' % (IsSafari() and not IsMobile() and 'onclick' or 'onchange', '"ralStep(\'%s\', this.value, 0);"' % id)
        self.default_tag = 'ral-color'

    def is_implemented(self):
        if IsIE() and float(BrowserVersion()) < 9:
            return False
        else:
            return True

    def set_value(self, value, **kw):
        super(ColorInputField, self).set_value(value, **kw)
        if not value:
            self.current_value = None
        self.html_min = 0
        self.html_max = 9999
        self.html_step = 1

    def html(self, tag=None):
        tag_mapping = { \
            'title' : 'title-div', 
            'content' : IsFirefox() and ('ral-color-calc',) or ('ral-color',),
        }
        return super(ColorInputField, self).html(tag in tag_mapping and tag_mapping[tag] or tag)

class DisplayField(Field):
    """
        Надпись: p, span, label ...
    """
    def __init__(self, id, value):
        super(DisplayField, self).__init__(id, value)

    def set_value(self, value, **kw):
        self.html_class = 'display'
        self.default_tag = self.unit and 'subvalue' or 'subtitle'
        self.tags = ('title', 'subtitle', 'br',)
        self.current_value = value

    def get_value(self):
        return self.current_value or self.title.get_value() or ''

class InputArea(Field):
    """
        Текст: textarea
    """
    def __init__(self, id, value):
        super(InputArea, self).__init__(id, value)

    def set_value(self, value, **kw):
        self.html_class = 'input-area'
        self.tags = ('textarea', 'endtextarea',)

    def html(self, tag=None):
        tag_mapping = { \
            'title' : 'title-div', 
        }
        return super(InputArea, self).html(tag in tag_mapping and tag_mapping[tag] or None)

class Constant(Field, ListDataType):
    """
        Константа для связи с сервером.
    """
    def __init__(self, id, value):
        super(Constant, self).__init__(id, value)

    def is_visible(self):
        return False

    def set_value(self, value, **kw):
        self.tags = ('hidden',)

        if not self.type or self.type == 'STRING':
            self.current_value = value or ''
            self.html_class = 'constant string'
        elif self.type == 'NUMBER':
            self.current_value = value and value.isdigit() and int(value) or 0
            self.html_class = 'constant number'
        elif self.type == 'BOOLEAN':
            self.current_value = value and value.lower() == 'true' and True or False
            self.html_class = 'constant boolean'
        elif self.type == 'LIST':
            self.set_list_value(value)
            self.html_class = 'constant list'
        else:
            self.type = None

    def get_html_value(self):
        # Locale depended types
        if self.type == 'LIST':
            return "'%s'" % self.get_list_value()
        else:
            return "'%s'" % (self.current_value or '')

class PopUpMenu(Field, ListDataType):
    """
        Перечисление: select.
    """
    def __init__(self, id, value):
        super(PopUpMenu, self).__init__(id, value)

    def set_value(self, value, **kw):
        if not self.type or self.type == 'LIST':
            self.set_list_value(value)
            self.html_class = 'popup'
            self.tags = ('select', 'content', 'endselect',)
        else:
            self.type = None

    def get_content(self, tag):
        if not self.is_valid():
            return ''
        elif tag in ('subtitle',) or tag.startswith('title'):
            return super(PopUpMenu, self).get_content('title')
        elif tag.startswith('content'):
            return self.get_html_content() or ''
        else:
            return ''

    def html(self, tag=None):
        x = self.max_size()
        if tag == 'content' and x and x<50:
            if IsIE():
                l = 6
                width = x==1 and 50 or x<30 and 40+x*l or 50+x*l
                self.style += 'width:%spx;margin-right:%spx;' % (width, 20)
            else:
                l = 6
                self.style += 'width:%spx;' % (x==1 and 50 or x<30 and 60+x*l or 70+x*l)
        tag_mapping = { \
            'title' : 'title-div', 
            'content' : None, 
        }
        return super(PopUpMenu, self).html(tag_mapping[tag])

class RadioButton(Field):
    """
        Радиокнопка: input type="radio"
    """
    def __init__(self, id, value):
        super(RadioButton, self).__init__(id, value)

    def set_value(self, value, **kw):
        self.html_selected = value and value.lower() == 'true' and 'checked' or ''
        self.html_class = 'radio'
        self.html_name = self.subgroup
        self.default_tag = 'radiobutton'
        self.tags = IsIE() and ('nobr', 'radiobutton', 'label', 'content', 'endlabel', 'endnobr',) or \
            ('label', 'radiobutton', 'content-div', 'endlabel',)
        self.inline = True

    def get_content(self, tag):
        if tag in ('subtitle',) or tag.startswith('title'):
            return self.get_title() or '&nbsp;'
        elif tag.startswith('content'):
            return self.get_label() or '&nbsp;'
        else:
            return ''

    def html(self, tag=None):
        tag_mapping = { \
            'radiobutton' : 'radiobutton',
            'title' : 'title-div', 
            'content' : None, 
        }
        return super(RadioButton, self).html(tag_mapping[tag])

class CheckBox(Field):
    """
        Опция: input type="checkbox"
    """
    def __init__(self, id, value):
        super(CheckBox, self).__init__(id, value)

    def set_value(self, value, **kw):
        self.html_selected = value and value.lower() == 'true' and 'checked' or ''
        self.html_class = 'checkbox'
        self.default_tag = 'checkbox'
        self.tags = IsIE() and ('nobr', 'checkbox', 'label', 'content', 'endlabel', 'endnobr',) or \
            ('label', 'checkbox', 'content-div', 'endlabel',)
        self.inline = True

    def get_content(self, tag):
        if tag in ('subtitle',) or tag.startswith('title'):
            return self.get_title() or ''
        elif tag.startswith('content'):
            return self.get_label() or ''
        else:
            return ''

    def html(self, tag=None):
        tag_mapping = { \
            'checkbox' : 'checkbox',
            'title' : 'title-div', 
            'content' : None, 
        }
        return super(CheckBox, self).html(tag_mapping[tag])

class ComboBox(Field, ListDataType):
    """
        Перечисление: select.
    """
    def __init__(self, id, value):
        super(ComboBox, self).__init__(id, value)

    def set_value(self, value, **kw):
        if not self.type or self.type == 'LIST':
            self.set_list_value(value)
            self.html_class = 'combobox'
            self.tags = ('combo', 'content', 'endcombo',)
        else:
            self.type = None

    def get_content(self, tag):
        if not self.is_valid():
            return ''
        elif tag.startswith('content'):
            return self.get_html_content() or ''
        else:
            return self.get_title() or '&nbsp;'

    def html(self, tag=None):
        x = self.max_size()
        if tag == 'content' and x and x<50:
            self.style += 'width:%spx;' % (x==1 and 50 or x<30 and 60+x*6 or 70+x*6)
        tag_mapping = { \
            'title' : 'title-div', 
            'content' : None, 
        }
        return super(ComboBox, self).html(tag_mapping[tag])

class Select(Field, ListDataType):
    """
        Список: multiple select.
    """
    def __init__(self, id, value):
        super(Select, self).__init__(id, value)

    def set_value(self, value, **kw):
        if not self.type or self.type == 'LIST':
            self.set_list_value(value)
            self.html_class = 'select'
            self.html_extra = ' multiple'
            self.tags = ('select', 'content', 'endselect',)
        else:
            self.type = None

    def get_content(self, tag):
        if not self.is_valid():
            return ''
        elif tag.startswith('content'):
            return self.get_html_content() or ''
        else:
            return self.get_title() or '&nbsp;'

    def html(self, tag=None):
        x = self.max_size()
        if tag == 'content' and x and x<50:
            self.style += 'width:%spx;' % (x==1 and 50 or x<30 and 60+x*6 or 70+x*6)
        tag_mapping = { \
            'title' : 'title-div', 
            'content' : None, 
        }
        return super(Select, self).html(tag_mapping[tag])

class Picture(Field):
    """
        Иллюстрация: img
    """
    def __init__(self, id, value):
        super(Picture, self).__init__(id, value)

    def has_title(self):
        return False

    def set_value(self, value, **kw):
        self.html_class = 'picture'
        self.default_tag = 'img'
        self.tags = None
        self.current_value = value

    def get_value(self):
        value = self.current_value or self.description and self.description.get_value()
        return value and os.path.join(BASE_URL, value) or ''

############################################################################################################################

def getXML(url):
    is_close = True
    try:
        f = urllib2.urlopen(url)
        is_close = False
    except:
        if IsConfiguratorsAbsolute:
            f = open(os.path.join(basedir, url))
        else:
            f = open(url)

    data = xml.dom.minidom.parse(f).documentElement

    if is_close: f.close()

    return data

def getItemValue(field):
   return ','.join([getattr(n, 'data', '').strip() for n in field.childNodes])

def getConfigValue(id, node, config=None):
    value = {}
    for field in node.childNodes:
        if field.nodeType == xml.dom.Node.ELEMENT_NODE and field.hasAttributes():
            value[field.getAttribute('name')] = getItemValue(field)

    ob = Config(id, value)

    if config and id in config:
        config[id].set_properties(value)

    return ob

def getConfigNodeValue(id, node):
    value = {}
    for field in node.childNodes:
        if field.nodeType == xml.dom.Node.ELEMENT_NODE and field.hasAttributes():
            value[field.getAttribute('name')] = getItemValue(field)

    ob = None
    if value.has_key('TypeID'):
        ob = Title(id, value)
    elif value.has_key('Description'):
        ob = Description(id, value)
    elif id in ('c0','c1','c2','c3','c4','c5','c6','c7','c8','c9',):
        ob = Repository(id, value)
    elif value.has_key('Kind') or value.has_key('CurrentValue'):
        if not value.has_key('Kind'):
            ob = Constant(id, value)
        elif value['Kind'] == 'INPUT FIELD':
            if value['Type'] == 'NUMBER' and value['Format']:
                x = value['Format'].split(FORMAT_SPLITTER)
                ln = len(x) > 1 and int(x[1].split('.')[0]) or 0
                if ln >= 4:
                    if id.endswith('Color_Value'):
                        ob = ColorInputField(id, value)
                    elif ln >= 6:
                        ob = InputField(id, value)
                    else:
                        ob = RangedInputField(id, value)
            if not ob or not ob.is_implemented():
                ob = InputField(id, value)
        elif value['Kind'] in ('DISPLAY FIELD', 'LABEL',):
            if value['Type'] in ('PICTURE',):
                ob = Picture(id, value)
            else:
                ob = DisplayField(id, value)
        elif value['Kind'] == 'INPUT AREA':
            ob = InputArea(id, value)
        elif value['Kind'] in ('CONSTANT', 'PROGRESS',):
            ob = Constant(id, value)
        elif value['Kind'] == 'POP-UP MENU':
            ob = PopUpMenu(id, value)
        elif value['Kind'] == 'RADIOBUTTON':
            ob = RadioButton(id, value)
        elif value['Kind'] == 'CHECKBOX':
            ob = CheckBox(id, value)
        elif value['Kind'] == 'COMBOBOX':
            ob = ComboBox(id, value)
        elif value['Kind'] == 'SELECT':
            ob = Select(id, value)
        else:
            ob = None
    else:
        ob = Field(id, value)

    if ob:
        ob.set_value(value.get('CurrentValue', None))

    return ob

def getConfig(url, config={}):
    data = getXML(url)
    records = {}

    for node in data.childNodes:
        if node.nodeName == 'configurator' and node.hasAttributes():
            if node.hasAttribute('id'):
                id = node.getAttribute('id')
                records[id] = getConfigValue(id, node, config)

    return records

def getForm(url):
    data = getXML(url)
    records = []

    for node in data.childNodes:
        if node.nodeName == 'record' and node.hasAttributes():
            if node.hasAttribute('id'):
                id = node.getAttribute('id')
                ob = getConfigNodeValue(id, node)
                if ob is not None:
                    records.append((id, ob,))

    return records

def getContent(url):
    data = getXML(url)
    tables = []

    for node in data.childNodes:
        if node.nodeName == 'table' and node.hasAttributes():
            name = node.getAttribute('name')
            table = {}
            for node in node.childNodes:
                if node.nodeName == 'record' and node.hasAttributes():
                    if node.hasAttribute('id'):
                        id = node.getAttribute('id')
                        table[id] = getConfigNodeValue(id, node)

            tables.append((name, table))

    return tables

def getUnits(url):
    data = getXML(url)
    records = {}

    for node in data.childNodes:
        if node.nodeName == 'unit' and node.hasAttributes():
            id = node.getAttribute('numCode')
            records[id] = getItemValue(node).strip()

    return records

def getConstructValue(id, node, construct=None):
    value = {}
    for field in node.childNodes:
        if field.nodeType == xml.dom.Node.ELEMENT_NODE and field.hasAttributes():
            value[field.getAttribute('name')] = getItemValue(field)

    ob = Construct(id, value)

    if construct and id in construct:
        construct[id].set_properties(value)

    return ob

def getConstruct(url, construct={}):
    try:
        data = getXML(url)
    except:
        return None

    records = []

    for node in data.childNodes:
        if node.nodeName == 'construct' and node.hasAttributes():
            if node.hasAttribute('id'):
                id = node.getAttribute('id')
                records.append(getConstructValue(id, node, construct))

    return records

def getPage(wizard, locale, init_only=False, **kw):
    global _agent, _keywords, _reference_units
    global BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL

    BASE_URL, BASE_PATH, REFERENCE_PATH, HELPER_URL = getReference()

    _agent = kw.get('agent')
    _keywords = kw.get('keywords')
    _reference_units = getUnits(os.path.join(REFERENCE_PATH, locale, 'units.xml'))

    config_common = getConfig(os.path.join(BASE_PATH, default_path, 'configurators_comm.xml'))
    config_local = getConfig(os.path.join(BASE_PATH, locale, 'configurators_local.xml'), config_common)

    if wizard not in config_common or not config_common[wizard].name:
        # Модуль не зарегистрирован
        return None

    config = config_common[wizard]
    path = config.uri

    form = getForm(os.path.join(BASE_PATH, path, 'form.xml'))
    repository, groups, descriptions = getContent(os.path.join(BASE_PATH, locale, path, 'content.xml'))

    groups_name, groups = groups
    descriptions_name, descriptions = descriptions

    page = Page(config, browser=_agent.browser)

    #if init_only:
    #    page.set_repository(repository)
    #    return page

    ##print groups.keys()

    current_group = ''
    group = None

    constants = Group('constants-group', 
        Title('constants', {'Description' : 'Constants group', 'TypeID' : '1'})
    )

    for id in descriptions.keys():
        ob = descriptions[id]
        if isinstance(ob, Constant):
            constants.add(ob)

    fields = {}
    cis = []

    for i, (id, ob) in enumerate(form):
        #id, ob = form[i]
        if not ob or not (group or ob.group):
            # Отсутствует объект описания или группа
            continue
        fields[id] = ob
        #
        # Создать группу
        #
        if ob.group != current_group and ob.group in groups and groups[ob.group].type == '1':
            group = Group(ob.group, groups[ob.group])
            page.add(group)
            current_group = ob.group
        #
        # Добавить ссылку на объект заголовка
        #
        if ob.subgroup:
            if ob.subgroup in groups and groups[ob.subgroup].type == '2':
                ob.set_title(groups[ob.subgroup])
        else:
            if id in descriptions:
                ob.set_title(descriptions[id])
        #
        # Добавить ссылку на объект описания (подсказку)
        #
        if id in descriptions:
            ob.set_description(descriptions[id])
        #
        # Контроль списковых полей
        #
        if ob.type == 'LIST':
            ob.set_list_value(None, constants)
        #
        # CIS-элемент
        #
        if hasattr(ob, 'cis') and ob.cis:
            setattr(ob, 'form_position', i)
            cis.append(ob)
        #
        # Добавить элемент в группу
        #
        group.add(ob)

    page.add(constants)
    page.set_repository(repository)
    page.set_descriptions(descriptions)

    unique_titles = []

    for ob in cis:
        title, unit, group, subgroup, value = _getCISAttrs(ob.id, ob, form, groups, fields)
        if type(title) in string_types:
            title = isinstance(title, str) and unicode(title.strip(), default_encoding) or title.strip()
            if ob.kind not in ('CHECKBOX', 'RADIOBUTTON',):
                if title in unique_titles:
                    title = ''

        if title not in unique_titles:
            unique_titles.append(title)

        ob.cis_attrs = { \
            'title':title or _keywords['Value'], 
            'unit':unit and '%s|%s' % (unit, _reference_units.get(unit, '')) or '',
            'group':group, 
            'subgroup':subgroup,
            'code': _getTypeOfCISItem(ob) == TYPE_PRODUCT and ob.cis or '',
            'value':value,
            #'keys':ob.type == 'LIST' and ':'.join(ob.get_list_ids()) or '',
        }

    page.set_cis(cis)

    construct = getConstruct(os.path.join(BASE_PATH, default_path, 'valid-construct.xml'))

    if construct:
        page.set_construct(construct)

    config = config_common[wizard]
    path = config.uri

    construct = getConstruct(os.path.join(BASE_PATH, path, 'local-valid-construct.xml'))

    if construct:
        page.set_construct(construct)

    return page
