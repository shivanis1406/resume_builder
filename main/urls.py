from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name = 'home'),
    path('create_cv/', create_cv, name='create_cv'),
    path('resume_preview/<str:resume_id>/', resume_preview, name='resume_preview'),
    path('process_payment/<str:resume_id>/', process_payment, name='process_payment'),
    path('payment_success/<str:resume_id>/', payment_success, name='payment_success'),
    path('payment_failed/', payment_failed, name='payment_failed'),
]
