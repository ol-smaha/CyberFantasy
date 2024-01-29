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

