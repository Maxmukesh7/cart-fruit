"""
store/context_processors.py

Injects `cart_count` and `cart_total` into every template context so the
navbar cart badge and any other global cart indicator works without each
view explicitly passing these values.
"""
from .cart import Cart


def cart_context(request):
    """Add cart summary to every template context."""
    cart = Cart(request)
    return {
        'cart_count': cart.total_items,
        'cart_total': cart.total_price,
    }
