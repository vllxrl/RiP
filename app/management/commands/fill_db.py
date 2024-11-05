from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_tickets():
    Ticket.objects.create(
        name="Пейнтбол",
        description="Пейнтбо́л — командная игра с применением маркеров, стреляющих шариками с краской, разбивающимися при ударе о препятствие и окрашивающими его. Существуют две основные разновидности пейнтбола: спортивный и тактический.",
        date=random_date(),
        image="1.png"
    )

    Ticket.objects.create(
        name="Картинг",
        description="Ка́ртинг — вид спорта и развлечения, гонки на картах — простейших гоночных автомобилях без кузова. Скорость карта может достигать 260 км/ч.",
        date=random_date(),
        image="2.png"
    )

    Ticket.objects.create(
        name="Театр",
        description="Московский драматический театр имени А.С. Пушкина предлагает студентам совершенно бесплатно посетить весенние спектакли. Сходить в театр – это отличный способ отвлечься от ежедневной суеты и окунуться в мир искусства.",
        date=random_date(),
        image="3.png"
    )

    Ticket.objects.create(
        name="Матч",
        description="Состязание между двумя или несколькими спортсменами, командами; как элемент турнирной системы организации соревнований или самостоятельное соревнование.",
        date=random_date(),
        image="4.png"
    )

    Ticket.objects.create(
        name="Музей",
        description="Музе́й — учреждение, занимающееся сбором, изучением, хранением и экспонированием предметов — памятников естественной истории, материальной и духовной культуры, а также просветительской и популяризаторской деятельностью.",
        date=random_date(),
        image="5.png"
    )

    Ticket.objects.create(
        name="Квиз",
        description="Виктори́на — игра, заключающаяся в ответах на устные или письменные вопросы из различных областей знания. Викторины в основном отличаются друг от друга правилами, определяющими очерёдность хода, тип и сложность вопроса, порядок определения победителей.",
        date=random_date(),
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_events():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    tickets = Ticket.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_event(status, tickets, owner, moderators)

    add_event(1, tickets, users[0], moderators)
    add_event(2, tickets, users[0], moderators)

    print("Заявки добавлены")


def add_event(status, tickets, owner, moderators):
    event = Event.objects.create()
    event.status = status

    if status in [3, 4]:
        event.moderator = random.choice(moderators)
        event.date_complete = random_date()
        event.date_formation = event.date_complete - random_timedelta()
        event.date_created = event.date_formation - random_timedelta()
    else:
        event.date_formation = random_date()
        event.date_created = event.date_formation - random_timedelta()

    if status == 3:
        event.phone = calc()

    event.name = "Макаров Алексей Дмитриевич"

    event.owner = owner

    for ticket in random.sample(list(tickets), 3):
        item = TicketEvent(
            event=event,
            ticket=ticket,
            count=random.randint(1, 10)
        )
        item.save()

    event.save()


def calc():
    allowed_numbers = '658034'
    indx = '+7916'
    for i in range(6):
        indx += allowed_numbers[random.randint(0, len(allowed_numbers) - 1)]
    return indx


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_tickets()
        add_events()
