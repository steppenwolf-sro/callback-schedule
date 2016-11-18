from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from callback_caller.views import CallbackCall, CallEntryResult, TokenRequest, DirectCallRequest, DirectCallResult

urlpatterns = [
    url(r'^call/direct/$', DirectCallRequest.as_view(), name='direct_call'),
    url(r'^call/direct/result/$', DirectCallResult.as_view(), name='direct_result'),

    url(r'^call/(?P<id>[^/]+)/$', CallbackCall.as_view(), name='callback_call'),
    url(r'^result/(?P<id>[^/]+)/$', CallEntryResult.as_view(), name='callback_result'),
    url(r'^token\.json$',
        permission_required('callback_caller.change_callbackrequest', raise_exception=True)(TokenRequest.as_view())),
]
