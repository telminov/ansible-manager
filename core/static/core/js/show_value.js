
$(document).ready(function () {
    $('.show_value').on('click', function (e) {
        var num_formset = e.target.id.split('-')[1];
        var id_formset = '#' + 'id_form-' + num_formset + '-value';
        if ($(id_formset).attr('type') == 'password') {
            $(this).text('Hide Value');
            $(id_formset).attr('type', 'text');
        } else {
            $(this).text('Show Value');
            $(id_formset).attr('type', 'password');
        }
    })

});
