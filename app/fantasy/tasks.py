import random

from celery import shared_task


@shared_task
def hello():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return a ** b
