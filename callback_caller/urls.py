from django.conf.urls import url

from callback_caller.views import CallbackCall, CallEntryResult

urlpatterns = [
    url(r'^call/(?P<id>[^/]+)/$', CallbackCall.as_view(), name='callback_call'),
    url(r'^result/(?P<id>[^/]+)/$', CallEntryResult.as_view(), name='callback_result'),
]
