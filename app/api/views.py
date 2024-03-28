from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from api.serializers import CompetitionSerializer, PlayerSerializer, FantasyTeamSerializer, FantasyPlayerSerializer, \
    FantasyTeamCreateSerializer, FantasyPlayerCreateSerializer, FantasyTeamRatingSerializer, UserSerializer, \
    CompetitionEditStatusSerializer, CompetitionTourSerializer, FantasyTeamTourSerializer, \
    FantasyTeamTourCreateSerializer

from fantasy.models import Competition, Player, FantasyTeam, FantasyPlayer, CompetitionTour, FantasyTeamTour
from djoser import utils
from djoser.conf import settings
from rest_framework import status

from users.models import CustomUser


class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        data = token_serializer_class(token).data
        data.update({'username': serializer.user.username})

        return Response(
            data=data, status=status.HTTP_200_OK
        )


class CompetitionViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def rating(self, request, pk=None):
        try:
            competition = self.get_object()
        except Competition.DoesNotExist:
            return Response({"error": "Competition not found"}, status=404)

        fantasy_teams = competition.fantasy_teams.all().order_by('-result')
        serializer = FantasyTeamRatingSerializer(fantasy_teams, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def edit_status(self, request, pk=None):
        instance = self.get_object()
        serializer = CompetitionEditStatusSerializer(instance)
        return Response({
            'competition_details': serializer.data
        })


class CompetitionTourViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             GenericViewSet):
    queryset = CompetitionTour.objects.all()
    serializer_class = CompetitionTourSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'competition': ['in', 'exact']
    }
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def rating(self, request, pk=None):
        try:
            tour = self.get_object()
        except Competition.DoesNotExist:
            return Response({"error": "Competition not found"}, status=404)

        fantasy_teams = tour.competition.fantasy_teams.all().order_by('-result')
        serializer = FantasyTeamRatingSerializer(fantasy_teams, many=True)
        return Response(serializer.data)


class PlayerViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'game_role': ['in', 'exact']
    }
    permission_classes = [IsAuthenticated]


class FantasyTeamViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):

    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'competition': ['in', 'exact']
    }
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(user=self.request.user)
        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FantasyTeamCreateSerializer
        else:
            return self.serializer_class


class FantasyTeamTourViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             GenericViewSet):

    queryset = FantasyTeamTour.objects.all()
    serializer_class = FantasyTeamTourSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'fantasy_team': ['in', 'exact'],
        'competition_tour': ['in', 'exact'],
    }
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FantasyTeamTourCreateSerializer
        else:
            return self.serializer_class


class FantasyPlayerViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           GenericViewSet):
    queryset = FantasyPlayer.objects.all()
    serializer_class = FantasyPlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FantasyPlayerCreateSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        try:
            tour = serializer.validated_data.get('fantasy_team_tour')
            if tour.competition_tour.is_editing_allowed:
                serializer.save()
        except KeyError:
            pass

    def perform_update(self, serializer):
        try:
            tour = serializer.validated_data.get('fantasy_team_tour')
            if tour.competition_tour.is_editing_allowed:
                serializer.save()
        except KeyError:
            pass


class UserViewSet(mixins.ListModelMixin,
                  GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        current_user = request.user
        serializer = self.get_serializer(current_user)
        return Response(serializer.data)


