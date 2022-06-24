from django.contrib import admin

from kino_app.models import Customer, CinemaHall, MovieSession, Ticket, Contacts

admin.site.register(Customer)
admin.site.register(CinemaHall)
admin.site.register(MovieSession)
admin.site.register(Ticket)
admin.site.register(Contacts)
