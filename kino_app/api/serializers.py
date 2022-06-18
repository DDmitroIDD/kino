from rest_framework import serializers
from taggit.models import Tag
from taggit_serializer.serializers import TagListSerializerField

from kino_app.models import Customer, CinemaHall, MovieSession, Ticket


class CustomerSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    def create(self, validated_data):
        if self.context['request'].user.is_anonymous:
            if validated_data['password'] != validated_data.pop('password2'):
                raise serializers.ValidationError('Passwords do not match!')
            user = Customer.objects.create_user(**validated_data)

            return user
        raise serializers.ValidationError('You are already registered!')

    class Meta:
        model = Customer
        fields = ("id", "username", "password", "password2", "money_spent")
        read_only_fields = ("id", "money_spent", "is_staff",)


class MovieSessionSerializer(serializers.ModelSerializer):
    tag = TagListSerializerField(required=True)
    show_hall = serializers.SlugRelatedField(slug_field="hall_name", queryset=CinemaHall.objects.all())

    class Meta:
        model = MovieSession
        fields = ("id", "hall", "movie", "qyt", "start_datetime", "end_datetime", "price",
                  "tag", "image", "slug", "description", )
        read_only_fields = ("id", )
        lookup_field = "slug"
        extra_kwargs = {
            "url": {"lookup_field": "slug"}
        }


class CinemaHallSerializer(serializers.ModelSerializer):
    movies = MovieSessionSerializer(many=True, required=False)
    hall_size = serializers.IntegerField(required=True)

    class Meta:
        model = CinemaHall
        fields = ("id", "hall_name", "hall_size", "movies")
        read_only_fields = ("id", "movies")

    # def validate(self, attrs):
    #     if self.instance:
    #         cinema_hall_id = self.instance.id
    #         hall_size = self.instance.hall_size
    #         movies = CinemaHall.objects.get(id=cinema_hall_id).movies.filter(free_seats__lt=hall_size)
    #         if movies:
    #             raise serializers.ValidationError(
    #                         {'movies': 'There are purchased tickets in this hall, cannot be changed!'})
    #         hall_size = attrs['hall_size']
    #         CinemaHall.objects.get(id=cinema_hall_id).movies.all().update(free_seats=hall_size)
    #     return attrs


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "customer", "movie", "qt")
        read_only_fields = ("id", )


class ContactSerailizer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()


class TagSerializer(MovieSessionSerializer):

    class Meta:
        model = Tag
        fields = ("name", )
        lookup_field = "name"
        extra_kwargs = {
            "url": {"lookup_field": "name"}
        }
