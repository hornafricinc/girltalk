import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received

from accounts.views import logoutView
from girltalk import settings
from subscription.models import ClientSubscription, SubscriberDetails, SubscriberSubscriptionDetails
import stripe

stripe.api_key=settings.STRIPE_SECRET_KEY


@csrf_exempt
def payment_done(request):
    logoutView(request)
    return render(request, 'payment_done.html')



@csrf_exempt
def payment_canceled(request):
    logoutView(request)
    return render(request, 'payment_cancelled.html')



@login_required(login_url='accounts:signin')
def subscribe(request):
   # if request.method == 'POST':
        #request.session['subscription_plan']=request.POST.get('frequency')
       # return redirect('subscription:process_subscription')
    return render(request,'subscriber/subscription_plans.html')

#This is the view to pprocess customer subscription.
@login_required(login_url='accounts:signin')
def process_subscription(request):
    usermail=request.user.email
    if request.method == 'POST':
        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.first_name+' '+request.user.last_name,
            source=request.POST['stripeToken'],
        )
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[
                {'plan': 'price_1H7QitFuwTkoJXtMe5otaHpo'}
            ],
            collection_method='charge_automatically',
            trial_period_days=7,
        )


        #Here we save the customer id and subscription id in our database.
        stripesubscriptionsdetails=SubscriberSubscriptionDetails()
        user=User.objects.get(email=request.user.email)
        stripesubscriptionsdetails.user=user
        stripesubscriptionsdetails.customer_id=customer.id
        stripesubscriptionsdetails.subscription_id=subscription.id
        stripesubscriptionsdetails.save()




    return redirect(reverse('subscription:success', args=[usermail]))


def successMsg(request, args):
    usermail = args
    return render(request, 'subscriber/success.html', {'username': usermail})



def process_payment(request):
    subscription_plan=request.session.get('subscription_plan')
    client_email=request.session.get('usermail')
    host=request.get_host()
    if subscription_plan == '1':
        price = "7"
        billing_cycle = 1
        billing_cycle_unit = "M"
    elif subscription_plan == '12':
        price = "59"
        billing_cycle = 1
        billing_cycle_unit = "Y"
    paypal_dict = {
        "cmd": "_xclick-subscriptions",
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        "a3": price,  # monthly price
        "p3": billing_cycle,  # duration of each unit (depends on unit)
        "t3": billing_cycle_unit,  # duration unit ("M for Month")
        "src": "1",  # make payments recur
        "sra": "1",  # reattempt payment on payment error
        "no_note": "1",  # remove extra notes (optional)
        'item_name': 'Service Subscription',
        'custom': request.user,
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,reverse('subscription:subscription_done')),
        'cancel_return': 'http://{}{}'.format(host,reverse('subscription:subscription_cancelled')),
    }

    form=PayPalPaymentsForm(initial=paypal_dict,button_type='subscribe')
    return render(request,'subscriber/process_payment.html',locals())


def payment_received(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.txn_type == "subscr_payment":
        user = User.objects.get(username=ipn_obj.custom)
        ClientSubscription.objects.create(user=user, status=True)
        subscribe_o = SubscriberDetails()
        s_plan=""
        if ipn_obj.mc_gross == 7:
            s_plan="M"

        else:
            s_plan="Y"



        subscribe_o.txn_id = ipn_obj.txn_id
        subscribe_o.user = user
        subscribe_o.s_plan = s_plan
        subscribe_o.amount = ipn_obj.mc_gross
        subscribe_o.payer_email = ipn_obj.payer_email
        subscribe_o.subscription_date = ipn_obj.payment_date

        subscribe_o.save()


valid_ipn_received.connect(payment_received)







