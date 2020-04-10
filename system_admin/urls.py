from django.urls import path
from system_admin import views
app_name='system_admin'
urlpatterns=[
     path('accounts/',views.load_admin_dash,name='admin_dash'),
     path('accounts/payments',views.load_payments_details,name='admin_payments'),
     path('accounts/users', views.get_total_users, name='admin_users'),
]