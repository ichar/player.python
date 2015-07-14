// ************************************
// HELPER PAGE DECLARATION: /index.html
// ------------------------------------
// Version: 1.0
// Date: 04-06-2015

// ----------------------
// Dialog Action Handlers
// ----------------------

function $_order_confirmed(callback) {
    option_update = $_is_checked('save-option-update');
    option_cost = $_is_checked('save-option-cost');

    $Calculate(is_action_save ? '205' : '207', callback);
}

function $_order_done(callback) {
    callback.dialog("close");

    if (!ordered_success)
        return;

    if (!option_update)
        changedLog.splice(0, changedLog.length);

    $DisableSaveAction();
}

function $_calculating_disabled() {
    return calculatingDisabled == 1 ? true : false;
}

// --------------
// Page Functions
// --------------

function $Init() {
    if (IsDebug || IsTrace) 
        alert('Init start, scriptExecCount:['+scriptExecCount+']');

    // Init module state
    // -----------------
    $InitState();

    // Run module brains
    // =================
       MainBrains();
    // =================

    if (forced_reload)
        return;

    if (helperErrorMessage && !helperErrorCode)
        helperErrorMessage = '';

    $Go(1, null);

    if (confirmMessage)
        $OpenHelperConfirmWindow();

    $ShowPrompting(null);
}

function $Go(ok, callback) {
    //
    //  ok:1/0 - ответ: да/нет
    //  callback - объект окна запроса (confirmation)
    //
    if (IsDebug || IsTrace) 
        alert('Go start, ok:['+ok+']');

    // Check confirmation message
    // --------------------------
    if (isConfirmation) {
        if (confirm_window_closed)
            return;

        if (ok != 1)
            helperErrorCode = -1;

        if (callback != null) {
            confirm_window_closed = true;
            callback.dialog("close");
        }

        confirmCode = ok;
    }

    // Evolute new module state
    // ------------------------
    $Upload();

    // Set confirmation reply
    // ----------------------
    if (isConfirmation) 
        $Init();

    // Set focus
    // ---------
    if (helperFocusOn && !helperErrorCode)
        $SetFocus();

    $ShowSystemMessages(false, false);

    if (helperErrorCode && helperErrorCode != -1)
        return;

    // Reload related items
    // --------------------
    while (changed_ids.length) {
        changedFormFieldID = changed_ids.pop();

        $Field.get(changedFormFieldID);
        forced_reload = true;

        $Init();
    }

    forced_reload = false;

    $CheckObjectStatus();

    $Images.ShowImages();

    // Forced refresh
    // --------------
    if (isAutoChanged && !forced_reload) 
        $Init();

    // Helper product control
    // ----------------------
    if (helperProductControl.finalize)
        $Finalize();

    // Register changedFormFieldID actions
    // -----------------------------------
    if (changedFormFieldID) {
        if (changedLog.indexOf(changedFormFieldID) > -1) changedLog.remove(changedFormFieldID);
        changedLog.push(changedFormFieldID);
    }

    $TriggerActions(false);

    if (scriptExecCount == 1) interrupt(true, 1, 0, null, 0); 
}

function $InitLogForm() {
    var container = $("#log-form-items");
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
            'priceTypeID',
            'clientName'
            //'countryName',
            //'regionName',
            //'wizardName'
        );
    container.html('');

    valid_items.forEach(function(name) {
        if (name in window) this.append(item.replace(/NAME/g, name).replace(/VALUE/g, escapeHtml(window[name])));
    }, container);

    container.append(item.replace(/NAME/g, 'screen').replace(/VALUE/g, is_full_screen ? 'full':''));
    container.append(item.replace(/NAME/g, 'scale').replace(/VALUE/g, window_actual_size.toString()));
}

function $ParentFormSubmit(mode) {
    if (helperHttpReferer)
        window.location.replace(helperHttpReferer); //closeURI
    else
        window.history.back();
}

function $ShowOnStartup() {
    $("#toolbar-title")
        .addClass('toolbar-title');
        //.addClass('displayed');

    $ResizeWindow(true, false);
    $Images.ArangeDefaultImage($("#default-image"), true);
}

function $ResizePageWindow(reset) {
    var data = $('#data-section');
    var container = $('#image-area');

    container.height(data.height()-56);

    $Images.ScrollImageArea();
}

function $GoCalculate() {
    //
    // Common Event Listener -> Page Function(*) -> Dialog window -> Action Handler -> WEB-SERVICE
    //
    $OpenCalculateWindow(false);
}

