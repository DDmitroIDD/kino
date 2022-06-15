from datetime import timedelta

from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotAcceptable
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from kino_app.api.serializers import CustomerSerializer, CinemaHallSerializer, MovieSessionSerializer, TicketSerializer
from kino_app.models import Customer, CinemaHall, MovieSession, Ticket
from kino_app.api.permissions import IsAnonymousUser, IsAuthNotAdmin


class CustomerModelViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = (IsAdminUser, )

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAnonymousUser, )
        return super(CustomerModelViewSet, self).get_permissions()


class CustomGetToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if created:
            token.created += timedelta(minutes=10)
            token.save()
        return Response({
            'token': token.key,
            'user_id': user.id,
            'time_to_live_seconds': (token.created - timezone.now()).seconds
                         })


class ApiLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        token: Token = request.auth
        token.delete()
        return Response()


class CustomPagination(PageNumberPagination):
    page_size = 5
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

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny, )
        return super(MovieSessionModelViewSet, self).get_permissions()


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
