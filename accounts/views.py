from django.contrib.sessions.models import Session
from django.utils import timezone
from djstripe.models import Subscription
import stripe
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, user_logged_in
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import TemplateView

from accounts.forms import LoginForm, UserAccountForm
from accounts.models import Search, Messages, Profile, UserSession
from django.core.mail import send_mail

from girltalk import settings
from girltalk.settings import EMAIL_HOST_USER
from subscription.models import ClientSubscription, SubscriberSubscriptionDetails

#This is the homepage;
from system_admin.models import AccessCodes

restricted_numbers=['14072096283','407.209.6283','407.782.0157','4077820157','@iamshagritty' '@producertybandit','@IAMSHAGRITTY','@PRODUCERTYBANDIT']
stripe.api_key=settings.STRIPE_LIVE_SECRET_KEY
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
    receiver_id = int(user_id)
    #Receiver session data.
    #all_sessions=Session.objects.filter(expire_date__gte=timezone.now())
    #uid_list=[]
    receiver_status=''



    '''
    for session in all_sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))
        #Now i have a list of all active users id.
        if receiver_id in uid_list:
            receiver_status='Online'
        else:
            receiver_status='Offline'
        '''
            


    userdetail=User.objects.filter(pk=receiver_id)
    user=User.objects.get(pk=receiver_id)
    #Session data
    usersession_info = UserSession.objects.filter(user=user)
    sessiondata="Offline"
    if len(usersession_info) > 0:
        sessiondata="Online"

    #for session_info in usersession_info:
    #    expiration_date = session_info.user
    #End of session data
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
    return  render(request,'subscriber/instant_messaging.html',{'receiver':receiver,'receiver_status':sessiondata,'chats':chats,'myFriends':myFriends})


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
    myFriends = getMyFriends(request.user.username)
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
    return  render(request,'subscriber/update_profile.html',{'myFriends':myFriends})

#Def users Search Terms;
@login_required(login_url='accounts:signin')
def get_matching_users(request):
    search_terms=Search.objects.filter(user=request.user)
    searches = ''
    if request.method == 'POST':
        full_term=request.POST['searchTerm']
        split_text=full_term.split('-')
        category=split_text[0]
        term=split_text[1]
        searches = Search.objects.filter(search_term__iexact=term).filter(
            search_group=category).exclude(user=request.user.id)


    return render(request,'subscriber/search_term_match.html',{'search_terms':search_terms,'searches':searches,})



def get_alerts(request):
    active_user_searches=Search.objects.filter(user=request.user)
    my_search=[]
    for term in active_user_searches:
        my_search.append(term.search_term)
    other_users=Search.objects.exclude(user=request.user)
    alerts={}
    for single_user_instance in other_users:
        if single_user_instance.search_term in my_search:
            alerts[single_user_instance.user.id]=single_user_instance.user.username
        else:
            pass
    return alerts



#This is a function to prepare a facebook search which is not unique.
def validate_facebook_search(entered_value):
    correct=False
    #Screen not a single word
    if len(entered_value.split())>1:
        #Check if dot exists since it seperates user profile
        if "." in entered_value:
            correct=True
        else:
           correct=False
    else:
        correct=True
    return  correct

#Load the Affiliate Link
def load_affiliate(request):
    return render(request,'affiliate_description.html')
#Logged in user;
@login_required(login_url='accounts:signin')
def user_affiliate_management(request):
    return render(request,'subscriber/user_affiliate.html')

