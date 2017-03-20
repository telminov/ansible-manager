from django.conf.urls import url

from core.views import views
from core.views import host
from core.views import host_group
from core.views import task_template

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
    url(r'^task_templates/(?P<pk>\d+)/delete/$', task_template.delete, name='task_template_delete'),
]
