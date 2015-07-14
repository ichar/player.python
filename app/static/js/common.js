// *******************
// COMMON DECLARATIONS
// -------------------
// Version: 1.0
// Date: 04-06-2015

var keywords = new Object();
var script_version = 0;
var default_timeout = 100;
var default_loader_timeout = 300;

var IsDebug = 0;                  // Turn on/off Debug-mode  
var IsDeepDebug = 0;              // Turn on/off DeepDebug-mode  
var IsTrace = 0;                  // Turn on/off Trace-mode
var IsTraceCommit = 0;            // Alert Field's state controller Commit-errors
var IsTraceRollback = 0;          // Alert Field's state controller Rollback-errors
var IsTraceErrorException = 0;    // Alert(show) error exception
var IsForcedRefresh = 0;          // Forced refresh any images in filesystem-cache (load with timestamp-link)
var IsAssumeExchangeError = 0;    // Exchange errors allowed or not (for localhost debug reasons)
var IsXMLDump = 0;                // For 'internal' only - dump request/response or not
var IsCleanBefore = 1;            // For 'internal' only - how to referesh items (clean before or not)
var IsCheckImageTimeout = 0;      // Wait images will be refreshed before init a new state

// ==========================================================================================================

// Global Constants
// ----------------
var LST_INDEX_DELIMETER = '##';
var LST_INDICES_DELIMETER = ':';
var LST_VALUE_DELIMETER = ';';
var LST_ITEM_DELIMETER = '|';

var TID = new Array(null, null);
var forced_reload = false;
var changed_ids = new Array();

var current_action = '';
var current_screen = '';
var current_scale = null;
var query_string = '';

var web_default_page = 'index';
var web_log_page = 'log';
var web_args = new Array();
var web_page = '';

var agent = '';
var platform = '';

var page_state = -1;

var isWebServiceExecute = false;
var isSubmitted = false;

var calculated_success = false;
var ordered_success = false;
var logged_success = false;

var custom_code = '';
var option_update = false;
var option_cost = false;

var selected_action = '';
var selected_item = '';

var total_log_rows = 0;

var SID = null;
var signal;

// Exchange handlers
// -----------------
var internal_get_action = null;
var internal_get_xml = null;
var internal_set_action = $web_calculating;
var internal_set_xml = null;

// Helper items
// ------------
var attentionMessage = '';
var baseURI = '';
var calculatingDisabled = -1;
var changedFormFieldID = '';
var changedLog = new Array();
var changedTitle = '';
var clientName = '';
var closeURI = '';
var confirmCode = -1;
var confirmMessage = '';
var confirm_window_closed = false;
var constSavedImage = '';
var currentImageURI = '';
var currentLocale = '';
var countryID = '';
var countryName = '';
var country_path = '';
var currencyID = '';
var currencyName = '';
var defaultConstruct = '';
var defaultConstructCount = 0;
var defaultProduct = '';
var defaultPrompting = '';
var documentID = '';
var helperCommunicationType = '';
var helperReset = false;
var helperErrorCode = 0;
var helperErrorMessage = '';
var helperFocusOn = '';
var helperHostName = '';
var helperHttpReferer = '';
var helperPageLocation = '';
var helperRequestURI = '';
var helperPathURI = '';
var helperCalculatingVersion = '';
var helperLoadedVersion = '';
var helperModelVersion = '';
var helperProductControl = {'active':false, 'enabled':false, 'type':null, 'finalize':false};
var helperSessionID = '';
var helperURI = '';
var helperVersion = '2.0';
var helperXMLVersion = '';
var host = '';
var image = '';
var imagePath = new Array();
var imageVisibility = new Array();
var imageOffset = new Array();
var imageX = new Array();
var imageY = new Array();
var isAutoChanged = false;
var isConfirmation = false;
var isInternal = false;
var isWorkWithout1C = false;
var loaderURI = '';
var NoticeMessage = '';
var objectStatus = new Object();
var options = new Array();
var parameters = '';
var priceTypeID = '';
var regionID = '';
var regionName = '';
var scriptExecCount = 0;
var setImageURI = '';
var sessionID = '';
var showOnStartup = '';
var userID = '';
var userTypeID = '';
var withoutRestriction = false;
var wizardID = '';
var wizardName = '';

var UPDATED_ITEMS = new Array('documentDate', 'documentNumber', 'priceTypeID', 'userTypeID', 'withoutRestriction');
var SERVICE_ITEMS = new Array('constSavedImage');

// ----------------
// Global Functions
// ----------------

