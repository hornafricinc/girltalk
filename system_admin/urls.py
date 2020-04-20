from django.urls import path
from system_admin import views
app_name='system_admin'
urlpatterns=[
     path('login/',views.process_admin_signin,name='login'),
     path('create_account/',views.create_account,name='create_account'),
     path('accounts/',views.load_admin_dash,name='admin_dash'),
     path('accounts/payments',views.load_payments_details,name='admin_payments'),
     path('accounts/users', views.get_total_users, name='admin_users'),

     path('accounts/manage_access_codes/',views.manage_codes,name='manage_codes'),
     path('accounts/manage_system_users/',views.get_all_users,name='manage_users'),
     path('accounts/manage_finances/',views.get_all_transactions,name='manage_finances'),
]