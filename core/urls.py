from django.conf.urls import url

from core.views import views
from core.views import hosts

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^permission_denied/$', views.permission_denied, name='permission_denied'),

    url(r'^hosts/$', hosts.search, name='host_search'),
    url(r'^hosts/create/$', hosts.create, name='host_create'),
    url(r'^hosts/(?P<pk>\d+)/$', hosts.update, name='host_update'),
    url(r'^hosts/(?P<pk>\d+)/delete/$', hosts.delete, name='host_edit'),
]
