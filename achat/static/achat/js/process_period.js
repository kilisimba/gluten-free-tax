
function search_period(triggeringLink) {
    query=[]
    var period = $("select[name='period'] option:selected").val();
    if (period && period != 'All') {
        query.push('period='+period)
    }
    if (query.length == 0) {
        window.location.search = "";
    } else {
        window.location.search = query.join('&')
    }
    window.location.assign(href)
}

function process_period(triggeringLink) {
    return search_period(triggeringLink);
}

