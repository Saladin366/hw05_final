from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import path

from . import views

app_name = 'users'

PASS_CHANGE_FORM = 'users/password_change_form.html'
PASS_CHANGE_DONE = 'users/password_change_done.html'
PASS_RESET_FORM = 'users/password_reset_form.html'
PASS_RESET_DONE = 'users/password_reset_done.html'
PASS_RESET_CONF = 'users/password_reset_confirm.html'
PASS_RESET_COMP = 'users/password_reset_complete.html'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('password_change/',
         PasswordChangeView.as_view(template_name=PASS_CHANGE_FORM),
         name='password_change'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view(template_name=PASS_CHANGE_DONE),
         name='password_change_done'),
    path('password_reset/',
         PasswordResetView.as_view(template_name=PASS_RESET_FORM),
         name='password_reset'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(template_name=PASS_RESET_DONE),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name=PASS_RESET_CONF),
         name='reset_token'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(template_name=PASS_RESET_COMP),
         name='reset_done'),
]
