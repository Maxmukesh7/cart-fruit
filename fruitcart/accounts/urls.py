"""
URL patterns for the accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),  # /register/
    path('login/',    views.login_view,    name='login'),     # /login/
    path('logout/',   views.logout_view,   name='logout'),    # /logout/
]
