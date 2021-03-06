from django.urls import path, re_path
from accounts import views
from django.contrib.auth import views as auth_views
app_name='accounts'

urlpatterns = [
   # path('',views.processSiteEntryCredentials,name='site_entry'),
    path('',views.LoadIndex.as_view(),name='index'),
    path('signup/',views.create_account,name='signup'),
    path('login/',views.process_user_signin,name='signin'),
    path('accounts/',views.prepareuserdashboard,name='dashboard'),
    path('accounts/view_matches',views.get_matching_users,name='matches'),
    path('accounts/facebook_instructions/',views.get_facebook_instructions,name='facebook-instructions'),
    path('logout/',views.logoutView,name='logout'),
    #path('process_subscription/', views.process_subscription, name='process_subscription'),


    re_path(r'chat/(?P<user_id>\d+)/',views.receiverDetail,name='chat'),
    path('user_profile/',views.update_profile,name='profile'),
    path('terms-and-conditions/',views.TermsAndConditions.as_view(),name='terms-and-conditions'),
    path('privacy-policy/',views.PrivacyPolicy.as_view(),name='privacy-policy'),
    path('affiliate/',views.load_affiliate,name='affiliate_description'),
    path('accounts/affiliate',views.user_affiliate_management,name='user_affiliate'),
    path('accounts/username_recovery/',views.recover_username,name='recover_username'),

    #Password Recovery.
    path('signin/password_reset/',views.reset_user_password,name='reset_user_password'),
    path('signin/password_reset_code/', views.reset_password_now, name='perform_password_reset'),




]