@login_required(login_url='accounts:signin')
def prepareuserdashboard(request):
    #Important variables to be used in the template
    match_alerts = get_alerts(request)
    myfriends = getMyFriends(request.user.username)
    search_results = ''
    subscription_status=''
    #Search Term Object
    searchTermObject = Search()
    # user details to be used in subscription.
    try:
        user = User.objects.get(username=request.user.username)
        subscription = SubscriberSubscriptionDetails.objects.filter(user=user).latest('date_subscribed')
    except SubscriberSubscriptionDetails.DoesNotExist:
        subscription=None

    if subscription is None:
        subscription_status=''
    else:
        subscription_check =Subscription.objects.get(pk=subscription.subscription_id) #stripe.Subscription.retrieve(subscription.subscription_id)
        subscription_status = subscription_check.status
    if request.method == 'POST':

        #Get data from the forms.
        entered_term = request.POST['searchTerm']
        searchterm = entered_term.lstrip()
        category = request.POST['cat']
        #Here we check if the user has exceeded the number of three searches given unto him.
        if get_user_total_searches(request.user)<3:
           #There is need to confirm this into a function of its own.
            # Prepare the data for database update;
            searchTermObject.search_term = searchterm.lower()
            searchTermObject.search_group = category
            user = User.objects.get(pk=request.user.id)
            searchTermObject.user_id = user.pk

            if category == 'null' or searchterm == '':
                messages.error(request, 'You have not selected any category or entered any search term')
            elif searchterm in restricted_numbers:
                messages.error(request, 'There is no match.')
            else:
                # Validate facebook now.
                if category == 'facebook' and validate_facebook_search(searchterm):
                    # check if the term is already in the database.
                    exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                        search_term__iexact=searchterm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if len(search_results) == 1:
                            singleResults = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id).first()
                            subject = "We Found a Match at Girl Tallk"
                            receiver = singleResults.user.email
                            user = User.objects.get(email=receiver)
                            message = user.username + ",we  found a match in Girl Tallk.Please visit the website to initiate a chat"
                            send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)
                            searchTermObject.save()
                        else:
                            searchTermObject.save()
                elif category == 'facebook' and validate_facebook_search(searchterm) == False:
                    messages.error(request, "Invalid Facebook ID.Kindly enter correct facebook ID")

                # Handle non facebook related searches.
                else:
                    # check if the term is already in the database.
                    exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                        search_term__iexact=searchterm).count()
                    if exists > 0:
                        ''''
                        Since it exists We have now to query the database for records that 
                        do not include my keyword.
                        '''
                        search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                            search_group=category).exclude(user=request.user.id)

                    else:
                        # Fetch results from database.
                        search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                            search_group=category).exclude(user=request.user.id)
                        if len(search_results) == 1:
                            singleResults = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id).first()
                            subject = "We Found a Match at Girl Tallk"
                            receiver = singleResults.user.email
                            user = User.objects.get(email=receiver)
                            message = user.username + ",we  found a match in Girl Tallk.Please visit the website to initiate a chat"

                            send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)
                            searchTermObject.save()
                        else:
                            searchTermObject.save()
        #Perform the search
        else:
            if subscription_status =='active' or subscription_status =='trialing':
                #Prepare the data for database update;
                searchTermObject.search_term = searchterm.lower()
                searchTermObject.search_group = category
                user = User.objects.get(pk=request.user.id)
                searchTermObject.user_id = user.pk

                if category == 'null' or searchterm == '':
                    messages.error(request, 'You have not selected any category or entered any search term')
                elif searchterm in restricted_numbers:
                    messages.error(request, 'There is no match.')
                else:
                    #Validate facebook now.
                    if category == 'facebook' and validate_facebook_search(searchterm):
                        # check if the term is already in the database.
                        exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                            search_term__iexact=searchterm).count()
                        if exists > 0:
                            ''''
                            Since it exists We have now to query the database for records that 
                            do not include my keyword.
                            '''
                            search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id)

                        else:
                            # Fetch results from database.
                            search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id)
                            if len(search_results) == 1:
                                singleResults = Search.objects.filter(search_term__iexact=searchterm).filter(
                                    search_group=category).exclude(user=request.user.id).first()
                                subject = "We Found a Match at Girl Tallk"
                                receiver = singleResults.user.email
                                user = User.objects.get(email=receiver)
                                message = user.username + ",we  found a match in Girl Tallk.Please visit the website to initiate a chat"
                                send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver],fail_silently=False)
                                searchTermObject.save()
                            else:
                                searchTermObject.save()
                    elif category == 'facebook' and validate_facebook_search(searchterm)==False:
                        messages.error(request,"Invalid Facebook ID.Kindly enter correct facebook ID")

                    #Handle non facebook related searches.
                    else:
                        # check if the term is already in the database.
                        exists = Search.objects.filter(user=request.user.id).filter(search_group=category).filter(
                            search_term__iexact=searchterm).count()
                        if exists > 0:
                            ''''
                            Since it exists We have now to query the database for records that 
                            do not include my keyword.
                            '''
                            search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id)

                        else:
                            # Fetch results from database.
                            search_results = Search.objects.filter(search_term__iexact=searchterm).filter(
                                search_group=category).exclude(user=request.user.id)
                            if len(search_results) == 1:
                                singleResults = Search.objects.filter(search_term__iexact=searchterm).filter(
                                    search_group=category).exclude(user=request.user.id).first()
                                subject = "We Found a Match at Girl Tallk"
                                receiver = singleResults.user.email
                                user = User.objects.get(email=receiver)
                                message = user.username + ",we  found a match in Girl Tallk.Please visit the website to initiate a chat"

                                send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)
                                searchTermObject.save()
                            else:
                                searchTermObject.save()




            else:
                message = format_html('Dear Girl Tallk user, your subscription is not active. Please <a href="{}">activate now</a>',reverse('subscription:subscriptionplans'))
                messages.error(request, message)

            # User has subscribed.



    context={
        's_status':subscription_status,
        'searchResults': search_results, 'total': len(search_results), 'myFriends': myfriends,
         'match_alerts': match_alerts, 'total_alerts': len(match_alerts),

    }
    return render(request, 'subscriber/matchalgo.html',context)




@login_required(login_url='accounts:signin')
def get_facebook_instructions(request):
    return render(request,'subscriber/facebook_instructions.html')

#This is the function to help those people who have forgotten their usernames;
def recover_username(request):
    if request.method == 'POST':
        email_address=request.POST['email']
        #Get the user with the registered email address;
        user=User.objects.filter(email=email_address).exists()
        if user:
            userObject=User.objects.filter(email=email_address)
            username=""
            for user in userObject:
                username=user.username
            # Sacco Manager should receive an email
            subject = "GIRLTALLK USERNAME RECOVERY"
            message = "Your GirlTallk Username is:"+username
            send_mail(subject, message, EMAIL_HOST_USER, [request.POST['email']], fail_silently=True)
            messages.success(request,"Your username has been emailed to the email address. Kindly log in to your email address and check.")
        else:
            messages.error(request,'The supplied email address does not exist')
    return render(request,'accounts/recover_username.html')
#This is the function to get total number of seraches by a client;
def get_user_total_searches(user):
    proceed=False
    try:
        total_searches=Search.objects.filter(user=user).count()
    except Search.DoesNotExist:
        total_searches=0
    return  total_searches
    '''
        if total_searches <= 3:
        proceed=True
    else:
        proceed=False
    return proceed
    '''
#This is the function to get the status of the logged in user.
def user_logged_in_handler(sender,request,user,**kwargs):
    UserSession.objects.get_or_create(user=user,session_id=request.session.session_key)
user_logged_in.connect(user_logged_in_handler)

