import datetime
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.cache import cache

class ActiveUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            now_time = now()
            cache.set(f'seen_{request.user.id}', now_time, 60 * 5)
