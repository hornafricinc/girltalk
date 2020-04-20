from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import TemplateView, FormView
from paypal.standard.forms import PayPalPaymentsForm


from accounts.forms import LoginForm, UserAccountForm, PasswordResetRequestForm
from accounts.models import Search, Messages, Profile
from django.core.mail import send_mail

from girltalk import settings
from subscription.models import ClientSubscription

#This is the homepage;
from system_admin.models import AccessCodes


def load_homepage(request):
    if request.method== 'POST':
        fname=request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['pass']
        cpass = request.POST['cpass'];
        if password != cpass:
            messages.error(request,"Your passwords do not match.Please enter matching passwords")
        else:
            #Check if email exists
            email_exists=User.objects.filter(email=email)
            if email_exists.count():
                messages.error(request,"Email address has been taken.Try with a new email address")
            else:
                username_exists=User.objects.filter(username=username)
                if username_exists.count():
                    messages.error(request,"Username has been taken.Try again with a different username")
                else:
                    #We save the details now.
                    User.objects.create_user(username,first_name=fname,last_name=lname,email=email,password=make_password(password))
                    messages.success(request,"Account Created Successfully.Proceed to subscription")
    return render(request,'home.html',locals())


class LoadIndex(TemplateView):
    template_name = 'home.html'





#This is the function to perform search on the database and present users who have searched before.
def processandPresentSearch(request):
    searchTermObject=Search()
    searchTerm=''
    if request.method == 'POST':
        searchTerm=request.POST['searchTerm']
        searchTermObject.search_term=searchTerm
        user=User.objects.get(pk=1)
        searchTermObject.user_id=user.pk
        searchTermObject.save()
        messages.success(request,'Search term successfully inserted')
    return render(request,'algorithm.html',{'name':searchTerm})
#Receiver Details
def receiverDetail(request,user_id):
    receiver=None
    receiver_id=int(user_id)
    userdetail=User.objects.filter(pk=receiver_id)
    chats = Messages.objects.filter(sender=request.user.id).filter(receiver=user_id).order_by('created_at') | Messages.objects.filter(sender=user_id).filter(receiver=request.user.id).order_by('created_at')
    if len(userdetail)>0:
        receiver=userdetail[0]
        ''''
        Here is where the chat will really take place.
        '''
        processChat(request,user_id)
        #Get the latest results
        chats = Messages.objects.filter(sender=request.user.id).filter(receiver=user_id).order_by('created_at')|  Messages.objects.filter(sender=user_id).filter(receiver=request.user.id).order_by('created_at')
    else:
        receiver=None
    return  render(request,'subscriber/instant_messaging.html',{'receiver':receiver,'chats':chats})


#This is the start of the web application
def processSiteEntryCredentials(request):
    access_code=''
    if request.method == 'POST':
        user_access_code=request.POST['access_code']
        try:
            db_acces_code=AccessCodes.objects.get(status=True)
            if user_access_code != db_acces_code.access_code:
                messages.error(request,"Invalid access Code.Please try again by entering a valid access code.")
            else:
                return redirect('accounts:index')
        except AccessCodes.DoesNotExist:
            messages.error(request, "Invalid access Code.Please try again by entering a valid access code.")
    return render(request,'entry.html')


#Perform Customer Sign Up
def create_account(request):
    if request.method == 'POST':
        form=UserAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account created Successfully.Proceed now to Login')
        else:
            messages.error(request,'Error Exists in your form Fields')
    else:
        form=UserAccountForm()
    return  render(request,'signup.html',{'form':form})

#Perform Security Checks Here
def process_user_signin(request):
    if request.method == 'POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            user=authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            if user is not None:
                if user.is_superuser == False:
                    login(request, user)
                    return redirect('accounts:dashboard')
                else:
                    messages.error(request,'Wrong login Credentials')
            else:
                messages.error(request,'Wrong username or Password')


    else:
        form=LoginForm()
    return  render(request,'login.html',{'form':form})


