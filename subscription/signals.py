from django.contrib.auth.models import User
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received

from subscription.models import ClientSubscription


@receiver(valid_ipn_received)
def ipn_receiver(sender,**kwargs):
       ipn=sender

       if ipn.payment_status == 'completed':
              user=User.objects.get(username=ipn.custom)
              ClientSubscription.objects.create(user=user,status=True)







