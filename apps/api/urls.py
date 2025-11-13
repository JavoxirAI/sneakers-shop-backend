from django.urls import path

from apps.api.views import health_check

app_name = 'api'

urlpatterns = [
    path('health', health_check, name='health'),
]