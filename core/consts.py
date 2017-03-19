IN_PROGRESS = 'in_progress'
COMPLETED = 'completed'
STOPPED = 'stopped'
FAIL = 'fail'
WAIT = 'wait'

STATUSES = [IN_PROGRESS, COMPLETED, STOPPED, FAIL, WAIT]
STATUS_CHOICES = [(status, status) for status in STATUSES]

