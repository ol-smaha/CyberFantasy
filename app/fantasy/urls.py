from django.urls import path
from fantasy.views import FantasyTeamView


urlpatterns = [
    path('tournament/<int:tournament_id>/fantasy-team', FantasyTeamView.as_view(), name="fantasy-team"),
]