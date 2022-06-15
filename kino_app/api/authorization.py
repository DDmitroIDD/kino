from datetime import timedelta

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


class CustomTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        time_to_live = timedelta(minutes=10)
        if timezone.now() > token.created:
            token.delete()
            raise exceptions.AuthenticationFailed('Invalid Token')
        token.created = timezone.now() + time_to_live
        token.save()
        return user, token