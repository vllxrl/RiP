from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('tickets/<int:ticket_id>/', ticket),
    path('events/<int:event_id>/', event),
]