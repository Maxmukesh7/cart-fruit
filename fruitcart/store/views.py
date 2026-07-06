"""
Views for the store app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Fruit, Category, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm


# ── Store pages ────────────────────────────────────────────────────

def custom_404(request, exception):
    """
    Custom 404 handler to render a branded 'Page Not Found' template.
    """
    return render(request, '404.html', status=404)


def home(request):
    """Home page — hero section welcoming users."""

    # Fetch the 4 newest available fruits for the 'Featured' section
    featured_fruits = Fruit.objects.filter(is_available=True).order_by('-created_at')[:4]

    # Fetch available fruits in the 'Tropical Fruits' category for the Tropical section
    tropical_fruits = (
        Fruit.objects
        .filter(is_available=True, category__slug='tropical-fruits')
        .select_related('category')
        .order_by('name')[:6]
    )

    context = {
        'page_title': 'FruitCart — Fresh Fruits Delivered',
        'featured_fruits': featured_fruits,
        'tropical_fruits': tropical_fruits,
    }
    return render(request, 'store/home.html', context)


def fruits(request):
    """
    Fruits listing page.

    Supports:
    - ?search=<name>   — case-insensitive name search
    - ?category=<slug> — filter by category slug
    - ?sort=<option>   — sorting (price_asc, price_desc, newest)
    - ?page=<number>   — pagination
    """
    queryset = Fruit.objects.filter(is_available=True).select_related('category')

    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # icontains is a Django ORM lookup for case-insensitive containment
        queryset = queryset.filter(name__icontains=search_query)

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            queryset = queryset.filter(category=active_category)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_desc':
        queryset = queryset.order_by('-price')
    else:  # newest
        queryset = queryset.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 8)  # Show 8 fruits per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # All categories for the filter bar
    categories = Category.objects.all()

    # Cart quantities for each fruit (so cards can show current qty)
    cart = Cart(request)

    context = {
        'page_title'    : 'Our Fruits — FruitCart',
        'fruits'        : page_obj,  # Pass the paginated object instead of raw queryset
        'categories'    : categories,
        'search_query'  : search_query,
        'active_category': active_category,
        'sort_by'       : sort_by,
        'result_count'  : paginator.count,  # Total results across all pages
        'cart'          : cart,
    }
    return render(request, 'store/fruits.html', context)


def fruit_detail(request, slug):
    """
    Fruit detail page.

    Only shows fruits that are marked is_available=True.
    Returns 404 for unknown or hidden fruits.
    """
    fruit = get_object_or_404(Fruit, slug=slug, is_available=True)
    cart = Cart(request)
    cart_qty = cart.get_quantity(fruit.pk)

    context = {
        'page_title': f'{fruit.name} — FruitCart',
        'fruit'     : fruit,
        'cart_qty'  : cart_qty,
    }
    return render(request, 'store/fruit_detail.html', context)


# ── Cart views ─────────────────────────────────────────────────────

def cart_detail(request):
    """Shopping cart page — shows all items, subtotals, and grand total."""
    cart = Cart(request)
    context = {
        'page_title': 'Your Cart — FruitCart',
        'cart'      : cart,
        'cart_items': list(cart),            # list of item dicts
        'total_price': cart.total_price,
        'total_items': cart.total_items,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def cart_add(request, fruit_id):
    """
    POST /cart/add/<fruit_id>/

    Adds 1 unit (or more via form field 'quantity') of the fruit to the cart.
    Redirects back to the page the user came from, or to the cart page.
    """
    fruit = get_object_or_404(Fruit, pk=fruit_id, is_available=True)
    cart = Cart(request)

    if not fruit.in_stock:
        messages.error(request, f'Sorry, {fruit.name} is currently out of stock.')
        return redirect(request.POST.get('next', 'store:fruits'))

    try:
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(1, quantity)
    except (ValueError, TypeError):
        quantity = 1

    final_qty = cart.add(fruit, quantity=quantity)

    if final_qty < (cart.get_quantity(fruit.pk) + quantity):
        # Stock cap was applied
        messages.warning(
            request,
            f'Only {fruit.stock} unit(s) of {fruit.name} available. '
            f'Cart updated to maximum stock.'
        )
    else:
        messages.success(
            request,
            f'🍊 {fruit.name} added to your cart!'
        )

    # Redirect: respect POST 'next' (validated), then Referer, then cart
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '')
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('store:cart')


@require_POST
def cart_update(request, fruit_id):
    """
    POST /cart/update/<fruit_id>/

    Updates the quantity of a cart item. Posting quantity=0 removes it.
    """
    fruit = get_object_or_404(Fruit, pk=fruit_id)
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    final_qty = cart.update(fruit, quantity=quantity)

    if final_qty == 0:
        messages.info(request, f'{fruit.name} removed from your cart.')
    else:
        messages.success(request, f'Cart updated — {fruit.name}: {final_qty} unit(s).')

    return redirect('store:cart')


@require_POST
def cart_remove(request, fruit_id):
    """
    POST /cart/remove/<fruit_id>/

    Removes a fruit from the cart entirely.
    """
    fruit = get_object_or_404(Fruit, pk=fruit_id)
    cart = Cart(request)
    cart.remove(fruit_id)
    messages.info(request, f'{fruit.name} removed from your cart.')
    return redirect('store:cart')


# ── Stage 6: Checkout and Orders ────────────────────────────────────────

@login_required
def checkout(request):
    """
    Checkout page. Validates cart, stock, and creates order.
    EDUCATIONAL: The @login_required decorator is a security feature that ensures only authenticated users can access this view.
    """
    cart = Cart(request)
    if cart.is_empty:
        messages.warning(request, "Your cart is empty. Please add some fruits before checking out.")
        return redirect('store:cart')

    # Double check stock before showing form
    for item in cart:
        fruit = Fruit.objects.filter(pk=item['fruit_id']).first()
        if not fruit or fruit.stock < item['quantity']:
            messages.error(request, f"Sorry, {item['name']} does not have enough stock. Please update your cart.")
            return redirect('store:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # EDUCATIONAL: transaction.atomic() ensures database integrity. 
            # If any operation inside this block fails, all changes are rolled back.
            with transaction.atomic():
                # Create Order
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = cart.total_price
                order.save()

                # Create OrderItems and reduce stock
                for item in cart:
                    # EDUCATIONAL: select_for_update() locks this specific row in the database until the transaction completes.
                    # This prevents "race conditions" where two users buy the last apple at the exact same millisecond.
                    fruit = Fruit.objects.select_for_update().get(pk=item['fruit_id'])
                    
                    if fruit.stock < item['quantity']:
                        # Final safety check in atomic block
                        transaction.set_rollback(True)
                        messages.error(request, f"Oops, someone just bought {fruit.name}. Not enough stock left. Please try again.")
                        return redirect('store:cart')
                    
                    # Create line item — capture unit_display historically
                    OrderItem.objects.create(
                        order=order,
                        fruit=fruit,
                        fruit_name=item['name'],
                        unit_display=item.get('unit_display', fruit.unit_display),
                        price=item['price_dec'],
                        quantity=item['quantity'],
                        subtotal=item['subtotal_dec']
                    )
                    
                    # Reduce stock
                    fruit.stock -= item['quantity']
                    fruit.save()
                
                # Clear cart
                cart.clear()

                messages.success(request, f"Order #{order.pk} placed successfully! Thank you for shopping with us.")
                return redirect('store:order_detail', order_id=order.pk)
    else:
        form = CheckoutForm()

    context = {
        'page_title': 'Checkout — FruitCart',
        'form': form,
        'cart_items': list(cart),
        'total_price': cart.total_price,
    }
    return render(request, 'store/checkout.html', context)


@login_required
def orders_list(request):
    """List of orders for the current user."""
    orders = request.user.orders.all()
    context = {
        'page_title': 'My Orders — FruitCart',
        'orders': orders,
    }
    return render(request, 'store/orders.html', context)


@login_required
def order_detail(request, order_id):
    """Detail view of a specific order belonging to the current user."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    context = {
        'page_title': f'Order #{order.pk} — FruitCart',
        'order': order,
    }
    return render(request, 'store/order_detail.html', context)
