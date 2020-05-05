from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import TemplateView

from accounts.forms import LoginForm, UserAccountForm
from accounts.models import Search, Messages, Profile
from django.core.mail import send_mail

from girltalk import settings
from subscription.models import ClientSubscription

#This is the homepage;
from system_admin.models import AccessCodes

restricted_numbers=['14072096283','407.209.6283','407.782.0157','4077820157']

class LoadIndex(TemplateView):
    template_name = 'home.html'

class TermsAndConditions(TemplateView):
    template_name = 'termsandconditions.html'
class PrivacyPolicy(TemplateView):
    template_name = 'privacy_policy.html'

def fetch_chats(request,user_id):
    chats= Messages.objects.filter(sender=request.user.id).filter(receiver=user_id).order_by('created_at') | Messages.objects.filter(sender=user_id).filter(receiver=request.user.id).order_by('created_at')
    return  chats
#Receiver Details

def receiverDetail(request,user_id):
    receiver=None
    receiver_id=int(user_id)
    userdetail=User.objects.filter(pk=receiver_id)
    myFriends=getMyFriends(request.user.username)
    chats =fetch_chats(request,user_id)
    if len(userdetail)>0:
        receiver=userdetail[0]
        ''''
        Here is where the chat will really take place.
        '''
        processChat(request,user_id)
        #Get the latest results
        chats =fetch_chats(request,user_id) #Messages.objects.filter(sender=request.user.id).filter(receiver=user_id).order_by('created_at')|  Messages.objects.filter(sender=user_id).filter(receiver=request.user.id).order_by('created_at')
    else:
        receiver=None
    return  render(request,'subscriber/instant_messaging.html',{'receiver':receiver,'chats':chats,'myFriends':myFriends})


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
    myFriends = getMyFriends(request.user.username)
    searchTermObject = Search()
    entered_term = ''
    searchResults=''
    if request.method == 'POST':
        entered_term = request.POST['searchTerm']
        searchTerm=entered_term.lstrip()
        category = request.POST['cat']
        if(category == 'null'):
            messages.error(request,'You have not selected any category')
        else:
            if searchTerm == '':
                messages.error(request,'You have not entered a term to search')
            elif searchTerm in restricted_numbers:
                messages.error(request,'There are no results for this search')
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
                        search_term__iexact=searchTerm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        searchResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        searchResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if (len(searchResults) == 1):
                            singleResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
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
                        search_term__iexact=searchTerm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        searchResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        searchResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if (len(searchResults) == 1):
                            singleResults = Search.objects.filter(search_term__iexact=searchTerm).filter(
                                search_group=category).exclude(user=request.user.id).first()
                            subject = "WE FOUND A MATCH FOR SEARCH TERM"
                            message = request.user.username + ",  we found a match for Search Term.Please visit us to initiate a chat"
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







''''
****************GET MY FRIENDS********************
'''
def getMyFriends(username):
    l_user=User.objects.get(username=username)
    friends=Messages.objects.all().filter(Q(receiver=l_user) | Q(sender=l_user)).exclude(receiver=l_user).distinct()

    friendsDict={}
    for friend in friends:
        if friend.receiver.id in friendsDict.values():
            pass
        else:
            friendsDict[friend.receiver.id]=friend.receiver.username

    #friends=Messages.objects.select_related('receiver').all().exclude(receiver=l_user).distinct()
    return  friendsDict
#Update PrOfile
@login_required(login_url='accounts:signin')
def update_profile(request):
    if request.method == 'POST':
        try:
            Profile.objects.get(user=request.user)
            Profile.objects.filter(user=request.user).update(profile_image_name=request.POST['image_name'])
            return redirect('accounts:dashboard')
        except Profile.DoesNotExist:
            profile_image=request.POST['image_name']
            user=User.objects.get(pk=request.user.id)
            Profile.objects.create(user=user,profile_image_name=profile_image)
            return redirect('accounts:dashboard')
    return  render(request,'subscriber/update_profile.html')





