import re
import django.utils.deprecation

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware(django.utils.deprecation.MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exceptions = tuple(re.compile(url) for url in settings.LOGIN_REQUIRED_URLS_EXCEPTIONS)

    def process_view(self, request, *args, **kwargs):
        if not request.user.is_authenticated():

            for url in self.exceptions:
                if url.match(request.path):
                    return None

            return redirect('{0}?next={1}'.format(
                reverse('login'), request.path
            ))

        return None
