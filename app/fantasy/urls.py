from django.urls import path
from fantasy.views import FantasyTeamView, TournamentsView


urlpatterns = [
    path('tournaments/', TournamentsView.as_view(), name="tournaments"),
    path('tournament/<int:tournament_id>/fantasy-team', FantasyTeamView.as_view(), name="fantasy-team"),
]