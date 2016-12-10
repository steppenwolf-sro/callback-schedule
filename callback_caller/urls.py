from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from callback_caller.views import CallbackCall, CallEntryResult, TokenRequest, DirectCallRequest, DirectCallResult, \
    DirectBackCallRequest, ClientStatusCallback

urlpatterns = [
    url(r'^call/direct/$', DirectCallRequest.as_view(), name='direct_call'),
    url(r'^call/direct/result/(?P<id>[^/]+)/$', DirectCallResult.as_view(), name='direct_result'),
    url(r'^call/direct_back/$', DirectBackCallRequest.as_view(), name='direct_back_call'),

    url(r'^client/(?P<id>[^/]+)/$', ClientStatusCallback.as_view(), name='callback_client_callback'),
    url(r'^call/(?P<id>[^/]+)/$', CallbackCall.as_view(), name='callback_call'),
    url(r'^result/(?P<id>[^/]+)/$', CallEntryResult.as_view(), name='callback_result'),
    url(r'^token\.json$',
        permission_required('callback_caller.change_callbackrequest', raise_exception=True)(TokenRequest.as_view())),
]
