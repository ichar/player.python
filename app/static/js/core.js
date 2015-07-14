// ==================================
//  Core javascript helper functions
// ==================================

function is_null(value) { return (value == null) ? true : false; }

function int(value) { return parseInt(value); }

function getattr(ob, id, value) { return (typeof(ob)=='object' && !is_null(ob) && id in ob) ? ob[id] : value; }

function setattr(ob, id, value) { if (typeof(ob)=='object' && !is_null(ob) && id in ob) ob[id] = value; }

// ----------------------------------------
//  Basic browser identification & version
// ----------------------------------------
var BrowserDetect = {
    init: function () {
        this.browser = this.searchString(this.dataBrowser).toLowerCase() || "An unknown browser";
        this.version = this.searchVersion(navigator.userAgent)
            || this.searchVersion(navigator.appVersion)
            || "an unknown version";
        this.OS = this.searchString(this.dataOS) || "an unknown OS";
    },
    searchString: function (data) {
        for (var i=0; i<data.length; i++)    {
            var dataString = data[i].string;
            var dataProp = data[i].prop;
            this.versionSearchString = data[i].versionSearch || data[i].identity;
            if (dataString) {
                if (dataString.indexOf(data[i].subString) != -1)
                    return data[i].identity;
            }
            else if (dataProp)
                return data[i].identity;
        }
    },
    searchVersion: function (dataString) {
        var index = dataString.indexOf(this.versionSearchString);
        if (index == -1) return;
        return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
    },
    dataBrowser: [
        {
            string: navigator.userAgent,
            subString: "YaBrowser",
            identity: "Yandex"
        },
        {
            string: navigator.userAgent,
            subString: "Chrome",
            identity: "Chrome"
        },
        {   
            string: navigator.userAgent,
            subString: "OmniWeb",
            versionSearch: "OmniWeb/",
            identity: "OmniWeb"
        },
        {
            string: navigator.vendor,
            subString: "Apple",
            identity: "Safari",
            versionSearch: "Version"
        },
        {
            prop: window.opera,
            identity: "Opera",
            versionSearch: "Version"
        },
        {
            string: navigator.vendor,
            subString: "iCab",
            identity: "iCab"
        },
        {
            string: navigator.vendor,
            subString: "KDE",
            identity: "Konqueror"
        },
        {
            string: navigator.userAgent,
            subString: "Firefox",
            identity: "Firefox"
        },
        {
            string: navigator.vendor,
            subString: "Camino",
            identity: "Camino"
        },
        {   // for newer Netscapes (6+)
            string: navigator.userAgent,
            subString: "Netscape",
            identity: "Netscape"
        },
        {
            string: navigator.userAgent,
            subString: "MSIE",
            identity: "Explorer",
            versionSearch: "MSIE"
        },
        {
            string: navigator.userAgent,
            subString: "Trident",
            identity: "Explorer",
            versionSearch: "rv"
        },
        {
            string: navigator.userAgent,
            subString: "Gecko",
            identity: "Mozilla",
            versionSearch: "rv"
        },
        {   // for older Netscapes (4-)
            string: navigator.userAgent,
            subString: "Mozilla",
            identity: "Netscape",
            versionSearch: "Mozilla"
        }
    ],
    dataOS : [
        {
            string: navigator.platform,
            subString: "Win",
            identity: "Windows"
        },
        {
            string: navigator.platform,
            subString: "Mac",
            identity: "Mac"
        },
        {
            string: navigator.userAgent,
            subString: "iPhone",
            identity: "iPhone/iPod"
        },
        {
            string: navigator.platform,
            subString: "Linux",
            identity: "Linux"
        }
    ]

};
BrowserDetect.init();

