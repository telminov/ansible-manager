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

@deleteElem = (elem) ->
  elem.prependTo("#deleted-variables");
  nameElements = elem.find('input:first').attr('name').split('-')
  deleteName = "#{nameElements[0]}-#{nameElements[1]}-DELETE"
  elem.append("<input id='id_#{deleteName}' name='#{deleteName}' type='text' value='on'>")


@deleteAllForms = ->
  for v in $('.variable')
    deleteElem(v)
