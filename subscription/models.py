from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class ClientSubscription(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
class SubscriberDetails(models.Model):
    txn_id=models.CharField(max_length=20,blank=False,primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    s_plan=models.CharField(max_length=4,blank=False)
    amount=models.DecimalField(decimal_places=4,max_digits=10,blank=False)
    payer_email=models.CharField(max_length=50,blank=False)
    subscription_date=models.DateTimeField()

    class Meta:
        db_table='subscriptions'
class SubscriberSubscriptionDetails(models.Model):

    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='subscriber')
    customer=models.ForeignKey('djstripe.Customer',blank=True,null=True,on_delete=models.SET_NULL)
    subscription=models.ForeignKey('djstripe.Subscription',blank=True,null=True,on_delete=models.SET_NULL)
    date_subscribed=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='stripe_subscriptions'



