var isExchangeReady = false;

isInternal = true;
default_loader_timeout = 400;

function $_is_exchange_ready() {
    return isExchangeReady;
}

function $GetXML() {
    var ob = document.getElementById('exchangeArea');
    return ob.value;
}

function $SetXML(value) {
    var ob = document.getElementById('exchangeArea');
    ob.value = value;
}

function $_exchange_complete() {
    var value = $GetXML();
    
    if (IsXMLDump) writeToFile('Dump to', "C:\\response.xml", value);

    $ExchangeReceive();
}

function $_exchange_raise() {
    interrupt(false, 0, 0, null, null);

    var root = document.body;

    if(document.createEvent) {
        var evObj = document.createEvent('UIEvents');
        evObj.initEvent('ondataavailable', true, false);
        root.dispatchEvent(evObj);
    }
    else if(document.createEventObject) {
        var evt = document.createEventObject();
        root.fireEvent('ondataavailable', evt);
    }
}

function $_exchange_init() {
    var root = document.body;
    var ob = document.getElementById('exchangeArea');

    if (IsXMLDump && isIE) alert('ExchangeData dumping is turn on');
    
    if (root.addEventListener) {
        root.addEventListener('ondatasetcomplete', $_exchange_complete, false);
        isExchangeReady = true;
    }
    else if(root.attachEvent) {
        isExchangeReady = root.attachEvent('ondatasetcomplete', $_exchange_complete);
    }
}

function $_exchange_run() {
    if ($_is_exchange_ready())
        interrupt(true, 9, 0, '$_exchange_raise', null);
    else
        interrupt(true, 9, 0, '$_exchange_run', null);
}

function $ExchangeSend(value) {
    $SetXML(value);

    if (IsXMLDump) writeToFile('Dump to', "C:\\request.xml", value);

    $_exchange_run();
}

function $ExchangeReceive() {
    if (internal_set_action && 'current_action' in window && current_action != '206') 
        internal_set_action(current_action, 'set');
}

internal_get_action = $ExchangeSend;
internal_get_xml = $GetXML;