function interrupt(start, mode, timeout, callback, index) {

    if (start) {
        var i = (index != null) ? index : TID.length;
        var s = "interrupt(false, "+mode+", 0, "+(callback ? "'"+callback+"'" : 'null')+", "+i+")";
        if (i == TID.length) TID.push(null);
        TID[i] = window.setTimeout(s, timeout ? timeout : default_timeout);
    } else if (mode) {
        if (mode == -1) {
            if (!callback) callback = 'https:/'+'/newdealer..'+(currentLocale=='rus'?'ru':'com')+'/'+currentLocale.substr(0,2)+'/';
            window.location.replace(callback);
        } else if (mode == 1) {
            interrupt(false, 0, 0, null, 0);
            $ToggleGroupsOnStartup();
            $Calculate('203', null);
        } else if (mode == 2) {
            if (!$Images.ai_count) {
                interrupt(false, 0, 0, null, 1);
                $Images._show_absolute_images();
            }
        } else if (mode == 3) {
            interrupt(false, 0, 0, null, index);
            $Search._clear();
        } else if (mode == 4) {
            interrupt(false, 0, 0, null, index);
            $ShowOnStartup();
        } else if (mode == 9) {
            interrupt(false, 0, 0, null, index);
            if (callback) window[callback]();
        }
    } else if (TID.length > index && TID[index] != null) {
        window.clearTimeout(TID[index]);
        if (index > 1) TID.splice(index, 1); else TID[index] = null;
    }
}

function $_init() {
    var f = !$IS_FRAME ? true : false;
    var top = int($(window).height()/2)-80; //(f?0:80);

    $("#page-loader")
        //.offset({ top:top })
        .css('top', top)
        .show();

    var host = location.origin+'/';
    var x = window.location.href.replace(host, '').split('?');

    query_string = x && x.length > 1 && x[1] ? '?'+x[1] : '';

    web_page = x && x.length ? (!x[0] ? web_default_page : x[0]) : web_default_page;
    if (x.length > 1 && x[1])
        web_args = x[1].split('&');

    helperURI = window.location.href.replace(/log|index/i, '');

    if (current_screen == 'full') {
        is_full_screen = false;
        $ToggleFullScreen();
    }

    interrupt(true, 4, 100, null, null);
}

function $_screen_center() {
    var f = !$IS_FRAME ? true : false;
    var m = f ? 'screen-max':'screen-min';
    return { 'W':$_width(m), 'H':$_height(m) };
}

function $_height(m) {
    //var ob = $(window);
    if (m == 'screen-max')
        return Math.max(window.screen.availHeight, verge.viewportH());
    if (m == 'screen-min')
        return Math.min(window.screen.availHeight, verge.viewportH());
    if (m == 'max')
        return Math.max(
            window.screen.height, 
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
            //ob.height()
        );
    else
        return Math.min(
            window.screen.height,
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
            //ob.height()
        );
}

function $_width(m) {
    //var ob = $(window);
    var f = !$IS_FRAME ? true : false;
    if (m == 'screen-max')
        return Math.max(window.screen.availWidth, verge.viewportW());
    if (m == 'screen-min')
        return Math.min(window.screen.availWidth, verge.viewportW());
    if (m == 'max')
        return Math.max(
            window.screen.width,                    // S
            window.screen.availWidth,               // W
            document.body.clientWidth,              // B
            document.documentElement.clientWidth    // H
            //ob.width()
        );
    else
        return Math.min(
            window.screen.width, 
            window.screen.availWidth, 
            document.body.clientWidth, 
            document.documentElement.clientWidth
            //ob.width()
        );
}

function $_check_number(value) {
    // ----------------------
    // Check and round number
    // ----------------------
    var v = parseFloat(value);
    if (isNaN(v))
        return value;
    var i = parseInt(value);
    if (isNaN(i) || i == v)
        return value;
    var s = (v - Math.floor(v)).toString();
    var d = s.length > 6 ? int(s.substr(2)) : 0;
    if (d)
        v = Number(roundNumber(v, d > 10000 ? 4 : 2, false));
    return v;
}

function $_get_cis_id(id) {
    for(var x in cis)
        //if (cis[x].id == id || (cis[x].keys && cis[x].keys.split(':').indexOf(id) > -1))
        if (cis[x].id == id)
            return x;
    return null;
}

function $_get_radiobutton_items(subgroup) {
    var ids = new Array();
    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        if (gattrs[gid].subgroup == subgroup && $_is_radiobutton(gid))
            ids.push(gid);
    }
    return ids;
}

