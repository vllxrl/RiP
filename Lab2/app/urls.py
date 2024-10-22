from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('tickets/<int:ticket_id>/', ticket_details, name="ticket_details"),
    path('tickets/<int:ticket_id>/add_to_event/', add_ticket_to_draft_event, name="add_ticket_to_draft_event"),
    path('events/<int:event_id>/delete/', delete_event, name="delete_event"),
    path('events/<int:event_id>/', event)
]
