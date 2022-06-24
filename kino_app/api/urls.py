from django.urls import path
from rest_framework import routers

from kino_app.api.resources import CustomerModelViewSet, CinemaHallModelViewSet, MovieSessionModelViewSet, \
    ApiLogoutView, ProfileView, TagView, LastFiveMoviesView, TagDetailView

router = routers.SimpleRouter()
router.register(r'registration', CustomerModelViewSet)
router.register(r'users', CustomerModelViewSet)
router.register(r'cinema', CinemaHallModelViewSet)
router.register(r'movie', MovieSessionModelViewSet)

urlpatterns = [
    path("tags/<slug:tag_slug>/", TagDetailView.as_view()),
    path("tags/", TagView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("last_five/", LastFiveMoviesView.as_view()),
    # path('api-token-auth/', CustomGetToken.as_view(), name='get_token'),
    path('logout/', ApiLogoutView.as_view(), name='api_logout'),
]

urlpatterns += router.urls
