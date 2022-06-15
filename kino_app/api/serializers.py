from rest_framework import serializers

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
            if validated_data['password'] != validated_data['password2']:
                raise serializers.ValidationError('Passwords do not match!')
            user = Customer.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
            )

            return user
        raise serializers.ValidationError('You are already registered!')

    class Meta:
        model = Customer
        fields = ("id", "username", "password", "password2", "money_spent")
        read_only_fields = ("id", "money_spent", )


class CinemaHallSerializer(serializers.ModelSerializer):

    class Meta:
        model = CinemaHall
        fields = ("id", "hall_name", "hall_size", )
        read_only_fields = ("id", )


class MovieSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MovieSession
        fields = ("id", "hall", "movie", "qyt", "start_datetime", "end_datetime", "price")
        read_only_fields = ("id", )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "customer", "movie", "qt")
        read_only_fields = ("id", )
