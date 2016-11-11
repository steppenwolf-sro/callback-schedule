from django.conf.urls import url

from callback_request.api_views import CreateCallbackRequest

urlpatterns = [
    url(r'^create\.json$', CreateCallbackRequest.as_view()),
]
