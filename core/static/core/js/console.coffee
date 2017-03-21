scrolling = true

scrollConsole = ->
  if scrolling
    console = $('.console')
    logs = $('.logs')
    console.animate({ scrollTop: logs.height() }, 1000)
scrollConsole()

setLogs = (logs) ->
  for log in logs
    message = log.output or log.message
    $('.logs').append("<p class='line log-#{log.status}'>#{log.id} #{message}</p>")

@getLogs = (last_id) ->
  if task_running
    if not last_id
      last_id = last_log_id

    url = GET_LOGS_URL
    if last_id
      url = "#{url}?last_log_id=#{last_id}"

    $.get(url, (data) ->
      scrollConsole()
      if data.length > 0
        last_id = data[data.length-1].id
        setLogs(data)

      setTimeout(getLogs(last_id), 1000)
    )

getLogs()