function $_get_obs(items) {
    var obs = new Object();
    for(var i=0; i < items.length; i++) {
        var ob = items[i];
        if (ob != null) {
            if ('id' in ob) obs[ob.id] = items[i];
            if ('parent' in ob && ob.parent) obs[ob.parent] = items[i];
        }
    }
    return obs;
}

function $_window_orientation() {
    return typeof(window.orientation) !== 'undefined' ? (
        window.orientation == 0 || window.orientation == 180 ? 'portrait' : 'landscape') : 
        window.screen.orientation;
}

function $_open_noframe_dialog(container) {
    var my = "center top";
    var at = "center top";
    var of = "#header-container";
    var orientation = $_window_orientation();

    if (is_full_screen) {
        if (IsStringStartedWith(orientation, 'portrait'))
            of ="#page-container";
        else
            at = "center top+40px";
    }
    else
        at = "center top+40px";

    container.dialog("option", "position", {my:my, at:at, of:of});
}

function $_get_window_scale() {
    var scale = 1;
    var window_height = 0;
    var enabled = true;

    if (isAndroid) {
        var h = document.documentElement.clientHeight;
        var w = document.documentElement.clientWidth;

        if (w <= 1040) {

            if (isMozilla) {
                window_height = Math.max(
                    window.screen.availHeight, 
                    verge.viewportH()
                );
                if (window_actual_size.length && window_actual_size[1] > window_height)
                    window_height = 0;
                enabled = false;
            }
            else if (current_scale && current_scale.length > 2) {

                scale = current_scale[2];
                window_height = current_scale[1];
                current_scale = null;
                window_actual_size = [];

            }
            else {
                scale = (verge.viewportW()/$_width('max'));
                window_height = verge.viewportH();
            }

            $IS_FRAME = 0;
        }
    } 
    else {
        enabled = false;
        scale = 0;
    }
    
    return {'scale':scale, 'window_height':window_height, 'enabled':enabled};
}

function $_is_radiobutton(gid) {
    return gattrs[gid].kind == 'RADIOBUTTON' && gattrs[gid].subgroup ? true : false;
}

function $_is_checked(id) {
    var ob = $("#"+id);
    return ob && ob.prop('checked') ? true : false;
}

function $_update_item_value(id, v) {
    if (v == n_a) return;
    var value = null;
    switch (v.toLowerCase()) {
        case 'true':
            value = true;
            break;
        case 'false':
            value = false;
            break;
        default:
            value = v;
    }
    if (id in self) self[id] = value;
}

function $_is_changed_key_exist(gid) {
    var up_key = '_up';
    var list_key = '_List';
    var value_key = '_Value';
    var keys = new Array(up_key, value_key);
    var is_ok = false;

    function cut_off(name, key) {
        if (key)
            return IsStringEndedWith(name, key) ? name.substr(0, name.indexOf(key)) : name;
        return name.split('_')[0];
    }

    if (changedLog.indexOf(gid) > -1)
        //
        // Explict equal
        //
        is_ok = true;
    else if (IsStringEndedWith(gid, up_key) || IsStringEndedWith(gid, value_key)) {
        //
        // Lists as for example: outerColor_up:OuterColor_List
        //
        for(var i=0; i < changedLog.length; i++) {
            var id = changedLog[i];
            if (IsStringEndedWith(id, value_key) || (gattrs[id].type == 'LIST' && IsStringEndedWith(id, list_key))) {
                //var key1 = cut_off(cut_off(gid, value_key), up_key).toLowerCase();
                //var key2 = cut_off(id, list_key).toLowerCase();
                var key1 = cut_off(gid, null).toLowerCase();
                var key2 = cut_off(id, null).toLowerCase();
                if (IsStringStartedWith(key2, key1)) {
                    is_ok = true;
                    break;
                }
            }
        }
    }

    if (!is_ok) {
        //
        // Ended with special keys: _up ...
        //
        for(var i=0; i < keys.length; i++) {
            var key = keys[i];
            var id = cut_off(gid, key);
            if (IsStringEndedWith(gid, key) && changedLog.indexOf(id) > -1) {
                is_ok = true;
                break;
            }
        }
    }

    return is_ok;
}

function $_stop_loader() {
    if (SID != null) {
        window.clearTimeout(SID);
        SID = null;
    }
}

function $_go_loader() {
    $_stop_loader();
    signal = signal==3 ? 1 : signal+1;
    SID = window.setTimeout("$ShowLoader(0)", default_loader_timeout);
}

function $_is_calculation_ready() {
    if (web_page == web_log_page)
        return true;
    if (!getListLength(parameters)) $OpenCalculateWindow(true);
    return order_info ? true : false;
}

