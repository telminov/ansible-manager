from django.conf.urls import url

from core.views import views, host, host_group, task_template, task, rest

urlpatterns = [
    url(r'^$', views.index, name='index'),

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

    url(r'^tasks/$', task.search, name='task_search'),
    url(r'^tasks/create/$', task.create, name='task_create'),
    url(r'^tasks/(?P<pk>\d+)/stop/$', task.stop, name='task_stop'),
    url(r'^tasks/(?P<pk>\d+)/replay/$', task.replay, name='task_replay'),
    url(r'^tasks/(?P<pk>\d+)/log/$', task.log, name='task_log'),

    url(r'^api/task/(?P<task_id>\d+)/logs/$', rest.task_logs, name='rest_task_logs')
]
