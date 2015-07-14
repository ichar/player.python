// ***********************************
// HELPER PAGE FIELDS STATE CONTROLLER
// -----------------------------------
// Version: 1.0
// Date: 04-06-2015

var DISABLED_KINDS = new Array('IMAGE', 'DUMMY', 'ALERT');

// ========================
// Field's State controller
// ========================

var $Field = {
    cache: new Object(),
    on_focus: null,

    get: function(id) 
    {
        if (!id || gids.indexOf(id) == -1 || DISABLED_KINDS.indexOf(gattrs[id].kind) > -1)
            return '';
        self[id] = $Field._read(id);
    },
    _read: function(id) 
    {
        var value = '';
        var ob = $("#"+id);
        switch (gattrs[id].type) 
        {
            case 'STRING':
                if (['DISPLAY FIELD', 'LABEL'].indexOf(gattrs[id].kind) > -1)
                    value = ob.html();
                else if (['INPUT AREA', 'SIMPLE INPUT'].indexOf(gattrs[id].kind) > -1)
                    value = ob.val();
                break;
            case 'NUMBER':
                value = ob.val();
                if (value && !isNaN(value))
                    value = int(value);
                else
                    value = 0;
                break;
            case 'BOOLEAN':
                value = ob.prop('checked') ? true : false;
                break;
            case 'LIST':
                var has_multiple = ob.prop("multiple") ? true : false;
                var has_code = [undefined, false].indexOf($("option", ob).first().attr("data-code")) == -1;
                var index = has_multiple ? '' : ob.prop('selectedIndex');
                var i = 0;
                $("option", ob).each(function() {
                    var oid = $(this).attr('value');
                    if (oid) {
                        value += $(this).attr('value') + LST_ITEM_DELIMETER + $(this).text();
                        var code = $(this).attr("data-code");
                        if (has_code && code)
                            value += LST_ITEM_DELIMETER + code;
                        if (has_multiple && $(this).prop('selected')) {
                            if (index) index += LST_INDICES_DELIMETER;
                            index += i.toString();
                        }
                        value += LST_VALUE_DELIMETER;
                    }
                    ++i;
                });
                value = index + LST_INDEX_DELIMETER + value;
                break;
            default:
                value = ob.val();
        }
        return value;
    },
    changed: function(id) 
    {
        return this._read(id) != this.cached(id) ? true : false;
    },
    cached: function(id) 
    {
        return id in this.cache ? this.cache[id] : null;
    },
    current_value: function(id)
    {
        var value = this.cache[id];
        var ob = $("#"+id);
        switch (gattrs[id].type) 
        {
            case 'STRING':
                if (gattrs[id].kind == 'CONSTANT')
                    value = self[id];
                else if (['DISPLAY FIELD', 'LABEL'].indexOf(gattrs[id].kind) > -1)
                    value = ob.html();
                else if (['INPUT AREA', 'SIMPLE INPUT'].indexOf(gattrs[id].kind) > -1)
                    value = strip(ob.val());
                break;
            case 'NUMBER':
                //value = int(ob.val());
                value = int(value);
                break;
            case 'BOOLEAN':
                value = value ? true : false;
                break;
            case 'LIST':
                //value = $("option:selected", ob).text();
                value = getListSelectedItem(value, 1);
                $Images.ArangeWidthOfSelectBox(ob);
                break;
            default:
                if (ob.val() != value)
                    value = '';
        }
        return value;
    },
    focus: function(id) 
    {
        var ob = $("#"+id);
        var area = $("#data-section");
        var row = $("#"+id+'_title');
        var title = typeof(row) == 'object' ? row.html() : '';
        if (title) {
            $Search.forced(title);
            $Field.on_focus = ob;
        }
        ob.focus();
    },
    set: function(id, value) 
    {
        if ($Field.on_focus)
            $Search.reset(0);
        if (!id || gids.indexOf(id) == -1 || DISABLED_KINDS.indexOf(gattrs[id].kind) > -1 || typeof(value) == 'undefined')
            return;
        if (!helperErrorCode || parseInt(helperErrorCode) == 0)
            $Field.commit(id, value); 
        else
            $Field.rollback(id, value);
    },
    _write: function(id, value) 
    {
        var ob = $("#"+id);
        if (typeof(ob) == 'undefined')
            return;
        switch (gattrs[id].type) 
        {
            case 'STRING':
                if (['DISPLAY FIELD', 'LABEL'].indexOf(gattrs[id].kind) > -1 && value)
                    ob.html(value);
                else if (['INPUT AREA', 'SIMPLE INPUT'].indexOf(gattrs[id].kind) > -1 && value)
                    ob.val(strip(value));
                break;
            case 'NUMBER':
                ob.val(value);
                break;
            case 'BOOLEAN':
                ob.prop('checked', value ? true : false);
                break;
            case 'LIST':
                var options = ob.prop("options");
                var is_run = false;
                if (options && typeof(options) != 'undefined') {
                    $('option', ob).remove();
                    is_run = true;
                }
                var has_multiple = ob.prop("multiple") ? true : false;
                var x = value.split(LST_INDEX_DELIMETER);
                if (value && x.length > 1 && x[1]) {
                    if (has_multiple) {
                        var selected_index = 0;
                        var selected_indices = x[0].split(LST_INDICES_DELIMETER);
                        for (var i=0; i<selected_indices.length; i++) {
                            selected_indices[i] = parseInt(selected_indices[i]);
                        }
                    } else {
                        var selected_index = parseInt(x[0]);
                        var selected_indices = new Array();
                    }
                    var values = x[1].split(LST_VALUE_DELIMETER);
                    var has_code = values[values.length>1 ? 1 : 0].split(LST_ITEM_DELIMETER).length > 2;
                    var l = 0;
                    if (is_run) {
                        for (var i=0; i<values.length; i++) {
                            if (!values[i] || values[i].indexOf(LST_ITEM_DELIMETER) == -1)
                                continue;
                            var items = values[i].split(LST_ITEM_DELIMETER);
                            var oid = items[0];
                            if (oid) {
                                var option = new Option(items[1],oid, false, false);
                                if (has_code)
                                    option.setAttribute('data-code', items.length > 2 ? items[2] : '');
                                if (has_multiple && selected_indices.indexOf(i) > -1) {
                                    option.setAttribute('selected',  'selected');
                                }   
                                options[options.length] = option;
                                l = Math.max(items[1].length, l);
                            }
                        }
                        if (!has_multiple)
                            ob.prop('selectedIndex', selected_index);
                        $Images.ArangeWidthOfSelectBox(ob);
                    }
                }
                break;
            default:
                ob.val(value);
        }
        this.cache[id] = value;
    },
    commit: function(id, value) {
        try {
            if (value != $Field.cached(id) || value != $Field._read(id))
                $Field._write(id, value);
        }
        catch(e) {
        }
    },
    rollback: function(id, value) {
        try {
            if (value != $Field.cached(id) || value != $Field._read(id))
                $Field._write(id, this.cache[id]);
                self[id] = this.cache[id];
        }
        catch(e) {
        }
    }
};

