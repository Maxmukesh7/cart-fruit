from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    """
    Collects shipping information for an order.
    """
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'city', 'pincode']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-field__input', 'placeholder': 'Jane Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-field__input', 'placeholder': '10-digit mobile number'}),
            'address': forms.Textarea(attrs={'class': 'form-field__input', 'rows': 3, 'placeholder': 'Street address, apartment, suite, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-field__input', 'placeholder': 'e.g. Mumbai'}),
            'pincode': forms.TextInput(attrs={'class': 'form-field__input', 'placeholder': '6-digit PIN code'}),
        }
