from django.conf.urls import url

from caller.views import CallbackCall, CallbackCallResult

urlpatterns = [
    url(r'^call/(?P<id>[^/]+)/$', CallbackCall.as_view(), name='callback_call'),
    url(r'^result/(?P<id>[^/]+)/$', CallbackCallResult.as_view(), name='callback_result'),
]