// Get field's values
// ------------------
function $Download() {
    if (IsDebug)
        alert('Download start');

    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        objectStatus[gid] = 1;
        $Field.get(gid);
    }
}

// Set field's values
// ------------------
function $Upload() {
    if (IsDebug)
        alert('Upload start');

    var ids = new Array();

    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        $Field.set(gid, self[gid]);
        // ----------
        // RAL Events
        // ----------
        try {
            if (gid in $ral_objects) {
                if ($ral_objects[gid] != null) {
                    if (!objectStatus[gid])
                        ralStep(gid, 0, true);
                    else if (ralStep(gid, $ral_objects[gid], false))
                        changed_ids.push(gid);
                } else if (self[gid]) {
                    $ral_objects[gid] = self[gid];
                    ralStep(gid, $ral_objects[gid], false);
                }
            }
        }
        catch(e) {
            alert(gid);
        }
        // ------------------------
        // Check RADIOBUTTON values
        // ------------------------
        if (gattrs[gid].kind == 'RADIOBUTTON')
            ids.push(gid);
    }

    for(var i=0; i < ids.length; i++) {
        var gid = ids[i];
        $Field.get(gid);
    }
}

// ============
// Helper State
// ============

function $ShowPrompting(id) {
    $("#prompting").text(id && id in promptings ? promptings[id] : defaultPrompting);
}