var isYandex = BrowserDetect.browser == 'yandex' ? true : false;
var isChrome = BrowserDetect.browser == 'chrome' ? true : false;
var isFirefox = BrowserDetect.browser == 'firefox' ? true : false;
var isMozilla = BrowserDetect.browser == 'mozilla' ? true : false;
var isSafari = BrowserDetect.browser == 'safari' ? true : false;
var isOpera = BrowserDetect.browser == 'opera' ? true : false;
var isIE = BrowserDetect.browser == 'explorer' ? BrowserDetect.version : 0;

//alert(navigator.userAgent+':'+BrowserDetect.version+':'+isIE.toString());

// ------------------------------
//  Cross-browser event handlers
// ------------------------------
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        return false;
    }
}

function removeEvent(obj, evType, fn) {
    if (obj.removeEventListener) {
        obj.removeEventListener(evType, fn, false);
        return true;
    } else if (obj.detachEvent) {
        obj.detachEvent("on" + evType, fn);
        return true;
    } else {
        return false;
    }
}

// ---------------------------------------------------------------------------------------------
//  quickElement(tagType, parentReference, textInChildNode, [, attribute, attributeValue ...]);
// ---------------------------------------------------------------------------------------------
function quickElement() {
    var obj = document.createElement(arguments[0]);
    if (arguments[2] != '' && arguments[2] != null) {
        var textNode = document.createTextNode(arguments[2]);
        obj.appendChild(textNode);
    }
    var len = arguments.length;
    for (var i = 3; i < len; i += 2) {
        obj.setAttribute(arguments[i], arguments[i+1]);
    }
    arguments[1].appendChild(obj);
    return obj;
}

// --------------------------------------------------------------------------------
//  Cross-browser xmlhttp object from http://jibbering.com/2002/4/httprequest.html
// --------------------------------------------------------------------------------
var xmlhttp;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
    try {
        xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
        try {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (E) {
            xmlhttp = false;
        }
    }
@else
    xmlhttp = false;
@end @*/
if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
  xmlhttp = new XMLHttpRequest();
}

// -------------------------------------------------------------------------------
//  Find-position functions by PPK. See http://www.quirksmode.org/js/findpos.html
// -------------------------------------------------------------------------------
function findPosX(obj) {
    var curleft = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft - ((isOpera) ? 0 : obj.scrollLeft);
            obj = obj.offsetParent;
        }
        // IE offsetParent does not include the top-level 
        if (isIE && obj.parentElement){
            curleft += obj.offsetLeft - obj.scrollLeft;
        }
    } else if (obj.x) {
        curleft += obj.x;
    }
    return curleft;
}

function findPosY(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop - ((isOpera) ? 0 : obj.scrollTop);
            obj = obj.offsetParent;
        }
        // IE offsetParent does not include the top-level 
        if (isIE && obj.parentElement){
            curtop += obj.offsetTop - obj.scrollTop;
        }
    } else if (obj.y) {
        curtop += obj.y;
    }
    return curtop;
}

// ------------------------
//  Date object extensions
// ------------------------
Date.prototype.getCorrectYear = function() {
    // Date.getYear() is unreliable --
    // see http://www.quirksmode.org/js/introdate.html#year
    var y = this.getYear() % 100;
    return (y < 38) ? y + 2000 : y + 1900;
};

Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth()+1) : (this.getMonth()+1);
};

Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
};

Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
};

Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
};

Date.prototype.getTwoDigitSecond = function() {
    return (this.getSeconds() < 10) ? '0' + this.getSeconds() : this.getSeconds();
};

Date.prototype.getISODate = function() {
    return this.getCorrectYear() + '-' + this.getTwoDigitMonth() + '-' + this.getTwoDigitDate();
};

Date.prototype.getHourMinute = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute();
};

Date.prototype.getHourMinuteSecond = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute() + ':' + this.getTwoDigitSecond();
};

// --------------------------
//  String object extensions
// --------------------------
String.prototype.pad_left = function(pad_length, pad_string) {
    var new_string = this;
    for (var i = 0; new_string.length < pad_length; i++) {
        new_string = pad_string + new_string;
    }
    return new_string;
};

