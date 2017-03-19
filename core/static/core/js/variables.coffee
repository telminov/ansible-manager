setTotalNumber = (e, replaced, total) ->
  e.find('input').each ->
        name = $(this).attr('name').replace(replaced, total)
        id = 'id_' + name
        $(this).attr({'name': name, 'id': id})

correctedIds = ->
  $('#variables').find('.variable').each (index, elem) ->
    elem = $(elem)
    current_number = elem.find('input:first').attr('name').split('-')[1]
    setTotalNumber(elem, "-#{current_number}-", "-#{index}-")

@addForm = () ->
    newElement = $('#empty_form').clone(true)
    newElement.removeAttr('id')
    newElement.css("display", "");
    total = $('#id_form-TOTAL_FORMS').val()
    setTotalNumber(newElement, '__prefix__', total)
    correctedIds()
    
    total++
    $('#id_form-TOTAL_FORMS').val(total);
    $('#variables').append(newElement);

@removeElem = (elem) ->
  elem.remove()
  total = $('#id_form-TOTAL_FORMS').val()
  total--
  $('#id_form-TOTAL_FORMS').val(total)
  correctedIds()