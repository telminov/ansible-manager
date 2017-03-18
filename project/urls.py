import os

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static


import core.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(core.urls)),
]

if settings.DEBUG:
    urlpatterns += static('node_modules', document_root=os.path.join(settings.BASE_DIR, 'node_modules'))

