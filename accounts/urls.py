from django.urls import path, re_path
from accounts import views
app_name='accounts'

urlpatterns = [
    path('',views.processSiteEntryCredentials,name='site_entry'),
    path('home/',views.LoadIndex.as_view(),name='index'),
    path('invite_test/',views.processSiteEntryCredentials,name='inviteCheck'),
    path('signup/',views.create_account,name='signup'),
    path('login/',views.process_user_signin,name='signin'),
    path('accounts/',views.loadUserDashBoard,name='dashboard'),
    path('logout/',views.logoutView,name='logout'),
    path('contact_us/',views.LoadContactUS.as_view(),name='contact_us'),
    #path('process_subscription/', views.process_subscription, name='process_subscription'),


    re_path(r'chat/(?P<user_id>\d+)/',views.receiverDetail,name='chat'),
]