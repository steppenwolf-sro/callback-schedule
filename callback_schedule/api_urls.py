from django.conf.urls import url

from callback_schedule.api_views import CallbackManagerList, ScheduleList

urlpatterns = [
    url(r'^managers\.json$', CallbackManagerList.as_view(), name='managers'),
    url(r'^managers/(?P<pk>\d+)/schedule\.json$', ScheduleList.as_view(), name='schedule'),
]
