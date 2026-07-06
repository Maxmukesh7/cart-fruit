"""
Views for the accounts app.

register  — create a new User, log them in, redirect to home
login_view — authenticate and log in, redirect to ?next or home
logout_view — log out, redirect to home
"""
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """
    Register a new user account.

    GET:  Show blank registration form.
    POST: Validate, create User, log them in, flash success, redirect home.
    """
    # Redirect already-authenticated users
    if request.user.is_authenticated:
        return redirect('store:home')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        # EDUCATIONAL: is_valid() runs all the validation rules defined in the form (e.g. password matching, uniqueness).
        # This protects the database from bad data.
        if form.is_valid():
            # cleaned_data contains the sanitized, Python-native data safe for use.
            username = form.cleaned_data['username']
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            # Log the new user in immediately
            login(request, user)

            messages.success(
                request,
                f"Welcome to FruitCart, {username}! 🎉 Your account has been created."
            )
            return redirect('store:home')

        # Form is invalid — errors are automatically attached to the form object and displayed in the template.
        messages.error(
            request,
            "Please fix the errors below and try again."
        )

    return render(request, 'accounts/register.html', {
        'page_title': 'Create Account — FruitCart',
        'form'      : form,
    })


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Log in an existing user.

    GET:  Show login form.
    POST: Authenticate credentials, log in, redirect to ?next or home.
    """
    # Redirect already-authenticated users
    if request.user.is_authenticated:
        return redirect('store:home')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = 'Please enter both your username and password.'
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f"Welcome back, {user.username}! 🍊"
                )
                # Honour the ?next parameter (safe redirect only)
                next_url = request.POST.get('next') or request.GET.get('next', '')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('store:home')
            else:
                error = 'Incorrect username or password. Please try again.'

    return render(request, 'accounts/login.html', {
        'page_title': 'Sign In — FruitCart',
        'error'     : error,
        'next'      : request.GET.get('next', ''),
    })


@require_http_methods(['POST'])
def logout_view(request):
    """
    Log out the current user (POST only to prevent CSRF abuse).
    """
    logout(request)
    messages.success(request, "You've been signed out. See you soon! 👋")
    return redirect('store:home')