function $GoOrder() {
    //
    // Common Event Listener -> Page Function(*) -> Dialog window -> Action Handler -> WEB-SERVICE
    //
    $OpenOrderConfirmationWindow();
}

// ====================
// Page Event Listeners
// ====================

jQuery(function($) 
{
    // -----------------------------------------------------
    // Main Helper Toolbar (Icons: Collapse, Expand, Search)
    // -----------------------------------------------------
    function $onToggleGroupState(state) {
        $(".groupHeader").each(function() {
            $ToggleGroupState($(this), state);
        });
    }

    $("#collapse").click(function(e) {
        $onToggleGroupState('collapse');
    });

    $("#expand").click(function(e) {
        $onToggleGroupState('expand');
    });

    // --------------
    // Search Toolbar
    // --------------
    function $onSearchActivate(e) {
        $Search.is_activated = true;
        $Search.open();
        if (e != null) e.preventDefault();
    }

    function $onSearchClose(e) {
        $Search.close();
        if (e != null) e.stopPropagation();
    }

    $("#search").click(function(e) {
        $onSearchActivate(null);
    });

    $("#search-text").keypress(function(e) {
        if (e && e.keyCode==13) {                    /* Enter */
            if ($Search.is_activated) {
                $Search.searching(1);
                e.preventDefault();
                return false;
            }
        }
    });

    // ------------
    // Forms Submit
    // ------------
    function $onLogSubmit() {
        var frm = $("#log-form");
        var action = frm.attr('action');
        frm.attr('action', action + query_string);

        $InitLogForm();

        frm.submit();
    }

    function $onLogLoad(e) {
        if (total_log_rows > 0)
            $onLogSubmit();
        if (e != null) e.preventDefault();
    }

    $("#log-icon").click(function(e) {
        $onLogLoad(e);
    });

    // --------------
    // Search buttons
    // --------------
    $(".btn").click(function(e) {
        var ob = $(this);
        var id = ob.attr('id');
        var href = ob.attr("data-href");
        if (id == 'search-back') {
            $Search.searching(0);
            return false;
        }
        if (id == 'search-forward') {
            $Search.searching(1);
            return false;
        }
        if (id == 'search-close') {
            $Search.close();
            return false;
        }
    });

    // --------------------------------
    // Default image position arranging
    // --------------------------------
    $("#default-image").load(function() {
        if (IsDeepDebug)
            alert('load');
        var image = $(this);
        $Images.ArangeDefaultImage(image, true);
        if (!image.hasClass('img-polaroid')) image.addClass('img-polaroid');
    });

    // -------------
    // Resize window
    // -------------
    $(window).on('resize', function() {
        $ResizeWindow(false, false);
        $Search.open();
    });
    $(window).on('touchmove', function() {
        $ResizeWindow(false, true);
    });

    // --------
    // Keyboard
    // --------
    $(window).keydown(function(e) {
        // -------------
        // Search Events
        // -------------
        if (e.keyCode==27 && $Search.is_activated) { // Esc
            $onSearchClose(e);
        }
        else if (e.ctrlKey) {
            if (e.keyCode==76) {                     // Ctrl-L
                $onToggleGroupState('collapse');
                e.preventDefault();
            } 
            else if (e.keyCode==69) {                // Ctrl-E
                $onToggleGroupState('expand');
                e.preventDefault();
            }
            else if (e.keyCode==83) {                // Ctrl-S
                $onSearchActivate(e);
            }
        }
        // --------
        // Controls
        // --------
        else if (e.keyCode==113) {                   // F2
            $onLogLoad(e);
        }
    });
});

// ============
// Page Dialogs
// ============

jQuery(function($) 
{
    // Helper-Confirm form
    // -------------------
    $("#helper-confirm-container").dialog({
        autoOpen: false,
        width:600,
        position: $IS_FRAME ? null : 'top',
        buttons: [
            {text: keywords['yes'], click: function() { $Go(1, $(this)); }},
            {text: keywords['no'], click: function() { $Go(0, $(this)); }}
        ],
        close: function() {
            $Go(0, null);
        },
        modal: true,
        draggable: true,
        resizable: false
    });
});

// =======
// STARTER
// =======

$(function() 
{
    if (IsTrace)
        alert('Document Ready (index)');

    $_init();

    // Global page adjustment
    // ----------------------
    $ShowTitle();
    $ShowClient();

    if (!('default_title_width' in self && !default_title_width))
        $(".fieldTitle").css('width', 200);
});