String.prototype.startswith = function(s) {
    return (s && this.substr(0, s.length) == s) ? true : false;
};

String.prototype.endswith = function(s) {
    return (s && this.substr(-s.length) == s) ? true : false;
};

function strip(s) {
    return s.replace(/^\s+|\s+$/g, ''); // trim leading/trailing spaces
}

function dumping(ob) {
    var s = '';
    if (typeof(ob) != 'object')
        s = ob.toString();
    else {
        try { 
            for (p in ob) s += p+'['+ob[p].toString()+']:'; 
        }
        catch(e) {}
    }
    return s;
}

var htmlMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': '&quot;',
    "'": '&#39;',
    "/": '&#x2F;'
};

function escapeHtml(string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return htmlMap[s];
    });
}

function cleanTextValue(string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return '';
    });
}

// ----------------------------------------
//  Get the computed style for and element
// ----------------------------------------
function getStyle(oElm, strCssRule) {
    var strValue = "";

    if (document.defaultView && document.defaultView.getComputedStyle) {
        strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
    }
    else if (oElm.currentStyle) {
        strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
            return p1.toUpperCase();
        });
        strValue = oElm.currentStyle[strCssRule];
    }

    return strValue;
}

// -----------------------
//  Hash table prototype
// -----------------------
/*  Usage: var attrs = new Hash(key1, value1, key2, value2, ...);
 *    key   -- name of the attribute, String
 *    value -- any valid data
 *  i.e. list of the argument pairs, can be omitted.
 */
function Hash()
{
    this.length = 0;
    this.items = new Array();
    for (var i = 0; i < arguments.length; i += 2) {
        if (typeof(arguments[i + 1]) != 'undefined') {
            this.items[arguments[i]] = arguments[i + 1];
            this.length++;
        }
    }
   
    this.removeItem = function(key)
    {
        var tmp_previous;
        if (typeof(this.items[key]) != 'undefined') {
            this.length--;
            var tmp_previous = this.items[key];
            delete this.items[key];
        }
        return tmp_previous;
    };

    this.getItem = function(key) {
        return this.items[key];
    };

    this.setItem = function(key, value)
    {
        var tmp_previous;
        if (typeof(value) != 'undefined') {
            if (typeof(this.items[key]) == 'undefined') {
                this.length++;
            }
            else {
                tmp_previous = this.items[key];
            }
            this.items[key] = value;
        }
        return tmp_previous;
    };

    this.hasItem = function(key)
    {
        return typeof(this.items[key]) != 'undefined';
    };

    this.clear = function()
    {
        for (var i in this.items) {
            delete this.items[i];
        }
        this.length = 0;
    };
}

// ------------------------
//  Functions under Arrays
// ------------------------
if (!Array.prototype.indexOf) Array.prototype.indexOf = function(value) {
    for (var i=0; i<this.length; i++) {
        if (this[i] === value) return i;
    }
    return -1;
};

Array.prototype.isEqual = function(arr) {
    if (this.length != arr.length)
        return false;
    for(var i=0; i<this.length; i++) {
        if (this[i] != arr[i])
            return false;
    }
    return true;
};

Array.prototype.makeEqual = function() {
    var value = new Array();
    for(var i=0; i<this.length; i++) {
        value.push(this[i]);
    }
    return value;
};

Array.prototype.remove = function(value) {
    for(var i=0; i<this.length; i++) {
        if (this[i] === value) {
            this.splice(i,1);
            break;
        }
    }
};

// ---------------------
//  Functions under DOM
// ---------------------
function appendImageInside(parent, src, attrs) {
    var area = document.getElementById(parent);
    if (typeof(area) != 'object')
        return;
    var img = document.createElement('img');
    if (typeof(attrs) == 'object' && 'class' in attrs)
        img.className = attrs['class'];
    img.src = src;
    area.appendChild(img);
}

