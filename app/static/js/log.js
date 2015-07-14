// **********************************
// HELPER PAGE DECLARATION: /log.html
// ----------------------------------
// Version: 1.0
// Date: 04-06-2015

var statistics_box_actual_size = [];

var default_statistics_box_width = 340;
var default_statistics_box_height = 480;
var statistics_box_offset = default_statistics_box_height + 41 - (isSafari ? 2 : 0);

var const_log_content_height  = 135; // 135
var const_data_content_height = 132; // 134
var const_data_content_delta  = 3;

// ----------------------
// Dialog Action Handlers
// ----------------------

function $_order_confirmed(callback) {
    $GetLog('307', callback);
}

function $_order_done(callback) {
    callback.dialog("close");

    if (!(calculated_success || ordered_success))
        return;

    if (ordered_success) {
        // Reset Page
        // ----------
        $_reset_page();

        refresh_current_state = true;
        //current_page = 0;
        //selected_row_id = null;
        current_order_code = '';

        IsGoPagination = true;

        // Deactivate Search
        // -----------------
        $ResetSearch(true);
    }

    // Get Page content
    // ----------------
    $GetLog('301', null);
}

function $_order_removed(callback) {
    selected_row = null;
    current_order_code = '';

    // Remove selected Log item
    // ------------------------
    $GetLog('308', callback);
}

function $_statistics_confirmed(callback) {
    if (!selected_row_id || is_statistics_activated)
        return;

    // Get Statistics for selected Log item
    // ------------------------------------
    $GetLog('305', callback);
}

function $_statistics_done(callback) {
    callback.dialog("close");
}

function $_reset_current_sort() {
    current_page = 1;
}

function $_next_current_sort() {
    current_sort = current_sort == LOG_SORT.length-1 ? 0 : current_sort + 1;
    $_reset_current_sort();
}

function $_deactivate_search() {
    is_search_activated = false;
    search_context = '';
    current_page = 1;
}

function $_reset_item() {
    refresh_current_state = true;
    selected_row_num = 0;
    //current_row_id = null;
}

function $_reset_page() {
    selected_row_num = 0;
    selected_row_id = null;
    current_row_id = null;
}

function $_calculating_disabled() {
    return false;
}

// --------------
// Page Functions
// --------------

function $Init() {
    page_sort_title = $("#sort_icon").attr('title');

    helperReset = false;
    interrupt(true, 9, 0, '$Go', 0);
}

function $Go() {
    $ResetHelper();
    $GetLog('301', null);
}

function $InitIndexForm(mode) {
    var container = $("#index-form-items");
    var item = '<input type="hidden" name="NAME" value="VALUE" />';
    var valid_items = new Array(
            'helperCommunicationType',
            'helperHttpReferer',
            'closeURI',
            'host',
            'sessionID',
            'wizardID',
            'helperSessionID',
            //'helperURI',
            'currentLocale',
            'countryID',
            'regionID',
            'userID',
            'userTypeID',
            'priceTypeID'
        );
    if (mode == 'load') {
        valid_items.push('selected_action');
        valid_items.push('selected_item');
    }
    container.html('');

    valid_items.forEach(function(name) {
        if (name in window) this.append(item.replace(/NAME/g, name).replace(/VALUE/g, escapeHtml(window[name])));
    }, container);

    container.append(item.replace(/NAME/g, 'screen').replace(/VALUE/g, is_full_screen ? 'full':''));
    container.append(item.replace(/NAME/g, 'scale').replace(/VALUE/g, window_actual_size.toString()));
}

function $ParentFormSubmit(mode) {
    var frm = $("#index-form");
    var action = frm.attr('action');

    frm.attr('action', action + query_string);

    if (mode == 'load') {
        if (!selected_row_id)
            return;

        selected_action = mode;
        selected_item = selected_row_id;
    }

    $InitIndexForm(mode);

    frm.submit();
}

