from django.conf.urls import url

from core.views import general, host, host_group, task_template, task, ansible_user, rest

urlpatterns = [
    url(r'^$', general.index, name='index'),

    url(r'^hosts/$', host.search, name='host_search'),
    url(r'^hosts/create/$', host.edit, name='host_create'),
    url(r'^hosts/(?P<pk>\d+)/$', host.edit, name='host_update'),
    url(r'^hosts/(?P<pk>\d+)/delete/$', host.delete, name='host_delete'),

    url(r'^host_groups/$', host_group.search, name='host_group_search'),
    url(r'^host_groups/create/$', host_group.edit, name='host_group_create'),
    url(r'^host_groups/(?P<pk>\d+)/$', host_group.edit, name='host_group_update'),
    url(r'^host_groups/(?P<pk>\d+)/delete/$', host_group.delete, name='host_group_delete'),

    url(r'^task_templates/$', task_template.search, name='task_template_search'),
    url(r'^task_templates/create/$', task_template.edit, name='task_template_create'),
    url(r'^task_templates/(?P<pk>\d+)/$', task_template.edit, name='task_template_update'),
    url(r'^task_templates/(?P<pk>\d+)/run/$', task_template.run, name='task_template_run'),
    url(r'^task_templates/(?P<pk>\d+)/delete/$', task_template.delete, name='task_template_delete'),
    url(r'^task_templates/(?P<pk>\d+)/inventory/$', task_template.inventory, name='task_template_inventory'),
    url(r'^task_templates/(?P<pk>\d+)/repeat_settings/$', task_template.repeat_settings, name='task_template_repeat_settings'),

    url(r'^tasks/$', task.search, name='task_search'),
    url(r'^tasks/create/$', task.create, name='task_create'),
    url(r'^tasks/(?P<pk>\d+)/stop/$', task.stop, name='task_stop'),
    url(r'^tasks/(?P<pk>\d+)/replay/$', task.replay, name='task_replay'),
    url(r'^tasks/(?P<pk>\d+)/log/$', task.log, name='task_log'),
    url(r'^tasks/(?P<pk>\d+)/inventory/$', task.inventory, name='task_inventory'),

    url(r'^ansible_users/$', ansible_user.search, name='ansible_user_search'),
    url(r'^ansible_users/create/$', ansible_user.edit, name='ansible_user_create'),
    url(r'^ansible_users/(?P<pk>\d+)/$', ansible_user.edit, name='ansible_user_update'),
    url(r'^ansible_users/(?P<pk>\d+)/delete/$', ansible_user.delete, name='ansible_user_delete'),

    url(r'^api/task/(?P<task_id>\d+)/logs/$', rest.task_logs, name='rest_task_logs')
]
