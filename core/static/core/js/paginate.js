/**
 * Created by YraganTron on 01.06.17.
 */

$(document).ready(function () {
    $('.custom-paginate').on('change', function (evt) {
        var url = window.location.href;
        if (url.match(/page=/)) {
            url = url.replace(/page=(\d+)/i, 'page=1')
        } else {
            url = url + '&page=1'
        }
        if (url.match(/paginate_by=/)) {
            window.location.href = url.replace(/paginate_by=(-?\d+)/i, 'paginate_by=' + evt.target.value)
        } else {
            window.location.href = url + '&paginate_by=' + evt.target.value
        }

    });

    var pag_by = window.location.href.match(/paginate_by=(-?\d+)/i);

    if (pag_by != null) {
        var val = pag_by[0].match(/-?\d+/);
        if (val != '-1') {
            $('.custom-paginate').val(val[0])
        } else {
            $('.custom-paginate').val("-1")
        }
    }
});