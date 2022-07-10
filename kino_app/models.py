from django.contrib.auth.models import AbstractUser
from django.db import models
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
from django.utils import timezone


class Customer(AbstractUser):
    money_spent = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(default='static/avatar.png', upload_to='avatar/')

    def __str__(self):
        return f'Username: {self.username}\nMoney spent: {self.money_spent}'


class CinemaHall(models.Model):
    hall_name = models.CharField(max_length=100, unique=True)
    hall_size = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'Hall: {self.hall_name}\nSize: {self.hall_size}\nid: {self.id}'


class MovieSession(models.Model):
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='movie_sessions')
    movie = models.CharField(max_length=20)
    qyt = models.PositiveSmallIntegerField()
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(default=timezone.now)
    price = models.PositiveSmallIntegerField()
    image = models.ImageField(blank=True, null=True, upload_to='posters/')
    slug = models.SlugField(blank=True, null=True)
    tag = TaggableManager()
    description = RichTextUploadingField(blank=True, null=True)

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self):
        return f'Hall: {self.hall.hall_name}\n' \
               f'Movie: {self.movie}\nPrice: {self.price} image: {self.image} id: {self.id}'

    def save(self, **kwargs):

        if not self.id:
            self.qyt = self.hall.hall_size
            self.slug = self.movie.replace(' ', '_')
            return super(MovieSession, self).save(**kwargs)

        #     try:
        #         hall = MovieSession.objects.filter(hall_id=self.hall.id)
        #         dates = create_dates(self, hall)
        #     except ValidationError:
        #         raise ValidationError({'movie_sessions_error': 'There is movie no this time in this hall!'})
        #     for start, end in dates:
        #         movie = MovieSession(hall_id=self.hall.id, movie=self.movie, qyt=self.qyt, price=self.price,
        #                              start_datetime=start, end_datetime=end, slug=self.slug,
        #                              description=self.description, image=self.image)
        #         tags = (movie.tag.add(t) for t in self.tag)
        #         movie.save()
        #     # movies = (MovieSession(hall_id=self.hall.id, movie=self.movie, qyt=self.qyt, price=self.price,
        #     #                        start_datetime=start, end_datetime=end, slug=self.slug,
        #     #                        description=self.description, image=self.image)
        #     #           for start, end in dates)
        #     # new_movies = MovieSession.objects.bulk_create(movies)
        #     # unpack = [new_movies]
        #     #
        #     # return new_movies
        # elif self.id:
        #     if tickets := Ticket.objects.filter(movie_id=self.id):
        #         raise ValidationError({'movie_sessions_error': 'There is tickets no this session. '
        #                                                        'You can`t changing this movie!'})
        #     sessions = MovieSession.objects.filter(movie=self.movie)
        #     mov_for_upd = []
        #     for session in sessions:
        #         if tickets := Ticket.objects.filter(movie_id=session.id):
        #             continue
        #         session.movie = self.movie
        #         session.qyt = self.qyt
        #         session.image = self.image
        #         session.description = self.description
        #         session.slug = self.slug
        #         session.price = self.price
        #         session.tag.add(self.tag)
        #         mov_for_upd.append(session)
        #     return MovieSession.objects.bulk_update(mov_for_upd, ["movie", "qyt", "image", "description",
        #                                                           "slug", "price"])
        #
        # return super(MovieSession, self).save(**kwargs)


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
