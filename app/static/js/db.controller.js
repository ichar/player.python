// ********************
// HELPER DB CONTROLLER
// --------------------
// Version: 1.0
// Date: 06-06-2015

var current_order_type = -1;            // Order type (otype) code value
var current_order_code = '';            // Current Order code value: C-000-0000

var LOG_SORT = new Array('', 'TOTAL-DESC', 'TOTAL-ASC', 'DATE-DESC', 'DATE-ASC', 'CUSTOM-CODE-DESC', 'CUSTOM-CODE-ASC');

var current_sort = 0;                   // Sorting index
var page_sort_title = '';               // Sorting title tag value

var current_row_id = null;              // ID of current (selected on Data section) row

var selected_row_num = 0;               // Number(#) of selected row 
var selected_row_id = null;             // Selected row ID
var selected_row = null;                // Selected row form's Object
var selected_data_menu_id = '';         // Selected Data menu item (Parameters/Products)
var selected_data_menu = null;          // Selected Data menu Object

var IsGoPagination = false;             // Reset Log page screen flag

var page_total_rows = 0;                // Total rows on the current page
var screen_rows = 5;                    // Rows on a screen
var current_page = 0;                   // Current page number
var per_page = 10;                      // Total rows on a page by default or by custom selection

var refresh_current_state = false;

var is_statistics_activated = false;    // Statistics is active
var is_search_activated = false;        // Search is active
var is_search_focused = false;          // Search input in focus

var search_context = '';                // Current search context value

// ===============
// Action handlers
// ===============

function $GetLog(action, callback) {
    var IsForced = ['301','302'].indexOf(action) > -1 ? true : false;
    var IsError = false;
    var IsRun = false;
    var msg = '';

    if (!isWebServiceExecute) {
        IsRun = true;
        if (!current_page) current_page = 1;
        if (action == '301') selected_row = null;
        //if (selected_row_id)
        current_row_id = selected_row_id;
    }

    if (IsForced || (IsRun && !IsError)) $web_logging(action);

    if (callback != null)
        callback.dialog("close");
    if (IsError)
        $ShowError(msg, true, true, false);
}

function $GetLogItem(source) {
    var container = (source == null ? $("#log-content") : source);
    var parent = null;
    var ob = null;
    var id = '';

    if (isWebServiceExecute)
        return;

    if (selected_row_num >= 1 && selected_row_num <= page_total_rows) {
        id = 'row:'+selected_row_num.toString();
        //parent = container.find("tr[id='row:'"+selected_row_num.toString()+"]").first();
        //parent = container.find("#row:"+selected_row_num.toString()).first();
        container.find(".log-row").each(function(index) {
            if ($(this).attr('id') == id)
                parent = $(this);
        });
        ob = parent ? parent.find(".row_id").first() : null;
        selected_row_id = null;
    } 
    else if (selected_row_id) {
        id = 'id:'+selected_row_id;
        selected_row = null;
        //ob = $("#id:")+selected_row_id;
        container.find(".row_id").each(function(index) {
            if ($(this).attr('id') == id)
                ob = $(this);
        });
    }
    else
        ob = container.find(".row_id").first();

    if (!ob)
        return;

    var id = ob.attr('id');

    if (!parent)
        parent = ob.parents("*[id^='row:']").first();

    //if (!selected_row_id)
    selected_row_id = parseInt(id.split(':')[1]);

    if (!selected_row_id)
        return;

    selected_row_num = parseInt(parent.attr('id').split(':')[1]);

    if (selected_row)
        selected_row.removeClass("selected");

    selected_row = parent;
    selected_row.addClass("selected");

    $ScrollLogContainer(parent);

    if (current_row_id != selected_row_id || refresh_current_state) {
        if (!refresh_current_state)
            $UpdateCurrentCost(0, '', '');
        $GetLog('302', null);
    }
}

// ============
// WEB-SERVICES
// ============

