# urls.py
from django.urls import path
from .views import CreateScheduleView, ListAvailableSchedules, BookScheduleView , ListTransporterBookings

urlpatterns = [
    path('schedule/create/', CreateScheduleView.as_view()),
    path('schedule/available/', ListAvailableSchedules.as_view()),
    path('schedule/book/', BookScheduleView.as_view()),
    path("bookings/", ListTransporterBookings.as_view())
]
