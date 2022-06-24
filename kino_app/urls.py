from django.urls import path

from kino_app.views import MovieListView, SignUpView, LogInView, LogOutView, CinemaCreateView, CinemaUpdateView, \
    MovieCreateView, MovieUpdateView, TicketCreateView, TicketsListView

urlpatterns = (
    path('', MovieListView.as_view(), name='movie_list'),
    path('register/', SignUpView.as_view(), name='register'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('cinema_create/', CinemaCreateView.as_view(), name='cinema_create'),
    path('cinema_update/<int:pk>/', CinemaUpdateView.as_view(), name='cinema_update'),
    path('movie_create/', MovieCreateView.as_view(), name='movie_create'),
    path('movie_update/<int:pk>/', MovieUpdateView.as_view(), name='movie_update'),
    path('ticket_create/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets_list/', TicketsListView.as_view(), name='tickets_list'),



)
