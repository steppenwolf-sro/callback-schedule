from django.conf.urls import url

from callback_request.api_views import CreateCallbackRequest, ManagersAvailabilityView, CallbackRequestAdminView, \
    CallbackRequestAdminDetailView, CallEntryList

urlpatterns = [
    url(r'^create\.json$', CreateCallbackRequest.as_view()),
    url(r'^availability\.json$', ManagersAvailabilityView.as_view()),

    url(r'^manage/requests\.json$', CallbackRequestAdminView.as_view()),
    url(r'^manage/requests/(?P<pk>\d+)\.json$', CallbackRequestAdminDetailView.as_view()),
    url(r'^manage/requests/(?P<pk>\d+)/entries\.json$', CallEntryList.as_view()),
]
