from enum import Enum


class CompetitionStatusEnum(str, Enum):
    NOT_STARTED = 'Ще не стартував'
    STARTED = 'Активний'
    FINISHED = 'Завершено'

    @classmethod
    def choices(cls):
        res = tuple([(e.value, e.value) for e in cls])
        return res


class GameRoleEnum(str, Enum):
    CARRY = 'CARRY'
    MIDDER = 'MIDDER'
    SUPPORT = 'SUPPORT'

    @classmethod
    def choices(cls):
        res = tuple([(e.value, e.value) for e in cls])
        return res

