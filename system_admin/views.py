import random

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from accounts.forms import UserAccountForm, LoginForm
from accounts.models import Profile
from subscription.models import SubscriberDetails
from system_admin.models import AccessCodes

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



def create_account(request):
    if request.method == 'POST':
        form=UserAccountForm(request.POST)
        if form.is_valid():
            fs=form.save(commit=False)
            fs.is_superuser=True
            fs.save()
            form=UserAccountForm()
            messages.success(request,'System Administrator Account Created Successfully.Proceed now to login')
        else:
            messages.error(request,'Data not entered correctly.Please enter a valid data')
    else:
        form=UserAccountForm()
    return  render(request,'sys_admin/create_account.html',{'form':form})

@login_required(login_url='system_admin:login')
def load_admin_dash(request):
    #get_total_users(request.user.username)
    return render(request,'sys_admin/dashboard.html')

def load_payments_details(request):
    return render(request,'accounts/admin/payment_details.html')

def process_admin_signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user is not None:
                if user.is_superuser == True:
                    login(request, user)
                    return redirect('system_admin:admin_dash')
                else:
                    messages.error(request,"Wrong Login Credentials")
            else:
                messages.error(request, 'Wrong username or Password')
    else:
        form = LoginForm()
    return render(request, 'sys_admin/login.html', {'form': form})


#This is the function to manage access codes;
def manage_codes(request):
    all_codes=AccessCodes.objects.all().order_by('-time_gen')
    active_code=AccessCodes.objects.filter(status=True)
    ac_object = AccessCodes()
    if request.method == 'POST':
        if request.POST.get('generate',False):
            #Check if the code exists.
            code_exists=AccessCodes.objects.filter(access_code=generate_access_code()).count()
            if code_exists >0:
                messages.error(request,"Please the generated code already exists.Please generate a new one")

            else:
                ac_object.access_code=generate_access_code()
                ac_object.status=False
                ac_object.save()
                all_codes=AccessCodes.objects.all().order_by('-time_gen')
                messages.success(request,'Access code was successfully generated.Please activate it if you want to use it.')
        elif request.POST.get('activate',False):
            activate_access_code(request,request.POST['codeID'])
        elif request.POST.get('del', False):
            delete_access_code(request,request.POST['codeID'])

    return render(request,'sys_admin/manage_codes.html',{'codes':all_codes,'active_code':active_code})
def generate_access_code():
    number=random.randint(2549,2999)
    return number;

def activate_access_code(request,code_id):
    AccessCodes.objects.all().update(status=False)
    AccessCodes.objects.filter(pk=code_id).update(status=True)
    messages.success(request,"Access code updadted successfully")



def delete_access_code(request,code_id):
    AccessCodes.objects.filter(pk=code_id).delete()
    messages.success(request,"The selected code has been deleted successfully")


''''
****************************USERS MANAGEMENT METHODS*******************
'''
def get_all_users(request):
    try:
        users=User.objects.all().exclude(is_superuser=True)
    except User.DoesNotExist:
        users=None

    return render(request,'sys_admin/manage_users.html',{'users':users})

''''
****************************FINANCE MANAGEMENT*******************
'''

def get_all_transactions(request):
    try:
        all_data=SubscriberDetails.objects.select_related('user').all()
    except SubscriberDetails.DoesNotExist:
        all_data=None
    return render(request,'sys_admin/manage_finances.html',{'all_data':all_data})

#This is the update on Admin profile
def update_admin_profile(request):
    if request.method == 'POST':
        try:
            Profile.objects.get(user=request.user)
            Profile.objects.filter(user=request.user).update(profile_image_name=request.POST['image_name'])
            return redirect('system_admin:admin_dash')
        except Profile.DoesNotExist:
            profile_image=request.POST['image_name']
            user=User.objects.get(pk=request.user.id)
            Profile.objects.create(user=user,profile_image_name=profile_image)
            return redirect('system_admin:admin_dash')
    return  render(request,'sys_admin/update_profile.html')
    