function $web_logging(action) {
    $TriggerActions(true);

    logged_success = false;
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
    var total = 0;

    current_action = action;

    var args = {
        'action':action,
        'custom_code':custom_code,
        'selected_item':selected_row_id,
        'otype':current_order_type,
        'search_context':(is_search_activated && search_context ? search_context : ''),
        'page':current_page,
        'per_page':per_page,
        'sort':LOG_SORT[current_sort],
        'demo':$IS_DEMO,
        'host':host,
        'countryID':countryID,
        'regionID':regionID,
        'userID':userID,
        'currentUsedLocalization':currentLocale,
        'helperXMLVersion':helperXMLVersion,
        'helperVersion':helperVersion,
        'withoutDB':isWorkWithout1C, 
        'withoutRestriction':withoutRestriction,
        'wizardID':wizardID,
        'wizardName':wizardName,
        'orderInfo':(action == '307' ? order_info : ''),
        'check':$("#check").val(),
        'data':''
    };

    $ShowSystemMessages(true, true);
    $ShowLoader(1);

    $.post($SCRIPT_ROOT + loaderURI, args, function(x) {
        if (action != x['action'])
            alert('...');

        var data = x['data'];
        var refresh_state = true;

        // -----------------------
        // Server Exchange erorors
        // -----------------------
        error.exchange_error = parseInt(x['exchange_error'] || 0);
        error.exchange_message = x['exchange_message'];

        // --------
        // RESPONSE
        // --------
        if (error.exchange_error)
            refresh_state = false;
        else if (action == '301' || action == '308') {
            total = int(x['total'] || 0);

            if (total > 0) { // || !is_search_activated
                $HideLogPage();
                $updateLog(data);

                var pages = x['pages'];
                var iter_pages = x['iter_pages'];
                var has_next = x['has_next'];
                var has_prev = x['has_prev'];

                current_page = x['page'];
                per_page = x['per_page'];

                $updateLogPagination(pages, total, iter_pages, has_next, has_prev, per_page);

                page_total_rows = int(x['rows_on_page']);
            }

            $updateResponsedItemValue('region', x, 'regionName');
            $updateResponsedItemValue('country', x, 'countryName');
            $updateResponsedItemValue('client', x, 'clientName');

            logged_success = true;
        }
        else if (action == '302') {
            custom_code = x['custom_code'];

            $updateLogData(action, data);

            logged_success = true;
        }
        else if (action == '304') {
            price = x['price'];

            $UpdateCurrentCost(price, error.exchange_error, '');
        }
        else if (action == '305') {
            $updateStatistics(data);
        }
        else if (action == '307') {
            order = x['order'];
            price = x['price'];

            $UpdateCurrentCost(price, error.exchange_error, '');

            ordered_success = true;
        }

        if (refresh_state) {
            if (['304','307'].indexOf(action) > -1) {
                $updateResponsedItemValue('region', x, 'regionName');
                $updateResponsedItemValue('country', x, 'countryName');
                $updateResponsedItemValue('client', x, 'clientName');
            }
        }

        $ShowLoader(-1);
        $TriggerActions(false);

    }, 'json')
    .fail(function() {
        $ShowLoader(-1);
        $TriggerActions(false);
    })
    .always(function() {

        if (page_state == -1)
            page_state = 0;

        if (['301','308'].indexOf(action) > -1 && logged_success) {
            $ResetSearch(false);

            if (!total) // && is_search_activated
                $ShowError(keywords['Data not found!'], true, true, false);
            else {
                $ResizePageWindow(false);
                $GetLogItem(null);

                if (IsGoPagination) {
                    $ResetLogPage();
                    IsGoPagination = false;
                }
            }
        }
        else if (action == '302' && logged_success) {
            refresh_current_state = false;
            
            $ResetHelper();
            $ShowMenu(selected_data_menu_id);
        }
        else if (action == '304' && price && calculated_success) {
            $OpenOrderWindow(keywords['cost form'], keywords['estimated cost'], keywords['cost']+': '+price);
        } 
        else if (action == '305') {
            $OpenStatisticsWindow();
        } 
        else if (action == '307' && order && price && ordered_success) {
            $OpenOrderWindow(keywords['order form'], keywords['ordered success'], order);
        }

        parameters = '';

        if (!page_state && (action == '302' || error.exchange_error || error.error_code)) {
            $("#page-loader").hide();
            $("#html-container").show();

            page_state = 1;
        }

        $HandleWithError(error);
    });
}
