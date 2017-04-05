IN_PROGRESS = 'in_progress'
COMPLETED = 'completed'
STOPPED = 'stopped'
FAIL = 'fail'
WAIT = 'wait'

STATUSES = [IN_PROGRESS, COMPLETED, STOPPED, FAIL, WAIT]
STATUS_CHOICES = [(status, status) for status in STATUSES]
NOT_RUN_STATUSES = [COMPLETED, STOPPED, FAIL]
RUN_STATUSES = [IN_PROGRESS, WAIT]

VERBOSE_CHOICES = (
    ('', 'silent'),
    ('v', 'standard'),
    ('vv', 'detail'),
    ('vvv', 'very detail'),
    ('vvvv', 'all'),
)
