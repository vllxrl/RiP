from rest_framework import serializers

from .models import *


class TicketsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, ticket):
        if ticket.image:
            return ticket.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Ticket
        fields = ("id", "name", "status", "date", "image")


class TicketSerializer(TicketsSerializer):
    class Meta(TicketsSerializer.Meta):
        model = Ticket
        fields = TicketsSerializer.Meta.fields + ("description", )


class EventsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class EventSerializer(EventsSerializer):
    tickets = serializers.SerializerMethodField()

    def get_tickets(self, event):
        items = TicketEvent.objects.filter(event=event)
        return [TicketItemSerializer(item.ticket, context={"count": item.count}).data for item in items]


class TicketItemSerializer(TicketSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, ticket):
        return self.context.get("count")

    class Meta(TicketSerializer.Meta):
        fields = "__all__"


class TicketEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketEvent
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
