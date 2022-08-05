import json
from datetime import datetime

import taggit
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
# from rest_framework import serializers
from rest_framework import serializers, status, filters
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAcceptable, ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from taggit.models import Tag

from kino_app.api.serializers import CustomerSerializer, CinemaHallSerializer, MovieSessionSerializer, TicketSerializer, \
    ContactSerailizer, TagSerializer
# from kino_app.creating_movie_sessions import creating
from kino_app.creating_movie_sessions import create_dates
from kino_app.models import Customer, CinemaHall, MovieSession, Ticket
from kino_app.api.permissions import IsAnonymousUser, IsAuthNotAdmin


class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            "user": CustomerSerializer(request.user, context=self.get_serializer_context()).data,
        })


class CustomerModelViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    http_method_names = ['post', ]
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_context(self):
        data_from_postman = self.request.data.pop('str_data', False)
        if data_from_postman:
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)
        return super().get_serializer_context()


class CustomPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 10


class CinemaHallModelViewSet(ModelViewSet):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    permission_classes = (IsAdminUser,)

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        return super(CinemaHallModelViewSet, self).get_permissions()

    def perform_update(self, serializer):
        inst = serializer.instance
        if Ticket.objects.filter(movie__hall=inst, movie__end_datetime__gte=timezone.now()):
            raise NotAcceptable("there are already purchased tickets in this hall, cannot be changed this hall!")

        serializer.save()


class AllSeancesOfThisMovie(ListAPIView):
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now())
    permission_classes = (AllowAny,)
    serializer_class = MovieSessionSerializer
    pagination_class = CustomPagination
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super(AllSeancesOfThisMovie, self).get_queryset()
        slug = self.kwargs.get('slug', False)
        queryset = queryset.filter(slug=slug)
        qyt = queryset[0].hall.hall_size
        return queryset.filter(qyt=qyt)


class MovieSessionModelViewSet(ModelViewSet):
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now())
    permission_classes = (IsAdminUser,)
    serializer_class = MovieSessionSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    order_by = ['-start_datetime']
    lookup_field = 'id'
    search_fields = ["movie"]

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        return super(MovieSessionModelViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):

        if data_from_postman := self.request.data.pop('str_data', False):
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)
        return super(MovieSessionModelViewSet, self).create(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        if kwargs.get('partial', False):
            movie = args[0]
            hall = movie.hall
            if movie.qyt != hall.hall_size:
                raise serializers.ValidationError("You can\'t change this movie "
                                                  "because there are tickets at this movie")
            movies_in_this_hall = MovieSession.objects.filter(hall=hall).exclude(id=movie.id)
            start = kwargs['data'].get('start_datetime', False)
            end = kwargs['data'].get('end_datetime', False)
            start_date = datetime.strptime(start, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end, '%Y-%m-%dT%H:%M')
            if start_date > end_date:
                raise serializers.ValidationError('Your start time starting after end time!')
            if start_date.date() != end_date.date():
                raise serializers.ValidationError('Dates can`t be difference!')
            if movies_in_this_hall.filter(Q(
                    start_datetime__range=(start_date, end_date)) | Q(end_datetime__range=(start_date, end_date)) |
                                          Q(start_datetime__lte=start_date, end_datetime__gte=end_date)):
                raise serializers.ValidationError("There is movie no this time in this hall!")
        return super(MovieSessionModelViewSet, self).get_serializer(*args, **kwargs)


class TicketModelViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAuthNotAdmin,)
        return super(TicketModelViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super(TicketModelViewSet, self).get_queryset()
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(customer=user)
        return queryset

    def perform_create(self, serializer):
        data = serializer.validated_data
        movie = data.get('movie')
        user = data.get('customer')
        qt = data.get('qt')
        if (movie.qyt - qt) < 0:
            raise serializers.ValidationError({'qnt': 'Not enough free seats!'})
        movie.qyt -= qt
        user.money_spent += qt * movie.price
        movie.save()
        user.save()
        serializer.save()


class TagDetailView(ListAPIView):
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now())
    serializer_class = MovieSessionSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        try:
            tag_slug = self.kwargs['tag_slug'].lower()
            tag = Tag.objects.get(slug=tag_slug)
            return super().get_queryset().filter(tag=tag)
        except taggit.models.Tag.DoesNotExist:
            return super(TagDetailView, self).get_queryset()


class TagView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    # pagination_class = CustomPagination


class FeedBackView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ContactSerailizer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerailizer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'От {name} | {subject}', message, from_email, ['dimakozhurin28@gmail.com'])
            return Response({"success": "Sent"})
        return Response("Form is not valid!")


class LastFiveMoviesView(ListAPIView):
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now()).order_by('slug').distinct('slug')[:5]
    serializer_class = MovieSessionSerializer
    permission_classes = [AllowAny]
