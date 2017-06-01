/**
 * Created by YraganTron on 01.06.17.
 */

$(document).ready(function () {
    $('.custom-paginate').on('change', function (evt) {
        console.log(evt);
        console.log(evt.target.form.id);
        $('#' + evt.target.form.id).submit();
    })
});