// --------------------------------------
// Public Page Controller Status handlers
// --------------------------------------

function $InitState() {
    helperErrorCode = 0;
    helperErrorMessage = '';
    attentionMessage = '';
    margins = '0##';
    imagePath = [];
    imageVisibility = [];
    imageOffset = [];
    imageX = [];
    imageY = [];

    if (calculatingDisabled != -1 && web_page == web_default_page) 
        $TriggerActions(calculatingDisabled ? true : false);

    isAutoChanged = false;

    if (!isConfirmation) confirmCode = -1;
    confirm_window_closed = false;
    confirmMessage = '';

    $InitObjectStatus();
}

function $InitObjectStatus() {
    if (IsDebug)
        alert('InitObjectStatus start');

    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        objectStatus[gid] = 1;
    }
}

function $UpdateState(action, data) {
    var items = { 'products':[], 'parameters':[], 'codes':[], 'ids':{} };
    var with_items = (action > '300' ? true : false);

    for(var i=0; i < UPDATED_ITEMS.length; i++) {
        var id = UPDATED_ITEMS[i];
        if (id in data)
            $_update_item_value(id, data[id]);
    }

    var products = $_get_obs(data['products']);
    var parameters = $_get_obs(data['parameters']);

    for(var i=0; i < SERVICE_ITEMS.length; i++) {
        var id = SERVICE_ITEMS[i];
        var ob = (id in parameters) ? parameters[id] : null;
        if (ob != null)
            self[id] = ob['value'];
    }

    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        var id = null, kind, typ, title;
        if (gid in cis) {
            id = getattr(cis[gid], 'id', null);
            kind = gattrs[gid].kind;
            typ = gattrs[gid]['type'];
            title = cis[gid]['title'];
        }
        if (!(id && gid in self))
            continue;

        if (IsCleanBefore) {
            if (['CONSTANT', 'CHECKBOX'].indexOf(kind) > -1 && typ == 'BOOLEAN')
                self[gid] = false;
            else if (['CONSTANT', 'INPUT FIELD', 'SIMPLE INPUT'].indexOf(kind) > -1 && typ == 'NUMBER')
                self[gid] = 0;
        }

        var ob = (id in products) ? products[id] : null;

        if (ob != null) {
            var a = ('article' in ob) ? ob['article'] : '';
            var p = ('price' in ob) ? ob['price'] : '';
            var t = ob['type'];
            var v = ob['value'];
            var value = null;

            if (['RADIOBUTTON', 'CHECKBOX'].indexOf(kind) > -1 && typ == 'BOOLEAN' && v)
                value = true;
            else if (['CONSTANT', 'INPUT FIELD', 'SIMPLE INPUT'].indexOf(kind) > -1 && v)
                value = (typ == 'NUMBER') ? Number(v) : v;

            if (value != null) self[gid] = value;

            if (with_items && title) {
                items.products.push({'article':a, 'price':p, 'title':title, 'value':value, 'code':id});
                items.codes.push(id);
                items.ids[id] = items.products.length-1;
            }
        }

        var ob = (id in parameters) ? parameters[id] : null;

        if (ob != null) {
            var parent = ob['parent'];
            var t = ob['type'];
            var v = ob['value'];
            var value = null;

            if (parent && IsStringStartedWith(ob.id, parent) && v == keywords['true'] && t == 'BOOLEAN') {
                if (typ == 'LIST') {
                    var key = ob.id.replace(parent, '').replace('_', '');
                    value = setListSelectedIndexById(self[gid], key);

                    if (with_items && title)
                        items.parameters.push({'title':title, 'value':getListSelectedItem(value, 1)});
                }
            }

            if (value == null && t == typ) {
                var x = null;
                if (v == keywords['true'] && t == 'BOOLEAN') {
                    if ($_is_radiobutton(gid)) {
                        var ids = $_get_radiobutton_items(gattrs[gid].subgroup);
                        for(var n=0; n < ids.length; n++)
                            self[ids[n]] = false;
                    }
                    value = true;

                    if (with_items)
                        x = cis[gid].value ? cis[gid].value : (value ? keywords['yes'] : keywords['no']);
                }
                else if (t == 'NUMBER')
                    value = Number(v); // $_check_number(v)
                else if (t == 'STRING')
                    value = v; //unescape(v);
                    
                if (with_items && title)
                    items.parameters.push({'title':title, 'value': (x ? x : value)});
            }

            if (value != null) self[gid] = value;
        }
    }

    return items;
}

// ================================================
// Form's submit & maintenance javascript utilities
// ================================================

