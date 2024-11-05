from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Ticket(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(verbose_name="Описание")

    date = models.DateField()

    def get_image(self):
        if self.image:
            return self.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
        db_table = "tickets"


class Event(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Сотрудник", null=True, related_name='moderator')

    name = models.CharField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True)

    def __str__(self):
        return "Получение №" + str(self.pk)

    def get_tickets(self):
        return [
            setattr(item.ticket, "value", item.value) or item.ticket
            for item in TicketEvent.objects.filter(event=self)
        ]

    class Meta:
        verbose_name = "Получение"
        verbose_name_plural = "Получения"
        ordering = ('-date_formation',)
        db_table = "events"


class TicketEvent(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "ticket_event"
        constraints = [
            models.UniqueConstraint(fields=['ticket', 'event'], name="ticket_event_constraint")
        ]