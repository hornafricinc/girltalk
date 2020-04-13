from django.urls import path

from subscription import views
app_name='subscription'

urlpatterns=[
    path('',views.LoadHome.as_view(),name='home'),
    path('subscribe/',views.subscribe,name='subscriptionplans'),
    path('process_payment/',views.process_payment,name='process_subscription'),
    path('subscription_done/',views.payment_done,name='subscription_done'),
    path('subscription_cancelled/', views.payment_canceled, name='subscription_cancelled'),

]