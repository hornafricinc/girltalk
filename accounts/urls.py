from django.urls import path, re_path
from accounts import views
from django.contrib.auth import views as auth_views
app_name='accounts'

urlpatterns = [
    path('',views.processSiteEntryCredentials,name='site_entry'),
    path('home/',views.LoadIndex.as_view(),name='index'),
    path('signup/',views.create_account,name='signup'),
    path('login/',views.process_user_signin,name='signin'),
    path('accounts/',views.loadUserDashBoard,name='dashboard'),
    path('logout/',views.logoutView,name='logout'),
    #path('process_subscription/', views.process_subscription, name='process_subscription'),


    re_path(r'chat/(?P<user_id>\d+)/',views.receiverDetail,name='chat'),
    path('user_profile/',views.update_profile,name='profile'),


]