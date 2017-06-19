/**
 * Created by YraganTron on 01.06.17.
 */

$(document).ready(function () {
    $('.custom-paginate').on('change', function (evt) {
        window.location.href = window.location.href.split('/').slice(0, 4).join('/') + '/' + '?paginate_by=' + evt.target.value
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