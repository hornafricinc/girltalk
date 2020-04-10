from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
'''
All the functionalities of the system administrator will take place here.All the Major functions that include:
1.Checking number of users
2.Checking received payments and refunding payments
3.Checking total numbers of registered users;
4.Checking total number of susbscribed users;
5.Performing refunding of funds to users who want a refund of their fund.
'''
def get_total_users(request):
    total_users=User.objects.all().exclude(username=request.user.username)
    return render(request,'accounts/admin/user_details.html',{'total_users'})


@login_required(login_url='accounts:signin')
def load_admin_dash(request):
    #get_total_users(request.user.username)
    return render(request,'accounts/admin/index.html')

def load_payments_details(request):
    return render(request,'accounts/admin/payment_details.html')
