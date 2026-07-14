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


def wishlist_context(request):
    """Add wishlist count and user's wishlisted fruit IDs to every template context."""
    if request.user.is_authenticated:
        from .models import Wishlist
        wishlist_items = Wishlist.objects.filter(user=request.user)
        wishlist_count = wishlist_items.count()
        wishlist_ids = list(wishlist_items.values_list('fruit_id', flat=True))
    else:
        wishlist_count = 0
        wishlist_ids = []
    return {
        'wishlist_count': wishlist_count,
        'wishlist_ids': wishlist_ids,
    }

