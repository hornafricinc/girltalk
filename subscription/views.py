import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received

from accounts.views import logoutView
from girltalk import settings
from subscription.models import ClientSubscription, SubscriberDetails


@csrf_exempt
@login_required(login_url='accounts:signin')
def payment_done(request):
    logoutView(request)
    return render(request, 'subscriber/payment_done.html')



@csrf_exempt
@login_required(login_url='accounts:signin')
def payment_canceled(request):
    logoutView(request)
    return render(request, 'subscriber/payment_cancelled.html')



@login_required(login_url='accounts:signin')
def subscribe(request):
    if request.method == 'POST':
        request.session['subscription_plan']=request.POST.get('frequency')
        return redirect('subscription:process_subscription')
    return render(request,'subscriber/subscription_plans.html')


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
        plan = ""
        plan_i = ""
        if (ipn_obj.mc_gross == 59.00):
            plan = "YEARLY"
            plan_i = "m"
        else:
            plan = "MONTHLY"
            plan_i = "y"
        datetime_object = datetime.strptime(ipn_obj.subscr_date, '%m/%d/%y %H:%M:%S')
        my_due_date = datetime_object + datetime.timedelta(days=0)
        if plan_i == "m":
            my_due_date = datetime_object + datetime.timedelta(days=30)
        else:
            my_due_date = datetime_object + datetime.timedelta(days=365)

        SubscriberDetails.objects.create(user=user,txn_id=ipn_obj.txn_id,s_plan=plan,amount=ipn_obj.mc_gross,subscription_date=ipn_obj.subscr_date,due_date=my_due_date)







valid_ipn_received.connect(payment_received)







