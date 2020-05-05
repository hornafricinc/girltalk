from django.contrib.auth import user_logged_out, user_logged_in
from django.dispatch import receiver

from accounts.models import LoggedInUser


@receiver(user_logged_in)
def on_user_logged_in(sender,request,**kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get('user'))

@receiver(user_logged_out)
def on_user_logged_in(sender,request,**kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()