function $getResponsedItemValue(id, response) {
    return id in response && response[id] != n_a ? response[id] : '';
}

function $updateResponsedItemValue(id, response, name) {
    var value = response[id+'_name'];
    var ob = $("#"+id);
    if (value && ob) ob.html(value);
    if (name && name in window) window[name] = value;
}

function $onSubmitForm(frm) {
    if (isSubmitted) return false;
    isSubmitted = true;
    $disableForm(frm);
    return true;
}
  
function $disableForm(frm) {
    for(var i=0; i<frm.length; i++) {
        var ob = frm.elements[i];
        if (ob.type == "submit") ob.disabled = true;
    }
}
  
function $enableForm(frm) {
    for(var i=0; i<frm.length; i++) {
        var ob = frm.elements[i];
        if (ob.type == "submit") ob.disabled = false;
    }
}

// ===============
// Action handlers
// ===============

function $ShowSystemMessages(reset, error) {
    if (reset)
        helperErrorMessage = '';
    if (Math.abs(helperErrorCode) >= 25 || (is_full_screen && helperErrorMessage))
        $ShowError(helperErrorMessage, true, error, false);
    else {
        $("#messages-area").html(
            (helperErrorMessage ? '<span class="msg-error">'+helperErrorMessage+'</span><br>' : '') + 
            (attentionMessage ? '<span class="msg-attention">'+attentionMessage+'</span><br>' : '') + NoticeMessage + 
            '<br>-----------<br><div class="msg-platform">'+agent +'</div>'
        );
    }
}

function $TriggerActions(disable) {
    if (disable || $_calculating_disabled()) {
        $("#calculate").attr('disabled', true).addClass('disabled');
        $("#order").attr('disabled', true).addClass('disabled');
        $("#save").attr('disabled', true).addClass('disabled');
    } else {
        $("#calculate").attr('disabled', false).removeClass('disabled');
        if (!isInternal)
            $("#order").attr('disabled', false).removeClass('disabled');
        if ($IsDocumentValid() || changedLog.length || changedTitle) {
            $("#save").attr('disabled', false).removeClass('disabled');
        }
    }
}

function $ToggleFullScreen() {
    $("#header-top").toggleClass('full-screen-header-container');
    $("#footer-container").toggleClass('full-screen-footer-container');
    $("#data-section").toggleClass('full-screen-data-section');
    $("#info-section").toggleClass('full-screen-info-section');
    $("#full-screen-title").toggleClass('displayed');
    $("#full-screen-price-box").toggleClass('displayed');

    $("#toolbar-title").toggleClass('displayed');
    $("#toolbar-loader").toggleClass('displayed');
    $("#toolbar-price-box").toggleClass('displayed');
    $("#toolbar-log-box").toggleClass('displayed');

    is_full_screen = !is_full_screen;
    if (isWebServiceExecute) {
        $("#full-screen-loader").toggleClass('displayed');
        $("#loader").toggleClass('displayed');
        $ShowLoader(0);
    }
}

function $DisableSaveAction() {
    $("#save").attr('disabled', true).addClass('disabled');
}

function $ShowError(msg, is_ok, is_err, is_session_close) {
    if (is_show_error || !msg)
        return;
    var container = $("#error-container");

    $("#error-text").html(msg);

    if (is_ok) {
        $("#error-button").append(
            '<button id="error-button-ok" class="ui-button-text" onclick="javascript:$HideError();">'+keywords['OK']+'</button>'
        );
    }
    if (is_err)
        container.removeClass("warning").addClass("error");
    else
        container.removeClass("error").addClass("warning");

    var f = !$IS_FRAME ? true : false;
    var c = $_screen_center();
    var top = (int((c.H-container.height())/2)-(f?20:0)).toString()+'px';
    var left = (int((c.W-container.width())/2)).toString()+'px';

    container
        .css('top', top).css('left', left)
        .show();
    is_show_error = true;

    $("#error-button-ok").focus();

    if (is_session_close && !$IS_DEMO) interrupt(true, -1, 5000, helperHttpReferer || closeURI, 0);
}

function $HideError() {
    $("#error-container").hide();
    $("#error-button").html('');
    is_show_error = false;
    $SetFocus();
}

function $ShowLoader(start) {
    if (start) {
        var loader = is_full_screen ? $("#full-screen-loader") : $("#loader");
        if (start==-1) { 
            loader.addClass('displayed');
            isWebServiceExecute = false;
        } else {
            loader.removeClass('displayed');
            isWebServiceExecute = true;
            signal = 1;
        }
    }
    if (is_full_screen || start==-1 || !isWebServiceExecute) {
        $_stop_loader();
        return;
    }
    $("#signal").attr('src', $SCRIPT_ROOT+'static/img/s'+signal.toString()+'.png');
    interrupt(true, 9, 200, '$_go_loader', null);
}

