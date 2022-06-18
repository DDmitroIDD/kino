from django.contrib.auth.models import AbstractUser
from django.db import models
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
from django.utils import timezone


class Customer(AbstractUser):
    money_spent = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(default='/static/421-4212341_default-avatar-svg-hd-png-download.png')

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
    image = models.ImageField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    tag = TaggableManager()
    description = RichTextUploadingField(blank=True, null=True)

    def __str__(self):
        return f'Hall: {self.hall.hall_name}\nMovie: {self.movie}\nPrice: {self.price} image: {self.image}'

    def save(self, **kwargs):
        if not self.id:
            self.free_seats = self.hall.hall_size
        if not self.slug:
            self.slug = '_'.join(self.movie.split())
        return super().save(**kwargs)


class Ticket(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_tickets')
    movie = models.ForeignKey(MovieSession, on_delete=models.CASCADE, related_name='movie_tickets')
    qt = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'Customer: {self.customer.username}\nMovie: {self.movie.movie}\nQt: {self.qt}'


class Contacts(models.Model):
    name_cont = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    topic = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    time_to_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cont name: {self.name_cont} | Topic: {self.topic}'
