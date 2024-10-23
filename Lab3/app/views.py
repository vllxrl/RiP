import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_event():
    return Event.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_tickets(request):
    ticket_name = request.GET.get("ticket_name", "")

    tickets = Ticket.objects.filter(status=1)

    if ticket_name:
        tickets = tickets.filter(name__icontains=ticket_name)

    serializer = TicketSerializer(tickets, many=True)

    draft_event = get_draft_event()

    resp = {
        "tickets": serializer.data,
        "tickets_count": len(serializer.data),
        "draft_event": draft_event.pk if draft_event else None
    }

    return Response(resp)


@api_view(["GET"])
def get_ticket_by_id(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)
    serializer = TicketSerializer(ticket, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_ticket(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    image = request.data.get("image")
    if image is not None:
        ticket.image = image
        ticket.save()

    serializer = TicketSerializer(ticket, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_ticket(request):
    Ticket.objects.create()

    tickets = Ticket.objects.filter(status=1)
    serializer = TicketSerializer(tickets, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_ticket(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.status = 2
    ticket.save()

    tickets = Ticket.objects.filter(status=1)
    serializer = TicketSerializer(tickets, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_ticket_to_event(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    draft_event = get_draft_event()

    if draft_event is None:
        draft_event = Event.objects.create()
        draft_event.owner = get_user()
        draft_event.date_created = timezone.now()
        draft_event.save()

    if TicketEvent.objects.filter(event=draft_event, ticket=ticket).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = TicketEvent.objects.create()
    item.event = draft_event
    item.ticket = ticket
    item.save()

    serializer = EventSerializer(draft_event)
    return Response(serializer.data["tickets"])


@api_view(["POST"])
def update_ticket_image(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    image = request.data.get("image")
    if image is not None:
        ticket.image = image
        ticket.save()

    serializer = TicketSerializer(ticket)

    return Response(serializer.data)


@api_view(["GET"])
def search_events(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    events = Event.objects.exclude(status__in=[1, 5])

    if status > 0:
        events = events.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        events = events.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        events = events.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = EventsSerializer(events, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_event_by_id(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)
    serializer = EventSerializer(event, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_event(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)
    serializer = EventSerializer(event, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)

    if event.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event.status = 2
    event.date_formation = timezone.now()
    event.save()

    serializer = EventSerializer(event, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event = Event.objects.get(pk=event_id)

    if event.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event.date_complete = timezone.now()
    event.status = request_status
    event.moderator = get_moderator()
    event.save()

    serializer = EventSerializer(event, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_event(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)

    if event.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event.status = 5
    event.save()

    serializer = EventSerializer(event, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_ticket_from_event(request, event_id, ticket_id):
    if not TicketEvent.objects.filter(event_id=event_id, ticket_id=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = TicketEvent.objects.get(event_id=event_id, ticket_id=ticket_id)
    item.delete()

    event = Event.objects.get(pk=event_id)

    serializer = EventSerializer(event, many=False)
    tickets = serializer.data["tickets"]

    if len(tickets) == 0:
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(tickets)


@api_view(["PUT"])
def update_ticket_in_event(request, event_id, ticket_id):
    if not TicketEvent.objects.filter(ticket_id=ticket_id, event_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = TicketEvent.objects.get(ticket_id=ticket_id, event_id=event_id)

    serializer = TicketEventSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)