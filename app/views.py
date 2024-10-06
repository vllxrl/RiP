from django.shortcuts import render

tickets = [
    {
        "id": 1,
        "name": "Пейнтбол",
        "short_description": "«В здоровом теле – здоровый дух»",
        "description": "Мероприятие насыщено весельем, командным духом и яркими красками. Атмосфера соперничества и любимая игра подарят море положительных эмоций, помогут отвлечься от учёбы и дадут возможность отдохнуть.",
        "date": "2 октября",
        "addres": "г. Москва, ул. Новая дорога, д.4с1",
        "image": "http://localhost:9000/images/1.png"
    },

    {
        "id": 2,
        "name": "Картинг",
        "short_description": "«Адреналин против наркотиков»",
        "description": "Это увлекательное и завораживающее действие. Приятная атмосфера и дух соперничества оставили в сердцах участников невероятное количество драйвовых ощущений!",
        "date": "5 ноября",
        "addres": "г. Москва, ул. Шарикоподшипниковская, д.13с89",
        "image": "http://localhost:9000/images/2.png"
    },

    {
        "id": 3,
        "name": "Театр",
        "short_description": "Комедия «Мадам Рубинштейн»",
        "description": "Московский драматический театр имени А.С. Пушкина предлагает студентам совершенно бесплатно посетить весенние спектакли. Сходить в театр – это отличный способ отвлечься от ежедневной суеты и окунуться в мир искусства.",
        "date": "15 декабря",
        "addres": "г. Москва, Тверской бульвар, д.23",
        "image": "http://localhost:9000/images/3.png"
    },

    {
        "id": 4,
        "name": "Матч",
        "short_description": "Спартак 1 – Спартак 2",
        "description": "«ЛУКОЙЛ АРЕНА» в честь своего 10-летия приглашает на большой праздник, главным событием которого станет матч звёзд с участием спартаковцев прошлого и настоящего.",
        "date": "2 октября",
        "addres": "г. Москва, Волоколамское ш., д. 69",
        "image": "http://localhost:9000/images/4.png"
    },

    {
        "id": 5,
        "name": "Музей",
        "short_description": "Выставка «Дали & Пикассо»",
        "description": "Выставка «Дали & Пикассо» – одна из самых больших в мире частных коллекций скульптур Сальвадора Дали и керамики Пабло Пикассо, а также графика. Путевой дворец Василия III.",
        "date": "13 ноября",
        "addres": "г. Москва, ул. Старая Басманная, д.15с3",
        "image": "http://localhost:9000/images/5.png"
    },

    {
        "id": 6,
        "name": "Квиз",
        "short_description": "Викторина по техническим специальностям",
        "description": "Викторина по техническим специальностям — это увлекательное и интеллектуальное соревнование, которое призвано проверить и расширить знания участников в области технических наук. Мероприятие состоится в формате командного турнира, где студенты и преподаватели смогут продемонстрировать свои знания, логику и умение работать в команде.",
        "date": "6 октября",
        "addres": "г. Москва, ул. Нижняя, д.14с2",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_event = {
    "id": 123,
    "status": "Проба",
    "date_created": "12 сентября 2024г",
    "name": "Макаров Алексей Дмитриевич",
    "phone": "+79584561203",
    "tickets": [
        {
            "id": 1,
            "count": 3
        },
        {
            "id": 2,
            "count": 2
        },
        {
            "id": 3,
            "count": 4
        }
    ]
}


def getTicketById(ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket


def getTickets():
    return tickets


def searchTickets(ticket_name):
    res = []

    for ticket in tickets:
        if ticket_name.lower() in ticket["name"].lower():
            res.append(ticket)

    return res


def getDraftEvent():
    return draft_event


def getEventById(event_id):
    return draft_event


def index(request):
    ticket_name = request.GET.get("ticket_name", "")
    tickets = searchTickets(ticket_name) if ticket_name else getTickets()
    draft_event = getDraftEvent()

    context = {
        "tickets": tickets,
        "ticket_name": ticket_name,
        "tickets_count": len(draft_event["tickets"]),
        "draft_event": draft_event
    }

    return render(request, "tickets_page.html", context)


def ticket(request, ticket_id):
    context = {
        "id": ticket_id,
        "ticket": getTicketById(ticket_id),
    }

    return render(request, "ticket_page.html", context)


def event(request, event_id):
    event = getEventById(event_id)
    tickets = [
        {**getTicketById(ticket["id"]), "count": ticket["count"]}
        for ticket in event["tickets"]
    ]

    context = {
        "event": event,
        "tickets": tickets
    }

    return render(request, "event_page.html", context)