function $IsDocumentValid() {
    return ((documentID && documentID != n_a) || isInternal) ? true : false;
}

function $IsClientValid() {
    return (userID && userID != n_a) ? true : false;
}

function $ShowTitle() {
    $("#title").removeClass('displayed');
}

function $ShowClient() {
    if (!userID || userID == n_a) {
        $("#client-caption").addClass('notice').html(keywords['no client']);
        $("#client").hide(); 
    } else {
        $("#client-caption").removeClass('notice').html(keywords['client']);
        $("#client").show();
    }
}

function $UpdateCurrentCost(price, exchange_error, error_code) {
    if (!exchange_error && price && !error_code && !$_calculating_disabled()) {
        $(".current_price").html(price).removeClass('na').addClass('success');
        calculated_success = true;
    }
    else {
        $(".current_price").html(keywords['not calculated']).removeClass('success').addClass('na');
    }
}

function $UpdateTotalLogRows(value) {
    total_log_rows = value ? parseInt(value) : 0;
    $("#total_log_rows").html(value);
}

function $SetFocus() {
    if (helperFocusOn) {
        $Field.focus(helperFocusOn);
        helperFocusOn = '';
    }
}

function $HandleWithError(error) {

    var exchange_error = error.exchange_error;
    var exchange_message = error.exchange_message;
    var error_description = error.error_description;
    var error_code = error.error_code;
    var errors = error.errors;

    if (!IsAssumeExchangeError) {
        if ([-1, -2, -3].indexOf(exchange_error) > -1 || [-99, -199].indexOf(error_code) > -1)
            return $ShowError(keywords['System is not available'], false, true, true);
        if (error_code == -100)
            return $ShowError(keywords['Session is expired'], false, true, true);
    }

    if (exchange_error || exchange_message) {
        if ([-4, -5].indexOf(exchange_error) > -1) {
            if (exchange_message)
                $ShowError(exchange_message, true, true, false);
            exchange_error = 0;
        }
        else {
            if (helperErrorMessage)
                helperErrorMessage += '<br>';
            helperErrorMessage += '['+exchange_error+':'+error_code+'] '+exchange_message+
                (error_description ? '<br>'+error_description : '');
        }
    }

    else if (error_code) {
        if (helperErrorMessage)
            helperErrorMessage += '<br>';
        helperErrorMessage += '['+error_code+'] '+(error_description ? error_description : keywords['Execution error']);
    }

    if (errors) {
        if (helperErrorMessage)
            helperErrorMessage += '<br>';
        helperErrorMessage += errors;
    }

    $ShowSystemMessages(false, true);
}

function $Calculate(action, callback) {
    var IsForced = ['206','208'].indexOf(action) > -1 ? true : false;
    var IsError = false;
    var IsRun = false;
    var msg = '';

    changedFormFieldID = '';

    if (!isWebServiceExecute) {
        IsRun = true;

        if (callback != null) {
            $Init();
            if (helperErrorCode) IsRun = false;
        }

        if (IsRun) {
            if (!$_is_calculation_ready()) {
                if (action == '203')
                    IsForced = true;
                else {
                    msg = keywords['Missing parameters'];
                    IsError = true;
                    IsRun = false;
                }
            }
            if (selected_item && action == '203')
                action = '303';
        }
    }

    if (IsForced || (IsRun && !IsError)) $web_calculating(action, isInternal ? 'get' : null);

    if (callback != null)
        callback.dialog("close");
    if (IsError)
        $ShowError(msg, true, true, false);
}

// ======================
// Common Event listeners
// ======================

