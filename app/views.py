import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_event(request):
    user = identity_user(request)

    if user is None:
        return None

    event = Event.objects.filter(owner=user).filter(status=1).first()

    return event


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_tickets(request):
    ticket_name = request.GET.get("ticket_name", "")

    tickets = Ticket.objects.filter(status=1)

    if ticket_name:
        tickets = tickets.filter(name__icontains=ticket_name)

    serializer = TicketsSerializer(tickets, many=True)

    draft_event = get_draft_event(request)

    resp = {
        "tickets": serializer.data,
        "draft_event_id": draft_event.pk if draft_event else None
    }

    return Response(resp)


@api_view(["GET"])
def get_ticket_by_id(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)
    serializer = TicketSerializer(ticket)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_ticket(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    serializer = TicketSerializer(ticket, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_ticket(request):
    serializer = TicketSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Ticket.objects.create(**serializer.validated_data)

    tickets = Ticket.objects.filter(status=1)
    serializer = TicketSerializer(tickets, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_ticket(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.status = 2
    ticket.save()

    ticket = Ticket.objects.filter(status=1)
    serializer = TicketSerializer(ticket, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_ticket_to_event(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    draft_event = get_draft_event(request)

    if draft_event is None:
        draft_event = Event.objects.create()
        draft_event.date_created = timezone.now()
        draft_event.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_ticket_image(request, ticket_id):
    if not Ticket.objects.filter(pk=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ticket = Ticket.objects.get(pk=ticket_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    ticket.image = image
    ticket.save()

    serializer = TicketSerializer(ticket)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_events(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    events = Event.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        events = events.filter(owner=user)

    if status_id > 0:
        events = events.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        events = events.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        events = events.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = EventsSerializer(events, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_event_by_id(request, event_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)
    serializer = EventSerializer(event)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=EventSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_event(request, event_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)
    serializer = EventSerializer(event, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, event_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)

    if event.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event.status = 2
    event.date_formation = timezone.now()
    event.save()

    serializer = EventSerializer(event)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event = Event.objects.get(pk=event_id)

    if event.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        event.phone = calc()

    event.status = request_status
    event.date_complete = timezone.now()
    event.moderator = identity_user(request)
    event.save()

    serializer = EventSerializer(event)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_event(request, event_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    event = Event.objects.get(pk=event_id)

    if event.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    event.status = 5
    event.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_ticket_from_event(request, event_id, ticket_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not TicketEvent.objects.filter(event_id=event_id, ticket_id=ticket_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = TicketEvent.objects.get(event_id=event_id, ticket_id=ticket_id)
    item.delete()

    event = Event.objects.get(pk=event_id)

    serializer = EventSerializer(event)
    tickets = serializer.data["tickets"]

    return Response(tickets)


@swagger_auto_schema(method='PUT', request_body=TicketEventSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_ticket_in_event(request, event_id, ticket_id):
    user = identity_user(request)

    if not Event.objects.filter(pk=event_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not TicketEvent.objects.filter(ticket_id=ticket_id, event_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = TicketEvent.objects.get(ticket_id=ticket_id, event_id=event_id)

    serializer = TicketEventSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