#Function to Present the Webpage;
@login_required(login_url='accounts:signin')
def  loadUserDashBoard(request):
    ''''
    My Friends are people who i have ever chatted with.
    '''
    l_user = User.objects.get(username=request.user.username)
    myFriends = Messages.objects.filter(sender=l_user).count()
    searchTermObject = Search()
    searchTerm = ''
    searchResults=''
    if request.method == 'POST':
        searchTerm = request.POST['searchTerm']
        category = request.POST['cat']
        if(category == 'null'):
            messages.error(request,'You have not selected any category')
        else:
            if (searchTerm == ''):
                messages.error(request,'You have not entered a term to search')
            else:
                u1 = User.objects.get(username=request.user.username)
                # Check if user has subscribed
                subexists = ClientSubscription.objects.filter(user=u1).count()
                if subexists > 0:
                    searchTermObject.search_term = searchTerm
                    searchTermObject.search_group = category
                    user = User.objects.get(pk=request.user.id)
                    searchTermObject.user_id = user.pk

                    # check if the term is already in the database.
                    exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                        search_term=searchTerm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        searchResults = Search.objects.filter(search_term_iexact=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        searchResults = Search.objects.filter(search_term=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if (len(searchResults) == 1):
                            singleResults = Search.objects.filter(search_term=searchTerm).filter(
                                search_group=category).exclude(user=request.user.id).first()
                            subject = "We Found a Match at Girl Tallk"
                            message = request.user.username + " " + searchTerm + " found a match in Girl Tallk.Please visit the website to initiate a chat"
                            receiver = singleResults.user.email
                            send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)
                            searchTermObject.save()
                        else:
                            searchTermObject.save()

                elif category != 'facebook' and subexists ==0:
                    message=format_html('OOPS! Kindly subscribe to enjoy our full search capability.In this free mode you are only allowed to search with facebook.Please click <a href="{}">Here</a> to subscribe',reverse('subscription:subscriptionplans'))
                    messages.error(request,message)
                else:
                    searchTermObject.search_term = searchTerm
                    searchTermObject.search_group = category
                    user = User.objects.get(pk=request.user.id)
                    searchTermObject.user_id = user.pk

                    # check if the term is already in the database.
                    exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                        search_term=searchTerm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        searchResults = Search.objects.filter(search_term=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        searchResults = Search.objects.filter(search_term=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if (len(searchResults) == 1):
                            singleResults = Search.objects.filter(search_term=searchTerm).filter(
                                search_group=category).exclude(user=request.user.id).first()
                            subject = "We Found a Match at Girl Tallk"
                            message = request.user.username + " " + searchTerm + " found a match in Girl Tallk.Please visit the website to initiate a chat"
                            receiver = singleResults.user.email
                            send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)
                            searchTermObject.save()
                        else:
                            searchTermObject.save()

    return  render(request,'subscriber/matchalgo.html',{'searchResults':searchResults,'total':len(searchResults),'myFriends':myFriends})


#Logout
def logoutView(request):
    logout(request)
    return  redirect('accounts:signin')


''''
This is where we process the chat system.
'''
def processChat(request,receiver_id):
    messageO=Messages()
    if request.method == 'POST':
        senderinstance= User.objects.get(pk=request.user.id)
        messageO.sender=request.user
        receiverinstance = User.objects.get(pk=receiver_id)
        messageO.receiver=receiverinstance
        messageO.message_text=request.POST['message']
        messageO.save()

'''
Process Subscription
'''






#get my friends
def getMyFriends(request,username):
    l_user=User.objects.get(username=username)
    friends=Messages.objects.filter(sender=l_user).count()
    return friends
#Update PrOfile
@login_required(login_url='accounts:signin')
def update_profile(request):
    if request.method == 'POST':
        profile_image=request.POST['image_name']
        user=User.objects.get(pk=request.user.id)
        UserProfile.objects.create(user=user,profile_image_name=profile_image)
        messages.error(request,"Profile image has been updated successfully")
        return redirect('accounts:dashboard')
    return  render(request,'subscriber/update_profile.html')

