from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/tickets/', search_tickets),  # GET
    path('api/tickets/<int:ticket_id>/', get_ticket_by_id),  # GET
    path('api/tickets/<int:ticket_id>/update/', update_ticket),  # PUT
    path('api/tickets/<int:ticket_id>/update_image/', update_ticket_image),  # POST
    path('api/tickets/<int:ticket_id>/delete/', delete_ticket),  # DELETE
    path('api/tickets/create/', create_ticket),  # POST
    path('api/tickets/<int:ticket_id>/add_to_event/', add_ticket_to_event),  # POST

    # Набор методов для заявок
    path('api/events/', search_events),  # GET
    path('api/events/<int:event_id>/', get_event_by_id),  # GET
    path('api/events/<int:event_id>/update/', update_event),  # PUT
    path('api/events/<int:event_id>/update_status_user/', update_status_user),  # PUT
    path('api/events/<int:event_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/events/<int:event_id>/delete/', delete_event),  # DELETE

    # Набор методов для м-м
    path('api/events/<int:event_id>/update_ticket/<int:ticket_id>/', update_ticket_in_event),  # PUT
    path('api/events/<int:event_id>/delete_ticket/<int:ticket_id>/', delete_ticket_from_event),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
