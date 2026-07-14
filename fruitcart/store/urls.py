"""
URL patterns for the store app.
"""
from django.urls import path
from . import views

app_name = 'store'  # Enables namespacing: {% url 'store:home' %}

urlpatterns = [
    # ── Store pages ────────────────────────────────────────────────
    path('', views.home, name='home'),                                    # /
    path('fruits/', views.fruits, name='fruits'),                         # /fruits/
    path('fruits/<slug:slug>/', views.fruit_detail, name='fruit_detail'), # /fruits/<slug>/

    # ── Cart ───────────────────────────────────────────────────────
    path('cart/', views.cart_detail, name='cart'),                        # /cart/
    path('cart/add/<int:fruit_id>/', views.cart_add, name='cart_add'),    # /cart/add/<id>/
    path('cart/update/<int:fruit_id>/', views.cart_update, name='cart_update'),  # /cart/update/<id>/
    path('cart/remove/<int:fruit_id>/', views.cart_remove, name='cart_remove'),  # /cart/remove/<id>/
    # ── Stage 6: Checkout & Orders ─────────────────────────────────
    path('checkout/', views.checkout, name='checkout'),                   # /checkout/
    path('orders/', views.orders_list, name='orders'),                    # /orders/
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'), # /orders/<id>/

    # ── Wishlist ───────────────────────────────────────────────────
    path('wishlist/', views.wishlist_detail, name='wishlist'),
    path('wishlist/toggle/<int:fruit_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('wishlist/move-to-cart/<int:fruit_id>/', views.wishlist_move_to_cart, name='wishlist_move_to_cart'),
]

