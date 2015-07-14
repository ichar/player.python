var c_point = '.';

var $Calculator = {
    is_created: false,
    is_refresh: false,
    is_command_add: false,
    is_command_sub: false,
    is_command_mul: false,
    is_command_div: false,
    current_container: null,
    current_value: '0',
    current_id: null,
    value1: 0,
    value2: 0,

    init: function(container) {
        this.current_container = container.parent();
        if (!this.is_created) {
            var s = 
                '<table id="calculator-form" border="0">'+
                '<tr><td colspan="4"><input id="calculator-score" type="text" value="0"></td></tr>'+
                '<tr><td><button class="btn" id="c_1">1</button></td><td><button class="btn" id="c_2">2</button></td><td><button class="btn" id="c_3">3</button></td><td><button class="btn com" id="c_action_add">+</button></td></tr>'+
                '<tr><td><button class="btn" id="c_4">4</button></td><td><button class="btn" id="c_5">5</button></td><td><button class="btn" id="c_6">6</button></td><td><button class="btn com" id="c_action_sub">-</button></td></tr>'+
                '<tr><td><button class="btn" id="c_7">7</button></td><td><button class="btn" id="c_8">8</button></td><td><button class="btn" id="c_9">9</button></td><td><button class="btn com" id="c_action_mul">*</button></td></tr>'+
                '<tr><td><button class="btn" id="c_0">0</button></td><td><button class="btn" id="c_point">.</button></td><td><button class="btn" id="c_equal">=</button></td><td><button class="btn com" id="c_action_div">/</button></td></tr>'+
                '<tr><td>&nbsp;</td><td><button class="btn action" id="c_reset">C</button></td><td><button class="btn action" id="c_action_close">X</button></td><td><button class="btn" id="c_action_go"> > </button></td></tr>'+
                '</table>';
            container.html(s);
        }
        this.is_created = true;
        this.reset();
    },

    reset: function() {
        this.clean();
        this.current_value = '0';
        this.value1 = this.value2 = 0;
        this.is_refresh = true;
        this.show();
    },

    check: function() {
        var x = $("#calculator-score").val();
        if (this.current_value != x) this.current_value = x;
    },

    show: function() {
        $("#calculator-score").val(this.current_value);
    },

    clean: function() {
        this.is_command_add = this.is_command_sub = this.is_command_mul = this.is_command_div = false;
    },

    close: function() {
        this.current_container.dialog("close");
    },

    set_value: function(gid) {
        this.current_value = $("#"+gid).val();
        this.current_id = gid;
        this.show();
    },

    add: function() {
        this.clean();
        this.is_command_add = true;
    },

    sub: function() {
        this.clean();
        this.is_command_sub = true;
    },

    mul: function() {
        this.clean();
        this.is_command_mul = true;
    },

    div: function() {
        this.clean();
        this.is_command_div = true;
    },

    action: function(key) {
        switch (key) {
            case 'add':
                this.add();
                break;
            case 'sub':
                this.sub();
                break;
            case 'mul':
                this.mul();
                break;
            case 'div':
                this.div();
                break;
        }
        this.value1 = Number(this.current_value);
        this.is_refresh = true;
    },

    evolute: function(value) {
        if (!value)
            return;
        if (this.is_refresh) {
            this.current_value = '';
            this.is_refresh = false;
        }
        if (value==c_point && this.current_value.indexOf(c_point) > -1)
            return;
        this.current_value += value;
        this.show();
    },

    equal: function() {
        if (this.is_command_add || this.is_command_sub || this.is_command_mul || this.is_command_div) {
            this.value2 = Number(this.current_value);
            try {
                var x = this.is_command_add ? this.value1 + this.value2 : (
                        this.is_command_sub ? this.value1 - this.value2 : (
                        this.is_command_mul ? this.value1 * this.value2 : (
                        this.is_command_div ? this.value1 / this.value2 : 
                        0)));
            }
            catch(e) {
                alert('Calculator error: ['+this.value1.toString()+':'+this.value2.toString()+']');
            }
            this.current_value = x.toString();
            this.clean();
            this.show();
        }
    },

    go: function() {
        if (!this.current_id)
            return;
        this.check();
        this.close();

        helperErrorCode = 0;
        if (this.current_id in $ral_objects) $ral_objects[this.current_id] = this.current_value;
        //$Field.set(this.current_id, this.current_value);
        $("#"+this.current_id).val(this.current_value);
        $Run(this.current_id);
    }
};

jQuery(function($) 
{
    $(document).on("click", "button[id^='c_']", function(e) {
        var id = $(this).attr('id');
        var x = id.split('_');
        var key = x.length > 0 ? x[1] : '';
        var action = x.length > 1 ? x[2] : '';

        if (key && '0123456789'.indexOf(key) > -1)
            $Calculator.evolute(key);
        else if (key=='point')
            $Calculator.evolute(c_point);
        else if (key=='reset')
            $Calculator.reset();
        else if (key=='equal')
            $Calculator.equal();
        else if (key=='action') {
            if (action=='go')
                $Calculator.go();
            else if (action=='close')
                $Calculator.close();
            else
                $Calculator.action(action);
        }
    });

    $(document).on("keypress", "#calculator-score", function(e) {
        if (e.keyCode < 48 || e.keyCode > 57)
            return false;
    });
});
