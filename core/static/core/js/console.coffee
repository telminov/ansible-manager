scrolling = true

scrollConsole = ->
  if scrolling
    console = $('.console')
    logs = $('.logs')
    console.animate({ scrollTop: logs.height() }, 0)
scrollConsole()

setLogs = (logs) ->
  for log in logs
    message = formatOutput(log.output or log.message)
    $('.logs').append("<p class='line log-#{log.status}'>#{message}</p>")
    scrollConsole()

    if log.status in ['fail', 'stopped', 'completed']
      @task_running = false
      $('#stop').hide()
      $('#replay').show()

@getLogs = (last_id) ->
  if not task_running
    return

  url = GET_LOGS_URL

  if not last_id and last_log_id
    last_id = last_log_id

  if last_id
    url = "#{url}?last_log_id=#{last_id}"

  $.get(url, (data) ->
    if data.length > 0
      last_id = data[data.length-1].id
      setLogs(data)

    setTimeout ( ->
      getLogs(last_id)
      ), 1000
  )

getLogs()


formatOutput = (message) ->
  return message.replace(/\n/g, '<br>').replace(/\s/g, '&nbsp;')

$('.line').each (i, element) ->
  e = $(element)
  e.html(formatOutput(e.html()))