function $ShowOnStartup() {
    $("#toolbar-title")
        .addClass('toolbar-log-title');

    $ResizeWindow(true, false);

    $("#data-section").show();
    $("#info-section").show();
}

function $HideLogPage() {
    $("#log-content").hide();
    $("#log-pagination").hide();
}

function $ShowLogPage() {
    $("#log-content").show();
    $("#log-pagination").show();
}

function $ResetLogPage() {
    $("#log-content").scrollTop(0);
}

function $ResetHelper() {
    //
    // Reset (execute) Helper Brains
    //
    scriptExecCount = 0;

    // Init module state
    // -----------------
    $InitState();

    // Run module brains
    // =================
        MainBrains();
    // =================

    $ShowSystemMessages(false, false);
}

function $ResetSearch(deactivate) {
    //
    // Set Search icon and clean search context box
    //
    if (deactivate)
        $_deactivate_search();

    var search = $("#search-context");

    if (search.val()) {
        var src = $SCRIPT_ROOT+'static/img/';

        if (is_search_activated) {
            $("#search-icon")
                .attr('title', keywords['Cancel search'])
                .attr('src', src+'db-close.png');
        } else {
            $("#search-icon")
                .attr('title', keywords['Search'])
                .attr('src', src+'db-search.png');
            search.val('');
        }
    }
}

function $ResizePageWindow(reset) {
    var data = $('#data-section');
    
    $("#log-content").height(data.height() - const_log_content_height);
    $("#data-content").height(data.height() - const_data_content_height);

    var parent = $("#data-content");
    
    var container = $("#parameters-content");
    container.height(parent.height() - const_data_content_delta);

    var container = $("#products-content");
    container.height(parent.height() - const_data_content_delta);

    $ShowLogPage();
}

function $ScrollLogContainer(parent) {
    //
    // Scroll Log page in order to make selected item visible
    //
    var container = $("#log-content");
    var container_top = container.offset().top;
    var container_height = container.height();
    var container_scrollTop = container.scrollTop();
    var parent_top = parent.offset().top - container_top - 1;
    var parent_height = parent.height();

    var x = int(parent_top)+int(parent_height)+2;

    if (x > container_height)
        container.scrollTop(container_scrollTop+x-container_height);
    else if (parent_top < 0)
        container.scrollTop(container_scrollTop+parent_top);
}

function $ShowMenu(id) {
    //
    // Show (open) selected right side's Data menu item (Parameters/Products)
    //
    var parameters = $("#parameters-content");
    var products = $("#products-content");

    if (!id)
        id = 'data-menu-parameters';

    if (selected_data_menu)
        selected_data_menu.removeClass('selected');

    selected_data_menu = $("#"+id);
    //$("#data-content").scrollTop(0);

    if (id == 'data-menu-parameters') {
        products.hide();
        parameters.show();
    } else {
        parameters.hide();
        products.show();
    }

    selected_data_menu.addClass('selected');
    selected_data_menu_id = id;
}

function $GoCalculate() {
    //
    // Common Event Listener -> Page Function(*) -> Action Handler -> WEB-SERVICE
    //
    if (is_statistics_activated)
        return;

    $GetLog('304', null);
}

function $GoOrder() {
    //
    // Common Event Listener -> Page Function(*) -> Dialog window -> Action Handler -> WEB-SERVICE
    //
    if (is_statistics_activated)
        return;

    $OpenOrderConfirmationWindow();
}

// ===========================
// Dialog windows declarations
// ===========================

function $OpenStatisticsWindow() {
    var container = $("#statistics-container");
    var f = !$IS_FRAME ? true : false;

    if (f) {
        container.dialog("option", "position", {my:"left top", at:"left+110px top+60px", of:"#header-container"});
    } else {
        container.dialog("option", "position", {my:"left top", at:"left+110px top+50px", of:"#header-container"});
    }
    container.dialog("open");
}

// ====================
// Page Event Listeners
// ====================

