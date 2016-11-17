from django.conf.urls import url

from callback_request.api_views import CreateCallbackRequest, ManagersAvailabilityView

urlpatterns = [
    url(r'^create\.json$', CreateCallbackRequest.as_view()),
    url(r'^availability\.json$', ManagersAvailabilityView.as_view()),
]
