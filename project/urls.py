import os
import django.contrib.auth.views

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static


import core.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', django.contrib.auth.views.login,
        {'template_name': 'core/user/login.html', 'redirect_authenticated_user': True},
        name='login'),
    url(r'^logout/', django.contrib.auth.views.logout_then_login, {'login_url': '/login/?next=/'}, name='logout'),

    url(r'^', include(core.urls)),
]

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=os.path.join(settings.BASE_DIR, 'node_modules'))

