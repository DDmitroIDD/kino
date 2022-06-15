from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from django.utils import timezone


class Customer(AbstractUser):
    money_spent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Username: {self.username}\nMoney spent: {self.money_spent}'


class CinemaHall(models.Model):
    hall_name = models.CharField(max_length=100)
    hall_size = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'Hall: {self.hall_name}\nSize: {self.hall_size}'


class MovieSession(models.Model):
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='movie_sessions')
    movie = models.CharField(max_length=20)
    qyt = models.PositiveSmallIntegerField()
    start_datetime = models.DateTimeField(default=timezone.now())
    end_datetime = models.DateTimeField(default=timezone.now())
    price = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'Hall: {self.hall.hall_name}\nMovie: {self.movie}\nPrice: {self.price}'


class Ticket(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_tickets')
    movie = models.ForeignKey(MovieSession, on_delete=models.CASCADE, related_name='movie_tickets')
    qt = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'Customer: {self.customer.username}\nMovie: {self.movie.movie}\nQt: {self.qt}'
