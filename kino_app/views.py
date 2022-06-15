from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from kino_app.forms import UserRegisterForm, TicketModelForm, CinemaModelForm, MovieSessionModelForm
from kino_app.models import MovieSession, CinemaHall, Ticket


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'register.html'
    success_url = '/'
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'], )
        login(self.request, user)
        return redirect('/')


class LogInView(LoginView):
    template_name = 'login.html'
    next_page = '/'


class LogOutView(LogoutView):
    next_page = 'login'


class MovieListView(ListView):
    model = MovieSession
    template_name = 'index.html'
    queryset = MovieSession.objects.filter(end_datetime__gte=timezone.now())
    extra_context = {'ticket_form': TicketModelForm}
    ordering = ('start_datetime', )
    context_object_name = 'movies'
    paginate_by = 10

    def get_queryset(self):
        date = self.request.GET.get('date_search')
        if date:
            query = MovieSession.objects.filter(start_datetime__range=(date+'T00:00', date+'T23:59'))
            return query
        return super(MovieListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'is_anonymous': self.request.user.is_anonymous,
            'is_superuser': self.request.user.is_superuser,
            'is_authenticated': self.request.user.is_authenticated
             })
        return super(MovieListView, self).get_context_data(**kwargs)

    def get_ordering(self):
        order = self.request.GET.get('order')
        if order:
            self.ordering = (order, )
        return self.ordering


class CinemaCreateView(PermissionRequiredMixin, CreateView):
    model = CinemaHall
    template_name = 'cinema_create.html'
    success_url = '/cinema_create'
    permission_required = 'is_superuser'
    form_class = CinemaModelForm

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     DateTimeRange


class CinemaUpdateView(PermissionRequiredMixin, UpdateView):
    model = CinemaHall
    template_name = 'cinema_create.html'
    success_url = '/'
    permission_required = 'is_superuser'
    form_class = CinemaModelForm

    def get(self, request, *args, **kwargs):
        hall_pk = kwargs.get('pk')
        tickets = Ticket.objects.filter(movie__hall_id=hall_pk)
        if tickets:
            messages.error(request, 'This hall already has active tickets!')
            return redirect('/')
        return super(CinemaUpdateView, self).get(request, *args, **kwargs)


class MovieCreateView(PermissionRequiredMixin, CreateView):
    model = MovieSession
    template_name = 'movie_create.html'
    success_url = '/movie_create'
    permission_required = 'is_superuser'
    form_class = MovieSessionModelForm

    def post(self, request, *args, **kwargs):
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        if start_datetime > end_datetime:
            messages.error(request, 'Your start time starting after end time!')
            return redirect('/movie_create')
        return super(MovieCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.qyt = object.hall.hall_size
        start_date = form.cleaned_data.get('start_datetime')
        end_date = form.cleaned_data.get('end_datetime')
        time_range = datetime.combine(start_date.date(), end_date.time()) - \
                     datetime.combine(start_date.date(), start_date.time())

        day_range = end_date.date() - start_date.date()

        dates = [(start_date + timedelta(days=day), start_date + timedelta(days=day, seconds=time_range.seconds))
                 for day in range(day_range.days+1)]

        for start, end in dates:
            mov = MovieSession.objects.filter(hall_id=object.hall_id).filter(Q(
                    start_datetime__range=(start, end)) | Q(end_datetime__range=(start, end)))
            if mov:
                messages.info(self.request, 'This time is taken!')
                return redirect('/movie_create')

        movies = (MovieSession(hall_id=object.hall_id, movie=object.movie, qyt=object.qyt, price=object.price,
                               start_datetime=start, end_datetime=end) for start, end in dates)

        MovieSession.objects.bulk_create(movies)
        return redirect('/movie_create')


class MovieUpdateView(UpdateView):
    model = MovieSession
    template_name = 'movie_create.html'
    success_url = '/'
    permission_required = 'is_superuser'
    form_class = MovieSessionModelForm

    def get(self, request, *args, **kwargs):
        movie_pk = kwargs.get('pk')
        tickets = Ticket.objects.filter(movie_id=movie_pk)
        if tickets:
            messages.error(request, 'This movie already has active tickets!')
            return redirect('/')
        return super().get(request, *args, **kwargs)


class TicketCreateView(CreateView):
    model = Ticket
    http_method_names = ('post', )
    form_class = TicketModelForm
    success_url = '/'
    template_name = 'index.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        customer = self.request.user
        movie_id = form.data.get('movie')
        qt = int(form.data.get('qt'))
        movie = MovieSession.objects.get(id=movie_id)
        movie.qyt -= qt
        if movie.qyt < 0:
            messages.error(self.request, 'You want more seats than session has!')
            return redirect('/')
        self.object.customer = customer
        self.object.movie = movie
        money_spent = movie.price * qt
        customer.money_spent += money_spent
        self.object.save()
        movie.save()
        customer.save()
        messages.success(self.request, f'You buy {qt} ticket/s!'
                                       f' Spend {money_spent} grn! Enjoy your movie')
        return super(TicketCreateView, self).form_valid(form)


class TicketsListView(ListView):
    model = Ticket
    queryset = Ticket.objects.all()
    template_name = 'tickets_list.html'
    ordering = ('movie__start_time', )

    def get_queryset(self):
        query = Ticket.objects.filter(customer=self.request.user)
        return query