jQuery(function($) 
{
    // ----------------
    // Calculator icons
    // ----------------
    $(".calculator").mouseover(function(e) {
        if (!$(this).hasClass('disabled')) $(this).addClass('calc_over');
    }).mouseout(function(e) {
        if (!$(this).hasClass('disabled')) $(this).removeClass('calc_over');
    }).mousedown(function(e) {
        if (!$(this).hasClass('disabled')) $(this).addClass('calc_press');
    }).mouseup(function(e) {
        if (!$(this).hasClass('disabled')) $(this).removeClass('calc_press');
    }).click(function(e) {
        if (!$(this).hasClass('disabled'))
            $OpenCalculatorWindow($(this).attr('id'));
        e.stopPropagation();
    });

    // ----------------------------------------------
    // Main Helper Toolbar (Icons: FullScreen, About)
    // ----------------------------------------------
    $("#screen").click(function(e) {
        $onFullScreen(e);
    });

    $("#info").click(function(e) {
        $OpenAboutWindow(e);
    });

    // ------------------------------------------------------
    // Command Panel (Buttons: Calculate, Order, Save, Close)
    // ------------------------------------------------------
    function $onOpenCalculate(e) {
        $GoCalculate();
        if (e != null) e.preventDefault();
    }

    function $onOpenOrder(e) {
        $GoOrder();
        if (e != null) e.preventDefault();
    }

    function $onOpenSave(e) {
        $GoCalculateWindow(true);
        $OpenSaveConfirmationWindow();
        if (e != null) e.preventDefault();
    }

    function $onFullScreen(e) {
        $ToggleFullScreen();
        $ResizeWindow(true, false);
        if (e != null) e.preventDefault();
    }

    function $onOpenHelp(e) {
        $OpenHelpWindow();
        if (e != null) e.preventDefault();
    }

    function $onOpenAbout(e) {
        $OpenAboutWindow();
        if (e != null) e.preventDefault();
    }

    function $onClose(e) {
        if (isInternal)
            $Calculate('206', null);
        else
            $ParentFormSubmit('close');
        if (e != null) e.stopPropagation();
        return false;
    }

    $(".btn").click(function(e) {
        var ob = $(this);
        var id = ob.attr('id');
        var href = ob.attr("data-href");
        if (!id)
            alert('...');
        else if (id == 'calculate')
            $onOpenCalculate(e);
        else if (id == 'order')
            $onOpenOrder(e);
        else if (id == 'save')
            $onOpenSave(e);
        else if (id == 'close')
            return $onClose(e);
    });

    // ---------------
    // Keyboard Events
    // ---------------
    $(window).keydown(function(e) {
        if (e.ctrlKey) {
            if (e.keyCode==85)                      // Ctrl-U
                $onFullScreen(e);
            else if (e.keyCode==73)                 // Ctrl-I
                $onOpenAbout(e);
        }
        else if (e.keyCode==112)                    // F1
            $onOpenHelp(e);
        else if (e.keyCode==115) {                  // F4
            if (!$("#calculate").attr('disabled'))
                $onOpenCalculate(e);
        }
        else if (e.keyCode==117) {                  // F6
            if (!$("#save").attr('disabled'))
                $onOpenSave(e);
        }
        else if (e.keyCode==118) {                  // F7
            if (!$("#order").attr('disabled'))
                $onOpenOrder(e);
        }
        else if (e.keyCode==121) {                  // F10
            return $onClose(e);
        }
        //alert(e.keyCode);
    });
});

// ==============
// Common Dialogs
// ==============

jQuery(function($) 
{
    // Calculator form
    // ---------------
    $("#calculator-container").dialog({
        autoOpen: false,
        width:isIE&&isIE<11?195:186,
        height:isIE&&isIE<11?292:270,
        position: null,
        modal: true,
        draggable: true,
        resizable: false
    });
});

// ============
// WEB-SERVICES
// ============

