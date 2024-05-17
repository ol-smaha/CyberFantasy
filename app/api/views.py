from django.db.models import Sum, Window, F
from django.db.models.functions import Rank
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.filters import PlayersFilterSet
from api.serializers import CompetitionSerializerShort, PlayerSerializer, FantasyTeamSerializer, \
    FantasyPlayerSerializer, \
    FantasyTeamCreateSerializer, FantasyPlayerCreateSerializer, FantasyTeamTourRatingSerializer, UserSerializer, \
    CompetitionEditStatusSerializer, CompetitionTourSerializer, FantasyTeamTourSerializer, \
    FantasyTeamTourCreateSerializer, AppErrorReportSerializer, FantasyTeamRatingSerializer, \
    CompetitionSerializerWithTours, AppScreenInfoSerializer

from fantasy.models import Competition, Player, FantasyTeam, FantasyPlayer, CompetitionTour, FantasyTeamTour, \
    AppScreenInfo
from djoser import utils
from djoser.conf import settings
from rest_framework import status

from users.models import CustomUser, AppErrorReport


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
    serializer_class = CompetitionSerializerWithTours
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list']:
            return CompetitionSerializerShort
        else:
            return self.serializer_class

    @action(detail=True, methods=['GET'])
    def rating(self, request, pk=None):
        try:
            competition = self.get_object()
        except Competition.DoesNotExist:
            return Response({"error": "Competition not found"}, status=404)

        fantasy_teams = (competition.fantasy_teams.all()
                         .annotate(rank=Window(expression=Rank(), order_by=F('result').desc())))[:100]
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

        fantasy_teams = (tour.fantasy_teams.all()
                         .annotate(rank=Window(expression=Rank(), order_by=F('result').desc())))[:100]
        serializer = FantasyTeamTourRatingSerializer(fantasy_teams, many=True)
        return Response(serializer.data)


class PlayerViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlayersFilterSet
    # ordering = ('-cost', 'team__name', 'nickname')
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
            ft_tour = serializer.validated_data.get('fantasy_team_tour')
            player = serializer.validated_data.get('player')
            team_cost = (ft_tour.fantasy_players.all()
                         .aggregate(team_cost=Sum('player__cost'))['team_cost']) or 0.00
            current_player_cost = (ft_tour.fantasy_players
                                   .filter(player__game_role=player.game_role)
                                   .aggregate(total_cost=Sum('player__cost')))['total_cost'] or 0.00
            allowable_balance = 50.0 - float(team_cost) + float(current_player_cost)
            if ft_tour.competition_tour.is_editing_allowed and float(player.cost) <= allowable_balance:
                serializer.save()
        except KeyError:
            pass

    def perform_update(self, serializer):
        try:
            ft_tour = serializer.validated_data.get('fantasy_team_tour')
            player = serializer.validated_data.get('player')
            team_cost = (ft_tour.fantasy_players.all()
                         .aggregate(team_cost=Sum('player__cost'))['team_cost']) or 0.00
            current_player_cost = (ft_tour.fantasy_players
                                   .filter(player__game_role=player.game_role)
                                   .aggregate(total_cost=Sum('player__cost')))['total_cost'] or 0.00
            allowable_balance = 50.0 - float(team_cost) + float(current_player_cost)
            if ft_tour.competition_tour.is_editing_allowed and float(player.cost) <= allowable_balance:
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


class AppReportViewSet(mixins.CreateModelMixin,
                       GenericViewSet):
    queryset = AppErrorReport.objects.all()
    serializer_class = AppErrorReportSerializer
    permission_classes = [AllowAny]


class AppInfoViewSet(mixins.ListModelMixin,
                     GenericViewSet):
    queryset = AppScreenInfo.objects.all()
    serializer_class = AppScreenInfoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'screen': ['exact'],
    }
    permission_classes = [AllowAny]
