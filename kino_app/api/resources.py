import json

import taggit
from django.core.mail import send_mail
from django.utils import timezone
# from rest_framework import serializers
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAcceptable
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
from kino_app.models import Customer, CinemaHall, MovieSession, Ticket
from kino_app.api.permissions import IsAnonymousUser, IsAuthNotAdmin


class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get(self, request, *args,  **kwargs):
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
            self.permission_classes = (AllowAny, )
        return super().get_permissions()

    def get_serializer_context(self):
        data_from_postman = self.request.data.pop('str_data', False)
        if data_from_postman:
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)
        return super().get_serializer_context()


# class CustomGetToken(ObtainAuthToken):
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         if created:
#             token.created += timedelta(minutes=10)
#             token.save()
#         return Response({
#             'token': token.key,
#             'user_id': user.id,
#             'time_to_live_seconds': (token.created - timezone.now()).seconds
#                          })


class ApiLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        token: Token = request.auth
        token.delete()
        return Response()


class CustomPagination(PageNumberPagination):
    page_size = 8
    page_query_param = 'page_size'
    max_page_size = 10


class CinemaHallModelViewSet(ModelViewSet):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer
    permission_classes = (IsAdminUser, )

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny, )
        return super(CinemaHallModelViewSet, self).get_permissions()

    def perform_update(self, serializer):
        inst = serializer.instance
        if Ticket.objects.filter(movie__hall=inst, movie__end_datetime__gte=timezone.now()):
            raise NotAcceptable("there are already purchased tickets in this hall, cannot be changed this hall!")

        serializer.save()


class MovieSessionModelViewSet(ModelViewSet):
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now()) 
    permission_classes = (IsAdminUser, )
    serializer_class = MovieSessionSerializer
    pagination_class = CustomPagination
    order_by = ['-start_datetime']

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny, )
        return super(MovieSessionModelViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):

        if data_from_postman := self.request.data.pop('str_data', False):
            json_data = json.loads(*data_from_postman)
            self.request.data.update(json_data)

        return super(MovieSessionModelViewSet, self).create(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        serializer.save(kwargs={'data': serializer.validated_data})

    # def perform_create(self, serializer):
    #
    #     try:
    #         dates, hall_id = creating(serializer.validated_data)
    #     except ValueError:
    #         raise serializers.ValidationError({'movie_sessions_error': 'There is movie no this time in this hall!'})
    #
    #     data = serializer.validated_data
    #     movie = data.get('movie', False)
    #     price = data.get('price', False)
    #     qyt = data.get('hall', False).hall_size
    #     slug = '_'.join(movie.split())
    #     description = data.get('description', False)
    #     tags = data.grt('tag', False)
    #
    #     movies = (MovieSession(hall_id=hall_id, movie=movie, qyt=qyt, price=price,
    #                            start_datetime=start, end_datetime=end, slug=slug,
    #                            description=description, tag=tags) for start, end in dates)
    #
    #     MovieSession.objects.bulk_create(movies)


class TicketModelViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAuthNotAdmin, )
        return super(TicketModelViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super(TicketModelViewSet, self).get_queryset()
        user = self.request.user
        if not user.is_admin:
            queryset = queryset.filter(customer=user)
        return queryset

    def perform_create(self, serializer):
        data = serializer.validated_data
        movie = MovieSession.objects.get(id=data['movie'].id)
        user = Customer.objects.get(id=self.request.user.id)
        qnt = data['qt']
        if (movie.free_seats - qnt) < 0:
            raise serializers.ValidationError({'qnt': 'Not enough free seats!'})
        movie.free_seats -= qnt
        user.spent += qnt * movie.price
        movie.save()
        user.save()
        data['customer'] = user
        serializer.validated_data = data
        serializer.save()


class TagDetailView(ListAPIView):
    queryset = MovieSession.objects.all()
    serializer_class = MovieSessionSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

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
    queryset = MovieSession.objects.all().order_by('-id')[:5]
    serializer_class = MovieSessionSerializer
    permission_classes = [AllowAny]