function preloadImages(items, callback) {
    var n = items.length;
    function ok() { 
        --n; 
        if (!n) callback();
    }
    for(var i=0; i < n; i++) {
        if (items[i]) {
            var img = document.createElement('img');
            img.onload = img.onerror = ok;
            img.src = items[i];
        }
        else ok();
    }
}

// Global namespace
// ----------------
var self = window;

var $SCRIPT_ROOT = '';
var $IS_FRAME = true;

var n_a = 'n/a';

// Range Input handler
// -------------------
function rangeStep(id, value) {
    //alert(id+':'+value);
    var x = value <= 0 ? 1 : value;
    //$("#"+id).attr('step', x);
    //$("#"+id+'_box').html(x);
    document.getElementById(id).step = x;
    document.getElementById(id+'_box').innerHTML = x;
}

// RAL Color Input handler
// -----------------------
var $ral_colors_spec = {
    '1000' : ['#d6c794', "Green beige"],
    '1001' : ['#d9ba8c', "Beige"],
    '1002' : ['#d6b075', "Sand yellow"],
    '1003' : ['#fca329', "Signal yellow"],
    '1004' : ['#e39624', "Golden yellow"],
    '1005' : ['#c98721', "Honey yellow"],
    '1006' : ['#e0821f', "Maize yellow"],
    '1007' : ['#e37a1f', "Daffodil yellow"],
    '1011' : ['#ad7a4f', "Brown beige"],
    '1012' : ['#e3b838', "Lemon yellow"],
    '1013' : ['#fff5e3', "Oyster white"],
    '1014' : ['#f0d6ab', "Ivory"],
    '1015' : ['#fcebcc', "Light ivory"],
    '1016' : ['#fff542', "Sulfur yellow"],
    '1017' : ['#ffab59', "Saffron yellow"],
    '1018' : ['#ffd64d', "Zinc yellow"],
    '1019' : ['#a38c7a', "Grey beige"],
    '1020' : ['#9c8f61', "Olive yellow"],
    '1021' : ['#fcbd1f', "Rape yellow"],
    '1023' : ['#fcb821', "Traffic yellow"],
    '1024' : ['#b58c4f', "Ochre yellow"],
    '1026' : ['#ffff0a', "Luminous yellow"],
    '1027' : ['#997521', "Curry"],
    '1028' : ['#ff8c1a', "Melon yellow"],
    '1032' : ['#e3a329', "Broom yellow"],
    '1033' : ['#ff9436', "Dahlia yellow"],
    '1034' : ['#f7995c', "Pastel yellow"],
    '1035' : ['#6a5d4d', "Pearl Beige"],
    '1036' : ['#705335', "Pearl gold"],
    '1037' : ['#f39f18', "Sun yellow"],
    '2000' : ['#e05e1f', "Yellow orange"],
    '2001' : ['#ba2e21', "Red orange"],
    '2002' : ['#cc241c', "Vermilion"],
    '2003' : ['#ff6336', "Pastel orange"],
    '2004' : ['#f23b1c', "Pure orange"],
    '2005' : ['#fc1c14', "Luminous orange"],
    '2007' : ['#ff7521', "Luminous bright orange"],
    '2008' : ['#fa4f29', "Bright red orange"],
    '2009' : ['#eb3b1c', "Traffic orange"],
    '2010' : ['#d44529', "Signal orange"],
    '2011' : ['#ed5c29', "Deep orange"],
    '2012' : ['#de5247', "Salmon orange"],
    '2013' : ['#c35831', "Pearl orange"],
    '2014' : ['#c8a4b0', "Caparol"],
    '3000' : ['#ab1f1c', "Flame red"],
    '3001' : ['#a3171a', "Signal red"],
    '3002' : ['#a31a1a', "Carmine red"],
    '3003' : ['#8a1214', "Ruby red"],
    '3004' : ['#690f14', "Purple red"],
    '3005' : ['#4f121a', "Wine red"],
    '3007' : ['#2e121a', "Black red"],
    '3009' : ['#5e2121', "Oxide red"],
    '3011' : ['#781417', "Brown red"],
    '3012' : ['#cc8273', "Beige red"],
    '3013' : ['#961f1c', "Tomato red"],
    '3014' : ['#d96675', "Antique pink"],
    '3015' : ['#e89cb5', "Light pink"],
    '3016' : ['#a62426', "Coral red"],
    '3017' : ['#d13654', "Rose"],
    '3018' : ['#cf2942', "Strawberry red"],
    '3020' : ['#c71712', "Traffic red"],
    '3022' : ['#d9594f', "Salmon pink"],
    '3024' : ['#fc0a1c', "Luminous red"],
    '3026' : ['#fc1414', "Luminous bright red"],
    '3027' : ['#b51233', "Raspberry red"],
    '3028' : ['#CB3234', "Pure Red"],
    '3031' : ['#a61c2e', "Orient red"],
    '3032' : ['#721422', "Pearl ruby red"],
    '3033' : ['#B44C43', "Pearl pink"],
    '4001' : ['#824080', "Red lilac"],
    '4002' : ['#8f2640', "Red violet"],
    '4003' : ['#c9388c', "Heather violet"],
    '4004' : ['#5c082b', "Claret violet"],
    '4005' : ['#633d9c', "Blue lilac"],
    '4006' : ['#910f66', "Traffic purple"],
    '4007' : ['#380a2e', "Purple violet"],
    '4008' : ['#7d1f7a', "Signal violet"],
    '4009' : ['#9e7394', "Pastel violet"],
    '4010' : ['#bf1773', "Telemagenta"],
    '4011' : ['#8673A1', "Pearl violet"],
    '4012' : ['#6C6874', "Pearl black berry"],
    '5000' : ['#17336b', "Violet blue"],
    '5001' : ['#0a3354', "Green blue"],
    '5002' : ['#000f75', "Ultramarine blue"],
    '5003' : ['#001745', "Sapphire blue"],
    '5004' : ['#030d1f', "Black blue"],
    '5005' : ['#002e7a', "Signal blue"],
    '5007' : ['#264f87', "Brillant blue"],
    '5008' : ['#1a2938', "Gray blue"],
    '5009' : ['#174570', "Azure blue"],
    '5010' : ['#002b70', "Gentian blue"],
    '5011' : ['#03142e', "Steel blue"],
    '5012' : ['#2973b8', "Light blue"],
    '5013' : ['#001245', "Cobalt blue"],
    '5014' : ['#4d6999', "Pigeon blue"],
    '5015' : ['#1761ab', "Sky blue"],
    '5017' : ['#003b80', "Traffic blue"],
    '5018' : ['#389482', "Turquoise blue"],
    '5019' : ['#0a4278', "Capri blue"],
    '5020' : ['#053333', "Ocean blue"],
    '5021' : ['#1a7a63', "Water blue"],
    '5022' : ['#00084f', "Night blue"],
    '5023' : ['#2e528f', "Distant blue"],
    '5024' : ['#578cb5', "Pastel blue"],
    '5025' : ['#2A6478', "Pearl gentian blue"],
    '5026' : ['#102C54', "Pearl night blue"],
    '6000' : ['#337854', "Patina green"],
    '6001' : ['#266629', "Emerald green"],
    '6002' : ['#265721', "Leaf green"],
    '6003' : ['#3d452e', "Olive green"],
    '6004' : ['#0d3b2e', "Blue green"],
    '6005' : ['#0a381f', "Moss green"],
    '6006' : ['#292b24', "Grey olive"],
    '6007' : ['#1c2617', "Bottle green"],
    '6008' : ['#21211a', "Brown green"],
    '6009' : ['#17291c', "Fir green"],
    '6010' : ['#366926', "Grass green"],
    '6011' : ['#5e7d4f', "Reseda green"],
    '6012' : ['#1f2e2b', "Black green"],
    '6013' : ['#75734f', "Reed green"],
    '6014' : ['#333026', "Yellow olive"],
    '6015' : ['#292b26', "Black olive"],
    '6016' : ['#0f7033', "Turquoise green"],
    '6017' : ['#408236', "Yellow green"],
    '6018' : ['#4fa833', "May green"],
    '6019' : ['#bfe3ba', "Pastel green"],
    '6020' : ['#263829', "Chrome green"],
    '6021' : ['#85a67a', "Pale green"],
    '6022' : ['#2b261c', "Olive drab"],
    '6024' : ['#249140', "Traffic green"],
    '6025' : ['#4a6e33', "Fern green"],
    '6026' : ['#0a5c33', "Opal green"],
    '6027' : ['#7dccbd', "Light green"],
    '6028' : ['#264a33', "Pine green"],
    '6029' : ['#127826', "Mint green"],
    '6032' : ['#298a40', "Signal green"],
    '6033' : ['#428c78', "Mint turquoise"],
    '6034' : ['#7dbdb5', "Pastel turquoise"],
    '6035' : ['#1C542D', "Pearl green"],
    '6036' : ['#193737', "Pearl opal green"],
    '6037' : ['#008F39', "Pure green"],
    '6038' : ['#00BB2D', "Luminous green"],
    '7000' : ['#738591', "Squirrel grey"],
    '7001' : ['#8794a6', "Silver grey"],
    '7002' : ['#7a7561', "Olive grey"],
    '7003' : ['#707061', "Moss grey"],
    '7004' : ['#9c9ca6', "Signal grey"],
    '7005' : ['#616969', "Mouse grey"],
    '7006' : ['#6b6157', "Beige grey"],
    '7008' : ['#695438', "Khaki grey"],
    '7009' : ['#4d524a', "Green grey"],
    '7010' : ['#4a4f4a', "Tarpaulin grey"],
    '7011' : ['#404a54', "Iron grey"],
    '7012' : ['#4a5459', "Basalt grey"],
    '7013' : ['#474238', "Brown grey"],
    '7015' : ['#3d4252', "Slate grey"],
    '7016' : ['#262e38', "Anthracite grey"],
    '7021' : ['#1a2129', "Black grey"],
    '7022' : ['#3d3d3b', "Umbra grey"],
    '7023' : ['#7a7d75', "Concrete grey"],
    '7024' : ['#303845', "Graphite grey"],
    '7026' : ['#263338', "Granite grey"],
    '7030' : ['#918f87', "Stone grey"],
    '7031' : ['#4d5c6b', "Blue grey"],
    '7032' : ['#bdbaab', "Pebble grey"],
    '7033' : ['#7a8275', "Cement grey"],
    '7034' : ['#8f8770', "Yellow grey"],
    '7035' : ['#d4d9db', "Light grey"],
    '7036' : ['#9e969c', "Platinum grey"],
    '7037' : ['#7a7d80', "Dusty grey"],
    '7038' : ['#babdba', "Agate grey"],
    '7039' : ['#615e59', "Quartz grey"],
    '7040' : ['#9ea3b0', "Window grey"],
    '7042' : ['#8f9699', "Verkehrsgrau A"],
    '7043' : ['#404545', "Verkehrsgrau B"],
    '7044' : ['#c2bfb8', "Silk grey"],
    '7045' : ['#8f949e', "Telegrau 1"],
    '7046' : ['#78828c', "Telegrau 2"],
    '7047' : ['#d9d6db', "Telegrau 4"],
    '7048' : ['#898176', "Pearl mouse grey"],
    '8000' : ['#7d5c38', "Green brown"],
    '8001' : ['#91522e', "Ocher brown"],
    '8002' : ['#6e3b30', "Signal brown"],
    '8003' : ['#733b24', "Clay brown"],
    '8004' : ['#85382b', "Copper brown"],
    '8007' : ['#5e331f', "Fawn brown"],
    '8008' : ['#633d24', "Olive brown"],
    '8011' : ['#47261c', "Nut brown"],
    '8012' : ['#541f1f', "Red brown"],
    '8014' : ['#38261c', "Sepia brown"],
    '8015' : ['#4d1f1c', "Chestnut brown"],
    '8016' : ['#3d1f1c', "Mahogany brown"],
    '8017' : ['#2e1c1c', "Chocolate brown"],
    '8019' : ['#2b2629', "Grey brown"],
    '8022' : ['#0d080d', "Black brown"],
    '8023' : ['#9c4529', "Orange brown"],
    '8024' : ['#6e4030', "Beige brown"],
    '8025' : ['#664a3d', "Pale brown"],
    '8028' : ['#402e21', "Terra brown"],
    '8029' : ['#763C28', "Pearl copper"],
    '9001' : ['#fffcf0', "Cream"],
    '9002' : ['#f0ede6', "Grey white"],
    '9003' : ['#ffffff', "Signal white"],
    '9004' : ['#1c1c21', "Signal black"],
    '9005' : ['#03050a', "Jet black"],
    '9006' : ['#a6abb5', "White aluminium"],
    '9007' : ['#7d7a78', "Grey aluminium"],
    '9010' : ['#faffff', "Pure white"],
    '9011' : ['#0d121a', "Graphite black"],
    '9016' : ['#fcffff', "Traffic white"],
    '9017' : ['#14171c', "Traffic black"],
    '9018' : ['#dbe3de', "Papyrus white"],
    '9022' : ['#9C9C9C', "Pearl light grey"],
    '9023' : ['#828282', "Pearl dark grey"]
};
var $ral_white_colors = ['1013','1014','1015','1016','1017','1018','1026','6019','7047','9001','9002','9003','9010','9016','9018'];
var $ral_objects = new Object();
var $ral_cleaned = new Array();
var $ral_min = 1000;
var $ral_max = 9018;

