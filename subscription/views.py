from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

from accounts.views import logoutView
from girltalk import settings


@csrf_exempt
def payment_done(request):
    logoutView(request)
    return render(request, 'accounts/payment_done.html')



@csrf_exempt
def payment_canceled(request):
    logoutView(request)
    return render(request, 'accounts/payment_cancelled.html')



@login_required(login_url='accounts:signin')
def subscribe(request):
    if request.method == 'POST':
        request.session['subscription_plan']=request.POST.get('frequency')
        return redirect('subscription:process_subscription')
    return render(request,'accounts/sunscription.html')


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
        'item_name': 'Content subscription',
        'custom': request.user,
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,reverse('subscription:subscription_done')),
        'cancel_return': 'http://{}{}'.format(host,reverse('subscription:subscription_cancelled')),
    }

    form=PayPalPaymentsForm(initial=paypal_dict,button_type='subscribe')
    return render(request,'accounts/process_subscription.html',locals())