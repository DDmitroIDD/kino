from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, DateTimeInput, SplitDateTimeWidget, SplitDateTimeField

from kino_app.models import Customer, CinemaHall, MovieSession, Ticket


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = Customer
        fields = ('username', )


class CinemaModelForm(ModelForm):

    class Meta:
        model = CinemaHall
        fields = ('hall_name', 'hall_size')


class MovieSessionModelForm(ModelForm):

    class Meta:
        model = MovieSession
        fields = ('hall', 'movie', 'start_datetime', 'end_datetime', 'price')

        # widgets = {
        #     'end_datetime': SplitDateTimeWidget(time_attrs={'type': 'time'}, date_attrs={'type': 'date'}),
        #     'start_datetime': SplitDateTimeWidget(time_attrs={'type': 'time'}, date_attrs={'type': 'date'}),
        #
        # }

    # def is_valid(self):
    #     data = self.data
    #     self.data['start_datetime'] = data.get('start_datetime_0') + 'T' + data.get('start_datetime_1')
    #     self.data['end_datetime'] = data.get('end_datetime_0') + 'T' + data.get('end_datetime_1')
    #     return super(MovieSessionModelForm, self).is_valid()
    # def clean(self):
    #     a = 1
    #     return


class TicketModelForm(ModelForm):

    class Meta:
        model = Ticket
        fields = ('qt', )


