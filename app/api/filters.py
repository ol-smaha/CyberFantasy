import json

from django_filters.rest_framework import FilterSet, NumberFilter, DjangoFilterBackend

from fantasy.models import Competition, Player


class PlayersFilterSet(FilterSet):
    competition_id = NumberFilter(method='filter_competition_id')

    class Meta:
        model = Player
        fields = ['game_role', 'competition_id']

    def filter_competition_id(self, queryset, field_name, value):
        if value != "":
            teams = Competition.objects.filter(id=int(value)).values_list('team', flat=True)
            queryset = queryset.filter(team__in=teams)
        return queryset
