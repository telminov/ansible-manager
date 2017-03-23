scrolling = true

scrollConsole = ->
  if scrolling
    console = $('.console')
    logs = $('.logs')
    console.animate({ scrollTop: logs.height() }, 0)
scrollConsole()

setLogs = (logs) ->
  for log in logs
    if log.status == 'in_progress'
      renderMessage(log.output or log.message, log.status)
    else
      renderMessage(log.message, log.status)
      if log.output
        renderMessage(log.output, log.status)

    if log.task_status in ['fail', 'stopped', 'completed']
      @task_running = false
      $('#stop').hide()
      $('#replay').show()


renderMessage = (message, status) ->
  message = formatOutput(message)
  $('.logs').append("<p class='line log-#{status}'>#{message}</p>")
  scrollConsole()

@getLogs = (force, last_id) ->
  if not force and not task_running
    return

  url = GET_LOGS_URL

  if not last_id and last_log_id
    last_id = last_log_id

  if not force and last_id
    url = "#{url}?last_log_id=#{last_id}"

  $.get(url, (data) ->
    if data.length > 0
      last_id = data[data.length-1].id
      setLogs(data)

    setTimeout ( ->
      getLogs(false, last_id)
      ), 1000
  )

getLogs(true)


formatOutput = (message) ->
  return message.replace(/\n/g, '<br>').replace(/\s/g, '&nbsp;')

$('.line').each (i, element) ->
  e = $(element)
  e.html(formatOutput(e.html()))


