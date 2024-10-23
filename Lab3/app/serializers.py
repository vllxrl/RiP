from rest_framework import serializers

from .models import *


class TicketSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, ticket):
        if ticket.image:
            return ticket.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Ticket
        fields = "__all__"


class TicketItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_image(self, ticket):
        if ticket.image:
            return ticket.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def get_value(self, ticket):
        return self.context.get("value")

    class Meta:
        model = Ticket
        fields = ("id", "name", "image", "value")


class EventSerializer(serializers.ModelSerializer):
    tickets = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, event):
        return event.owner.username

    def get_moderator(self, event):
        if event.moderator:
            return event.moderator.username
            
    def get_tickets(self, event):
        items = TicketEvent.objects.filter(event=event)
        return [TicketItemSerializer(item.ticket, context={"value": item.value}).data for item in items]

    class Meta:
        model = Event
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, event):
        return event.owner.username

    def get_moderator(self, event):
        if event.moderator:
            return event.moderator.username

    class Meta:
        model = Event
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
