from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Ticket, Event, TicketEvent


def index(request):
    ticket_name = request.GET.get("ticket_name", "")
    tickets = Ticket.objects.filter(status=1)

    if ticket_name:
        tickets = tickets.filter(name__icontains=ticket_name)

    draft_event = get_draft_event()

    context = {
        "ticket_name": ticket_name,
        "tickets": tickets
    }

    if draft_event:
        context["tickets_count"] = len(draft_event.get_tickets())
        context["draft_event"] = draft_event

    return render(request, "tickets_page.html", context)


def add_ticket_to_draft_event(request, ticket_id):
    ticket_name = request.POST.get("ticket_name")
    redirect_url = f"/?ticket_name={ticket_name}" if ticket_name else "/"

    ticket = Ticket.objects.get(pk=ticket_id)

    draft_event = get_draft_event()

    if draft_event is None:
        draft_event = Event.objects.create()
        draft_event.owner = get_current_user()
        draft_event.date_created = timezone.now()
        draft_event.save()

    if TicketEvent.objects.filter(event=draft_event, ticket=ticket).exists():
        return redirect(redirect_url)

    item = TicketEvent(
        event=draft_event,
        ticket=ticket
    )
    item.save()

    return redirect(redirect_url)


def ticket_details(request, ticket_id):
    context = {
        "ticket": Ticket.objects.get(id=ticket_id)
    }

    return render(request, "ticket_page.html", context)


def delete_event(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE events SET status=5 WHERE id = %s", [event_id])

    return redirect("/")


def event(request, event_id):
    if not Event.objects.filter(pk=event_id).exists():
        return redirect("/")

    event = Event.objects.get(id=event_id)
    if event.status == 5:
        return redirect("/")

    context = {
        "event": event,
    }

    return render(request, "event_page.html", context)


def get_draft_event():
    return Event.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()