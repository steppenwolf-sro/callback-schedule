from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('callback_schedule.api_urls', namespace='callback_schedule')),
    url(r'^', include('callback_request.api_urls', namespace='callback_request')),
    url(r'^', include('callback_caller.urls', namespace='callback_caller')),
]
