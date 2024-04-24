from enum import Enum


class CompetitionStatusEnum(str, Enum):
    NOT_STARTED = 'NOT STARTED'
    STARTED = 'STARTED'
    FINISHED = 'FINISHED'

    @classmethod
    def choices(cls):
        res = tuple([(e.value, e.value) for e in cls])
        return res


class GameRoleEnum(str, Enum):
    CARRY = 'CARRY'
    MID = 'MID'
    HARD = 'HARD'
    SUPPORT_4 = 'SUPPORT_4'
    SUPPORT_5 = 'SUPPORT_5'

    @classmethod
    def choices(cls):
        res = tuple([(e.value, e.value) for e in cls])
        return res


class MatchSeriesBOFormatEnum(str, Enum):
    BO1 = 'bo1'
    BO2 = 'bo2'
    BO3 = 'bo3'
    BO5 = 'bo5'

    @staticmethod
    def get_format(series_type):
        mapper = {
            0: MatchSeriesBOFormatEnum.BO1,
            1: MatchSeriesBOFormatEnum.BO3,
            2: MatchSeriesBOFormatEnum.BO5,
            3: MatchSeriesBOFormatEnum.BO2,
        }
        return mapper.get(series_type, MatchSeriesBOFormatEnum.BO1)

    @classmethod
    def choices(cls):
        res = tuple([(e.value, e.value) for e in cls])
        return res