jQuery(function($) 
{

    // ----------------------
    // Select log row (click)
    // ----------------------
    function $onLogClick(ob) {
        if (isWebServiceExecute)
            return;

        selected_row_id = null;

        $GetLogItem(ob);
    } 

    $("#log-content").on('click', '.log-row', function(e) {
        selected_row_num = 0;

        $onLogClick($(this));

        e.preventDefault();
    });

    // ----------------------------
    // Select log page (Pagination)
    // ----------------------------
    function $onSubmitPage() {
        if (isWebServiceExecute)
            return;

        $_reset_page();

        if (current_page) {
            IsGoPagination = true;
            $UpdateCurrentCost(0, '', '');
            $Go();
        }
    }

    function $onSortClick(ob) {
        $_next_current_sort();

        var x = LOG_SORT[current_sort];
        ob.attr('title', page_sort_title+(x ? ' ['+x+']' : ''));

        $onSubmitPage();
    }

    function $onPaginationClick(ob) {
        var id = ob.attr('id');
        if (id == 'page:prev' && current_page > 0)
            current_page -= 1;
        else if (id == 'page:next')
            current_page += 1;
        else
            current_page = int(id.split(':')[1]);

        $onSubmitPage();
    }

    function $onPerPageChanged(ob) {
        var value = ob.val();

        per_page = int(value);
        current_page = 1;

        $onSubmitPage();
    }

    function $onOrderTypeFilterChanged(ob) {
        var value = ob.val();

        current_order_type = (value == 'x' ? -1: value);
        current_page = 1;

        $onSubmitPage();
    }

    $("#sort_icon").click(function(e) {
        $onSortClick($(this));
        e.preventDefault();
    });

    $("#log-pagination").on('click', '.enabled', function(e) {
        $onPaginationClick($(this));
        e.preventDefault();
    });

    $("#log-pagination").on('change', '#per-page', function(e) {
        $onPerPageChanged($(this));
        e.preventDefault();
    });

    $("#log-pagination").on('change', '#filter-otype', function(e) {
        $onOrderTypeFilterChanged($(this));
        e.preventDefault();
    });

    $("#filter-otype").change(function(e) {
        $onOrderTypeFilterChanged($(this));
        e.preventDefault();
    });

    // --------------------
    // Right side Data menu
    // --------------------
    $("div[id^='data-menu']", this).click(function(e) {
        var ob = $(this);
        var id = ob.attr('id');

        $ShowMenu(id);
    });

    // -------------
    // Command Panel
    // -------------
    function $onIndexLoad(e) {
        $ParentFormSubmit('load');
        if (e != null) e.preventDefault();
    }

    function $onLogItemRemove(e) {
        $_order_removed(null);
        if (e != null) e.preventDefault();
    }

    function $onLogItemStatistics(e) {
        $_statistics_confirmed(null);
        if (e != null) e.preventDefault();
    }

    $(".btn").click(function(e) {
        var ob = $(this);
        var id = ob.attr('id');

        if (!id)
            alert('...');
        else if (id == 'load')
            $onIndexLoad(e);
        else if (id == 'remove')
            $onLogItemRemove(e);
        else if (id == 'statistics')
            $onLogItemStatistics(e);
    });

    // ---------------------
    // Search context events
    // ---------------------
    function $onSearchSubmit(e) {
        var s = strip($("#search-context").val());

        if (s) {
            search_context = s;
            is_search_activated = true;

            $_reset_current_sort();
            $onSubmitPage();
        }
        if (e != null) e.preventDefault();
    }

    $("#search-context").focusin(function(e) {
        is_search_focused = true;
    }).focusout(function(e) {
        is_search_focused = false;
    });

    $("#search-icon").click(function(e) {
        if (is_search_activated) {
            $_deactivate_search();

            $onSubmitPage();
        } else
            $onSearchSubmit(null);
    });

    $("#search-form").submit(function(e) {
        $onSearchSubmit(e);
        return false;
    });

    // -------------
    // Resize window
    // -------------
    $(window).on('resize', function() {
        $ResizeWindow(false, false);
    });
    $(window).on('touchmove', function() {
        $ResizeWindow(false, true);
    });

    // --------
    // Keyboard
    // --------
    $(window).keydown(function(e) {
        // -----------------
        // Log Cursor Events
        // -----------------
        if (!e.ctrlKey && e.keyCode < 50) {
            if (isWebServiceExecute || isAndroid || is_statistics_activated || is_search_focused)
                return;
            else if (e.keyCode==38) {               // Up
                if (selected_row_num > 0) {
                    selected_row_num -= 1;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            } 
            else if (e.keyCode==40) {               // Down
                if (selected_row_num < per_page && selected_row_num < page_total_rows) {
                    selected_row_num += 1;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            }
            else if (e.keyCode==35) {               // End
                if (selected_row_num != page_total_rows) {
                    selected_row_num = page_total_rows;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            }
            else if (e.keyCode==36) {               // Home
                if (selected_row_num != 1) {
                    selected_row_num = 1;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            }
            else if (e.keyCode==34) {               // PgDown
                if (selected_row_num < page_total_rows) {
                    selected_row_num += screen_rows;
                    if (selected_row_num > page_total_rows)
                        selected_row_num = page_total_rows;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            }
            else if (e.keyCode==33) {               // PgUp
                if (selected_row_num > 0) {
                    selected_row_num -= screen_rows;
                    if (selected_row_num < 0)
                        selected_row_num = 1;
                    selected_row_id = null;
                    $onLogClick(null);
                }
                e.preventDefault();
            }
        }
        // --------
        // Controls
        // --------
        else if (e.keyCode==113) {                  // F2
            $onIndexLoad(e);
        }
        else if (e.keyCode==120) {                  // F9
            $onLogItemStatistics(e);
        }
    });
});

// ============
// Page Dialogs
// ============

jQuery(function($) 
{

    // -----------------------------------
    // Price Statistics form: <statistics>
    // -----------------------------------
    //$("#statistics-box").css('height', default_statistics_box_height - (isFirefox ? 3 : 0) + (isSafari ? 3 : 0));

    function resizeStatisticsBox(force) {
        if (!$IS_FRAME) return;

        var ob = $("#statistics-container");
        var h = Math.floor(ob.height()) - statistics_box_offset - 4;
        if (!ob.height())
            return;
        $("#statistics-box").css('height', default_statistics_box_height+h-(isIE ? 10 : 0));
        if (force)
            statistics_box_actual_size = [ob.width(), ob.height()];
    }

    $("#statistics-container").dialog({
        autoOpen: false,
        width:default_statistics_box_width,
        //height:default_statistics_box_height,
        position:0,
        buttons: [
            {text: keywords['OK'], click: function() { $_statistics_done($(this)); }}
        ],
        modal: true,
        draggable: true,
        resizable: false, //$IS_FRAME ? true : false,
        open: function() {
            var container = $(this);
            var page = $("#html-container"); // #page-container
            var box = $("#statistics-box");
            var content = $("#statistics-content");
            var x = Math.ceil(page.height());
            x = x - 168;
            try {
                container.height(x);
                box.height(x-54);
                content.height(box.height()-55).scrollTop(0);
            } 
            catch(e) {
                alert('error statistics-container:'+e);
                resizeStatisticsBox(false);
            }
            is_statistics_activated = true;
        },
        close: function() {
            is_statistics_activated = false;
        },
        resize: function() {
            resizeStatisticsBox(false);
        }
    });
});

// =======
// STARTER
// =======

$(function() 
{
    if (IsTrace)
        alert('Document Ready (log)');

    $_init();

    // Global page adjustment
    // ----------------------
    $ShowTitle();
    $ShowClient();

    $("#search-context").attr('placeholder', keywords['Search context']);
});
