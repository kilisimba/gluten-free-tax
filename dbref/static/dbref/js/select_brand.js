
function search_description(triggeringLink) {
    query=[]
    var location = window.location.search.substring(1);
    var vars = location.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] === 'achat') {
            var achat = decodeURIComponent(pair[1]).split("=");
            query.push('achat='+achat)
        }
    }
    var description = $("input[name='searchDescription']").val();
    if (description != "") { query.push('description='+description) }
    var search = $("input[name='searchBrand']").val();
    if (search != "") { query.push('search='+search) }
    var brand = $("select[name='Brands'] option:selected").val();
    if (brand) { query.push('brand='+brand) }
    window.location.search = '&'+query.join('&')
    window.location.assign(href)
}

/*
function clear_description(triggeringLink) {
    query=[]
    var location = window.location.search.substring(1);
    var vars = location.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] === 'achat') {
            var achat = decodeURIComponent(pair[1]).split("=");
            query.push('achat='+achat)
        }
    }
    var description = $("input[name='searchDescription']").val();
    if (description == "") { return; }
    var search = $("input[name='searchBrand']").val();
    if (search != "") { query.push('search='+search) }
    var brand = $("input[name='Brands']").val();
    if (brand) { query.push('brand='+brand) }
    window.location.search = '&'+query.join('&')
    window.location.assign(href)
}

function clear_selection(triggeringLink) {
    query=[]
    var location = window.location.search.substring(1);
    var vars = location.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] === 'achat') {
            var achat = decodeURIComponent(pair[1]).split("=");
            query.push('achat=')
        }
    }
    var description = $("input[name='searchDescription']").val();
    if (description != "") { query.push('description='+description) }
    var search = $("input[name='searchBrand']").val();
    var brand = $("select[name='Brands'] option:selected").val();
    if ( (brand === undefined) && (search === undefined) ) { return; }
    window.location.search = '&'+query.join('&')
    window.location.assign(href)
}
*/

function SelectBrand(triggeringLink) {
    return search_description(triggeringLink);
}

$(function() {
    $("input[name='searchBrand']").keyup(function(){
        var brand = $(this).val().toLowerCase();
        $("select[name='Brands'] option").each(function(idx){
            if ($(this).text().toLowerCase().search(brand) < 0) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });
    $("input[name='searchDescription']").click(function(){
        var description = $(this).val().toLowerCase();
    });
});

$(document).ready ( function(){
    var location = window.location.search.substring(1);
    var vars = location.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] === 'search') {
            var brand = decodeURIComponent(pair[1]).split("=");
            $("select[name='Brands'] option").each(function(idx){
                if ($(this).text().toLowerCase().search(brand) < 0) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        }
    }
} );
