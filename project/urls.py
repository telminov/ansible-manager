import os
import django.contrib.auth.views

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

import core.urls

from core.views.general import permission_denied
from core.views.rest import Metrics

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', django.contrib.auth.views.login,
        {'template_name': 'core/user/login.html', 'redirect_authenticated_user': True},
        name='login'),
    url(r'^logout/', django.contrib.auth.views.logout_then_login, {'login_url': '/login/?next=/'}, name='logout'),
    url(r'^permission_denied/$', permission_denied, name='permission_denied'),
    url(r'^tz_detect/', include('tz_detect.urls')),
    url(r'^metrics', Metrics.as_view(), name='metrics'),
    url(r'^', include(core.urls)),
]

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=os.path.join(settings.BASE_DIR, 'node_modules'))