function $web_calculating(action, op) {
    if (IsTrace) 
        alert('$web_calculating, action:['+action+']');

    $TriggerActions(true);

    calculated_success = false;
    ordered_success = false;

    var error = {
        'exchange_error':0, 
        'exchange_message':'', 
        'error_description':'', 
        'error_code':'', 
        'errors':''
    };

    var price = '';
    var order = '';

    current_action = action;

    var args = {
        'action':action,
        'title':(changedTitle ? $("#save-confirmation-construction").val():''),
        'selected_item':selected_item,
        'custom_code':custom_code,
        'option_update':(option_update ? '1':''),
        'option_cost':(option_cost ? '1':''),
        'op':op ? op : '',
        'demo':$IS_DEMO,
        'host':host,
        'sessionID':sessionID,
        'countryID':countryID,
        'currency':currencyID,
        'priceTypeID':priceTypeID,
        'regionID':regionID,
        'userID':userID,
        'userTypeID':userTypeID,
        'currentUsedLocalization':currentLocale,
        'defaultConstruct':(construct_default && 'construct_default' in cis ? cis['construct_default'].id : 'construct'+defaultConstruct),
        'defaultConstructCount':Math.max(defaultConstructCount, construct_default, 1),
        'documentID':documentID,
        'documentNumber':'n/a',
        'documentDate':'n/a',
        'helperCommunicationType':helperCommunicationType,
        'helperLoadedVersion':helperLoadedVersion,
        'helperModelVersion':helperModelVersion,
        'helperPageLocation':helperPageLocation,
        'helperRequestURI':helperRequestURI,
        'helperHttpReferer':helperHttpReferer,
        'helperXMLVersion':helperXMLVersion,
        'helperVersion':helperVersion,
        'margins':margins,
        'options':options,
        'parameters':parameters,
        'withoutDB':isWorkWithout1C, 
        'withoutRestriction':withoutRestriction,
        'wizardID':wizardID,
        'wizardName':wizardName,
        'orderInfo':(action == '207' ? order_info : ''),
        'check':$("#check").val(),
        'data':isInternal && op == 'set' && internal_get_xml != null ? internal_get_xml() : ''
    };

    $ShowSystemMessages(true, true);
    if (!isInternal || op == 'get') $ShowLoader(1);

    $.post($SCRIPT_ROOT + loaderURI, args, function(x) {
        if (action != x['action'])
            alert('...');

        var op = x['op'];
        var data = x['data'];
        var refresh_state = true;

        // -----------------------
        // Server Exchange erorors
        // -----------------------
        error.exchange_error = parseInt(x['exchange_error'] || 0);
        error.exchange_message = x['exchange_message'];

        // --------------
        // Service errors
        // --------------
        error.error_description = x['error_description'];
        error.error_code = x['error_code'] ? parseInt(x['error_code']) : 0;
        error.errors = x['errors'];

        // --------
        // RESPONSE
        // --------
        if (error.exchange_error)
            refresh_state = false;
        else if (isInternal && op == 'get') {
            if (internal_get_action != null) internal_get_action(data);
            calculated_success = true;
            refresh_state = false;
        }
        else if (isInternal && op == 'set') {
            if (action == '203') $UpdateState(action, data);
            calculated_success = true;
            data = null;
        }
        else if (action == '303') {
            $UpdateState(action, data);
            calculatingDisabled = -1;
            action = '203';
        }

        if (refresh_state) {
            price = x['price'];
            order = x['order'];

            helperSessionID = $getResponsedItemValue('sessionID', x);

            $updateResponsedItemValue('region', x, 'regionName');
            $updateResponsedItemValue('country', x, 'countryName');
            $updateResponsedItemValue('client', x, 'clientName');

            countryID = x['countryID'];
            regionID = x['regionID'];
            userID = x['userID'];

            custom_code = $getResponsedItemValue('custom_code', x);
            option_update = $getResponsedItemValue('option_update', x) ? true : false;
            option_cost = $getResponsedItemValue('option_cost', x) ? true : false;

            //changedTitle = x['title'];

            $ShowClient();
            $UpdateCurrentCost(price, error.exchange_error, error.error_code);
            $UpdateTotalLogRows(x['total_log_rows']);
        }

        if (!isInternal || op == 'set') {
            $ShowLoader(-1);
            $TriggerActions(false);
        }

    }, 'json')
    .fail(function() {
        $(".current_price").html(keywords['not calculated']).removeClass('success').addClass('na');

        $ShowLoader(-1);
        $TriggerActions(false);
    })
    .always(function() {

        if (page_state == -1)
            page_state = 0;

        if (calculated_success) {
            if (action == '207' && order) {
                ordered_success = true;
                $OpenOrderWindow(keywords['order form'], keywords['ordered success'], order);
            }
            else if (action == '205' && order) {
                ordered_success = true;
                $OpenOrderWindow(keywords['save form'], keywords['saved success'], keywords['Custom code']+': '+order);
            }
            else if (action == '204' && price) {
                $OpenOrderWindow(keywords['cost form'], keywords['estimated cost'], keywords['cost']+': '+price);
            }
            else if (action == '203' && (op == 'set' || !isInternal)) {
                $Init();
            }
        } 

        parameters = '';

        if (!page_state && (action == '203' || error.exchange_error || error.error_code)) {
            $("#page-loader").hide();
            $("#html-container").show();

            page_state = 1;
        }

        $HandleWithError(error);
    });
}

function $web_checking() {
    var checker = new Array();
    var args = {
        'action':'100',
        'host':host,
        'demo':$IS_DEMO,
        'userID':userID,
        'wizardID':wizardID
    };
    $.post($SCRIPT_ROOT + loaderURI, args, function(x) {
        checker.push(x['x1']);
        checker.push(x['x2']);
        checker.push(x['op']);
    }, 'json')
    .done(function() {
        $OpenOrderConfirmationGoWindow(checker[0], checker[1], checker[2]);
    });
}

