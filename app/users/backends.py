import random

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()

def generate_username():
    first_list = ['super', 'strong', 'smart', 'beautiful', 'elegant', 'muscular', 'skinny', 'clever',
                  'famous', 'powerful', 'aggressive', 'ambitious', 'happy', 'wonderful', 'witty']
    second_list = ['rabbit', 'mouse', 'snake', 'turtle', 'alpaca', 'chicken', 'mule', 'sheep',
                   'duck', 'goose', 'beaver', 'coyote', 'frog', 'salamander', 'crab']

    last_user = User.objects.last()
    last_id = last_user.pk if last_user else 1
    username = f'{random.choice(first_list)} {random.choice(second_list)} {last_id}'
    return username


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if username == 'admin':
                user = UserModel.objects.get(username=username)
            else:
                user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

