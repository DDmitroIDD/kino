from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from kino_app.creating_movie_sessions import create_dates
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
        fields = ("id", "username", "password", "password2", "money_spent", "is_staff", "avatar")
        read_only_fields = ("id", "money_spent", "is_staff",)


class TicketSerializer(serializers.ModelSerializer):
    qt = serializers.IntegerField(required=True)
    spent = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(slug_field="username", queryset=Customer.objects.all(), required=False)

    class Meta:
        model = Ticket
        fields = ("id", "customer", "movie", "qt", "spent", "user")
        read_only_fields = ("id", "spent", "user",)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    @staticmethod
    def get_spent(obj):
        return obj.customer.money_spent


class MovieSessionSerializer(TaggitSerializer, serializers.ModelSerializer):
    tag = TagListSerializerField()
    hall = serializers.SlugRelatedField(slug_field="hall_name", queryset=CinemaHall.objects.all())
    start_datetime = serializers.DateTimeField(required=True)
    end_datetime = serializers.DateTimeField(required=True)

    class Meta:
        model = MovieSession
        fields = ("id", "hall", "movie", "qyt", "start_datetime", "end_datetime", "price",
                  "tag", "image", "slug", "description", )
        read_only_fields = ("id", "qyt", )
        lookup_field = "slug"
        extra_kwargs = {
            "url": {"lookup_field": "slug"}
        }

    def validate(self, attrs):
        start_datetime = attrs.get('start_datetime', False)
        end_datetime = attrs.get('end_datetime', False)
        if not self.instance:
            if start_datetime > end_datetime:
                raise serializers.ValidationError({'datetime_error': 'Your start time starting after end time!'})
            try:
                hall = attrs.get('hall')
                sessions_in_hall = MovieSession.objects.filter(hall=hall)
                dates = create_dates(attrs, sessions_in_hall)
            except serializers.ValidationError:
                raise serializers.ValidationError({'movie_sessions_error': 'There is movie no this time in this hall!'})
            start, end = dates.pop(0)
            attrs['start_datetime'] = start
            attrs['end_datetime'] = end
            slug = attrs.get('movie').replace(' ', '_')
            movies = (
            MovieSession(hall_id=attrs.get('hall').id, movie=attrs.get('movie'), qyt=attrs.get('hall').hall_size,
                         price=attrs.get('price'), slug=slug,
                         start_datetime=start, end_datetime=end,
                         description=attrs.get('description'), image=attrs.get('image'))
                        for start, end in dates)
            new_movies = MovieSession.objects.bulk_create(movies)
            tags = attrs.get('tag')
            for movie in new_movies:
                for t in tags:
                    movie.tag.add(t)

        return attrs


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


class ContactSerailizer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()


class TagSerializer(MovieSessionSerializer):
    class Meta:
        model = Tag
        fields = ("name",)
        lookup_field = "name"
        extra_kwargs = {
            "url": {"lookup_field": "name"}
        }
