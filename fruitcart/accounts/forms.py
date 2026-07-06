"""
Forms for the accounts app.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    """
    User registration form.

    Validates that:
    - Username is not already taken (case-insensitive)
    - Email is not already registered
    - Password meets Django's password validators
    - Passwords match
    """

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'id': 'id_username',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        }),
        label='Username',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'id': 'id_email',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        }),
        label='Email address',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'id_password1',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        }),
        label='Password',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'id_password2',
            'placeholder': 'Repeat your password',
            'autocomplete': 'new-password',
        }),
        label='Confirm password',
    )

    # ── Field-level validation ──────────────────────────────────────

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('That username is already taken. Please choose another.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            try:
                # Run Django's built-in password validators
                validate_password(password)
            except ValidationError as exc:
                raise ValidationError(list(exc.messages))
        return password

    # ── Form-level validation ───────────────────────────────────────

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('password1')
        pw2 = cleaned.get('password2')

        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', "Passwords don't match. Please try again.")

        return cleaned
