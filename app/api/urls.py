from rest_framework.routers import DefaultRouter

from api.views import CompetitionViewSet, PlayerViewSet, FantasyTeamViewSet, FantasyPlayerViewSet, UserViewSet, \
    CompetitionTourViewSet, FantasyTeamTourViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='user'),
router.register('competition', CompetitionViewSet, basename='competition'),
router.register('competition-tour', CompetitionTourViewSet, basename='competition-tour'),
router.register('player', PlayerViewSet, basename='player'),
router.register('fantasy-team', FantasyTeamViewSet, basename='fantasy-team'),
router.register('fantasy-team-tour', FantasyTeamTourViewSet, basename='fantasy-team-tour'),
router.register('fantasy-player', FantasyPlayerViewSet, basename='fantasy-player'),

urlpatterns = router.urls


