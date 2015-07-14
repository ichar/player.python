// ***************************
// HELPER PAGE DEFAULT CONTENT
// ---------------------------
// Version: 1.0
// Date: 04-06-2015

// -----------------
// Log page handlers
// -----------------

function $updateLog(data) {
    var container = $("#log-content");
    var body = '<td id="ID" class="dataCLASS">VALUE</td>';
    var row = '';

    if (!data) return;

    container.html('');

    row += '<table border="0">';

    for(var i=0; i < data.length; i++) {
        var id = data[i][0];
        var items = data[i][1];
        row += '<tr id="row:NUM" class="log-row CLASS">'
            .replace(/NUM/g, items[0])
            .replace(/CLASS/g, i%2 ? 'odd' : 'even');
        items.forEach(function(x, index) {
            row += body
                .replace(/ID/g, (index == 0 ? 'id:'+id : 'data:'+id+'-'+log_columns[index]))
                .replace(/CLASS/g, (index == 0 ? ' row_id' : ''))
                .replace(/VALUE/g, x);
        });
        row += '</tr>';
    }

    row += '</table>';

    container.append(row);
}

function $updateLogPagination(pages, rows, iter_pages, has_next, has_prev, per_page) {
    var container = $("#log-pagination");
    var prev = '<dd id="page:prev" class="pagination shift CLASS"><<</dd>';
    var body = '<dd id="page:PAGE" class="pagination CLASS">VALUE</dd>';
    var next = '<dd id="page:next" class="pagination shift CLASS">>></dd>';
    var option = '<option value="VALUE"SELECTED>SPACENAMESPACE</option>';
    var space = isAndroid ? '&nbsp;':'';
    var otype_options = new Array(
        {'value':'x', 'name':keywords['All']},
        {'value':'0', 'name':keywords['Standard']},
        {'value':'1', 'name':keywords['Custom']},
        {'value':'2', 'name':keywords['Done']}
    );
    var per_page_options = new Array(10, 20, 30, 40, 50);
    var row = '';

    container.html('');

    row += '<table border="0"><tr>';

    row += '<td><div class="total_rows">TOTAL:<span class="total">ROWS</span></div></td>'
        .replace(/TOTAL/g, keywords['Total'])
        .replace(/ROWS/g, rows);

    if (iter_pages) {
        row += '<td><div id="log-page"><dl>';
        row += prev
            .replace(/CLASS/g, has_prev ? 'enabled':'disabled');
        iter_pages.forEach(function(x, index) {
            row += body
                .replace(/PAGE/g, x ? x : '')
                .replace(/VALUE/g, x ? x : '...')
                .replace(/CLASS/g, (x ? 'valid enabled':'empty') + (int(x)==current_page ? ' selected':''));
        });
        row += next
            .replace(/CLASS/g, has_next ? 'enabled':'disabled');
        row += '</dl></div></td>';
    }

    if (per_page_options) {
        row += '<td><div id="log-per-page"><select class="popup" id="per-page">';
        per_page_options.forEach(function(x, index) {
            row += option
                .replace(/VALUE/g, x)
                .replace(/NAME/g, x)
                .replace(/SPACE/g, space)
                .replace(/SELECTED/g, (per_page == x ? ' selected':''));
        });
        row += '</select></div></td>';
    }

    if (otype_options) {
        row += '<td class="log-filter"><div id="log-filter"><select class="popup" id="filter-otype">';
        otype_options.forEach(function(x, index) {
            var op = otype_options[index];
            row += option
                .replace(/VALUE/g, op.value)
                .replace(/NAME/g, op.name)
                .replace(/SPACE/g, space)
                .replace(/SELECTED/g, (current_order_type == op.value ? ' selected':''));
        });
        row += '</select></div></td>';
    }

    row += '</tr></table>';

    container.append(row);
}

function $updateLogData(action, data) {
    var items = $UpdateState(action, data);
    var container = $("#parameters-content");
    //var parent = $("#data-content");
    var body = '';

    function no_data() {
        return '<tr><td colspan="2"><div class="no-data">'+keywords['No data...']+'</div></tr>';
    }

    container.html('');

    for(var i=0; i < items.parameters.length; i++) {
        var x = items.parameters[i];
        body += '<tr class="parameter-row"><td class="title">TITLE</td><td class="value"><div>VALUE</div></td></tr>'
            .replace(/TITLE/g, (x.title == '...' ? '' : x.title))
            .replace(/VALUE/g, x.value);
    }

    body = '<table border="0">'+(body || no_data())+'</table>';

    container.append(body);

    var container = $("#products-content");
    var products = $_get_obs(data['products']);
    var body = '';

    for(var key in products) {
        var x = products[key];
        var code = x.id;
        var construct = IsStringStartedWith(x.id, 'construct');
        var title = x.title || (construct ? keywords['Base article'] : keywords['Price article']);
        if (items.codes.indexOf(code) == -1) {
            items.products.push({
                'article' : x['article'] || '',
                'price'   : x['price'] || '',
                'title'   : title,
                'value'   : x.value,
                'code'    : code
            });
        }
        else if (x.title && !construct && code in items.ids) {
            var index = items.ids[code];
            if (!isNaN(index) && index > -1 && index < items.products.length && x.title != items.products[index].title)
                items.products[index].title = x.title;
        }
    }

    items.products.sort(function(a,b) { return (a.code > b.code) ? -1 : ((b.code > a.code) ? 1 : 0); });

    container.html('');

    for(var i=0; i < items.products.length; i++) {
        var x = items.products[i];
        var article = x['article'];
        var price = x['price'];
        var title = x.title;
        var value = $_check_number(x.value).toString();
        var code = x.code;
        body += '<tr class="product-row"><td colspan="3"><div class="article">CODE</div></td></tr>'
            .replace(/CODE/g, code);
        body += '<tr class="product-row">';
        body += '<td class="title">TITLE</td><td class="value"><div>VALUE</div></td>'
            .replace(/TITLE/g, title)
            .replace(/VALUE/g, value == 'true' ? keywords['yes'] : (value == 'false' ? keywords['no'] : value));
        if (price && price != n_a)
            body += '<td class="price"><div>PRICE</div></td>'
                .replace(/PRICE/g, price && price != n_a ? '=&nbsp;'+price : '');
        else
            body += '<td></td>';
        body += '</tr>';
    }

    body = '<table cellspacing="0" border="0">'+(body || no_data())+'</table>';

    container.append(body);

    $ShowMenu(selected_data_menu_id);
    $ResizePageWindow(true);
}

function $updateStatistics(data) {
    var container = $("#statistics-content");
    var body = '<td id="ID" class="dataCLASS">VALUE</td>';
    var row = '';

    if (!data) return;

    container.html('');

    row += '<table id="statistics-form" cellspacing="0" border="0">';

    for(var i=0; i < data.length; i++) {
        var id = data[i][0];
        var items = data[i][1];
        row += '<tr id="row:NUM" class="statistics-row CLASS">'
            .replace(/NUM/g, items[0])
            .replace(/CLASS/g, i%2 ? 'odd' : 'even');
        items.forEach(function(x, index) {
            row += body
                .replace(/ID/g, (index == 0 ? 'id:'+id : 'data:'+id+'-'+statistics_columns[index]))
                .replace(/CLASS/g, (index == 0 ? ' row_id' : ''))
                .replace(/VALUE/g, x);
        });
        row += '</tr>';
    }

    row += '</table>';

    container.append(row);
}