//alert($ral_colors_spec['9015']==undefined);

function ralStep(id, value, clean) {
    //alert('RAL:'+id+':'+value);
    var ob = document.getElementById(id+'_box');
    if (typeof(ob) == undefined)
        return 0;
    if (clean || (value == 0 && $ral_objects[id] == null)) {
        ob.className = '';
        ob.innerHTML = '';
        if ($ral_cleaned.indexOf(id) == -1) $ral_cleaned.push(id);
        return 0;
    }
    var v = int(value);
    var x = value < 998 ? $ral_min : v;
    var reload = 0;
    if ($ral_objects[id] != value) {
        var inc = ($ral_objects[id] && v>=$ral_min && v<=$ral_max) ? ($ral_objects[id]>v ? -1 : 1) : 
                  (v>1 && v<$ral_min ? -1 : 1);
        while ($ral_colors_spec[x.toString()] == undefined) {
            if (x<=$ral_min && inc==-1) x=$ral_max;
            else if (x>=$ral_max && inc==1) x=$ral_min;
            else x=x+inc;
        }
    }
    else if ($ral_cleaned.indexOf(id) > -1) {
        $ral_cleaned.remove(id);
        reload = 1;
    }
    document.getElementById(id).value = x;
    var key = x.toString();
    var ral = $ral_colors_spec[key];
    var $ral_class_color = $ral_white_colors.indexOf(key) > -1 ? 'black' : 'white';
    if (ral && ral.length==2) {
        ob.style.backgroundColor = ral[0];
        ob.className = 'ral-box'+' '+$ral_class_color;
        ob.innerHTML = '<span>'+ral[1]+'</span>';
    }
    $ral_objects[id] = x;
    return reload;
}


function writeToFile(title, file, text) { 
    if (!isIE) return;

    try {
        alert(title+': '+file);

        var fso = new ActiveXObject("Scripting.FileSystemObject");
        var a = fso.CreateTextFile(file, true);
        a.WriteLine(text.replace(/>\t/g, '>\r\n\t'));
        a.Close();

        alert('OK');
    } 
    catch (e) { 
        alert('error:'+e['description']); 
    }
}