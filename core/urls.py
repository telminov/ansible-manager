from django.conf.urls import url

from core.views import views
from core.views import hosts

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^permission_denied/$', views.permission_denied, name='permission_denied'),
    # url(r'^hosts/$', hosts.search, name='host_list'),

]