// Status handlers
// ---------------
function $CheckObjectStatus() {
    if (IsDebug)
        alert('CheckObjectStatus start');

    for(var i=0; i < gids.length; i++) {
        var gid = gids[i];
        if (DISABLED_KINDS.indexOf(gattrs[gid].kind) > -1)
            continue;
        var disabled = objectStatus[gid] == 0 ? true : false;
        var is_check_title = true;
        if ($_is_radiobutton(gid)) {
            var ids = $_get_radiobutton_items(gattrs[gid].subgroup);
            for(var n=0; n < ids.length; n++) {
                if (objectStatus[ids[n]]) {
                    is_check_title = false;
                    break;
                }
            }
        }
        for(var n=0; n < 2; n++) {
            var ob = $("#"+gid+(n?'_title':''));
            try {
                if (disabled) {
                    if (!is_check_title && n)
                        disabled = false;
                    else {
                        ob.attr('disabled', disabled);
                        ob.parent().children().addClass('disabled');
                        ob.parent().children("input").attr('disabled', disabled);
                    }
                }
                if (!disabled && ob.hasClass('disabled')) {
                    ob.removeAttr('disabled');
                    ob.parent().children().removeClass('disabled');
                    ob.parent().children("input").attr('disabled', disabled);
                }
            }
            catch(e) {
                if (IsTraceErrorException)
                    alert('Error CheckObjectStatus:'+gid);
            }
        }
    }
}

// ====================
// Form events handlers
// ====================

function $Run(id) {
    if (IsDebug)
        alert('Run start, scriptExecCount:['+scriptExecCount+']');

    if (isConfirmation) return;

    if (IsCheckImageTimeout && TID[1] && id == changedFormFieldID) return;

    if (TID[1]) interrupt(false, 0, 0, null, 1);

    // Catch related changed items
    // ---------------------------
    var ids = new Array(id);

    if ($_is_radiobutton(id)) {
        ids = ids.concat($_get_radiobutton_items(gattrs[id].subgroup));
    }
    if (ids.length) {
        for(var i=0; i < ids.length; i++) {
            var gid = ids[i];
            $Field.get(gid);
        }
    }

    // Mark off field changed item
    // ---------------------------
    changedFormFieldID = id;

    $(".current_price").html(keywords['not calculated']).removeClass('success').addClass('na');

    $Init();
}

function $Finalize() {
    if (IsDebug || IsTrace) 
        alert('Finalize start');

    var x = helperProductControl.type;

    helperProductControl.active = false;
    helperProductControl.finalize = false;
    helperProductControl.type = 0;

    if (x == 1)
        $GoCalculateWindow(false);
    else if (x == 2)
        $GoOrderConfirmationWindow();
}

// =======================
// Field's Event listeners
// =======================

jQuery(function($) 
{
    // -----------------
    // Form Field Events
    // -----------------
    function onChange(ob) {
        var id = ob.attr('id');
        if (IsDeepDebug) {
            var value = gattrs[id].type == 'BOOLEAN' ? ob.prop('checked') : ob.val();
        }
        if (isConfirmation) {
            if (id == changedFormFieldID && id in self && ob.val() != self[id])
                ob.val(self[id]); 
            return;
        }
        $Run(id);
    }

    // Changed events
    // --------------
    $(".field").click(function(e) {
        if (isSafari && $Field.changed($(this).attr('id'))) onChange($(this));
    });

    $(".field").change(function(e) {
        //if (!isSafari) 
        onChange($(this));
    });

    // Forbid cursor moving keypress actions for Safari
    // ------------------------------------------------
    $(".field").keydown(function(e) {
        if ([33, 34, 35, 36, 38, 40].indexOf(e.keyCode)>-1) {
            var id = $(this).attr('id');
            if (isSafari && gattrs[id].type == 'LIST')
                return false;
        }
    });

    // Prompting & Illustration
    // ------------------------
    $(".fieldValue").mouseover(function(e) {
        var id = $(this).find(".field").first().attr('id');
        if (objectStatus[id]) {
            $ShowPrompting(id);
            if (id in illustrations) {
                var src = baseURI+illustrations[id];
                $("#illustration").attr('src', src);
                $("#illustration-area").show();
            }
        }
    }).mouseout(function(e) {
        //var ob = $("#prompting");
        //if (ob.text())
        //    ob.text('');
        var ob = $("#illustration-area");
        if (ob.css('display') != 'none')
            ob.hide();
    });

    // Field's group collapse/expanding
    // --------------------------------
    $(".groupHeader").mouseover(function(e) {
        $(this).css('cursor', 'pointer');
    }).mouseout(function(e) {
        $(this).css('cursor', 'default');
    }).click(function(e) {
        $ToggleGroupState($(this), null);
        e.stopPropagation();
    });
});
