from rest_framework.routers import DefaultRouter

from api.views import CompetitionViewSet, PlayerViewSet, FantasyTeamViewSet, FantasyPlayerViewSet

router = DefaultRouter()
router.register('competition', CompetitionViewSet, basename='competition'),
router.register('player', PlayerViewSet, basename='player'),
router.register('fantasy-team', FantasyTeamViewSet, basename='fantasy-team'),
router.register('fantasy-player', FantasyPlayerViewSet, basename='fantasy-player'),

urlpatterns = router.urls


