"""
store/cart.py — Session-based shopping cart helper.

The cart is stored entirely in the user's session under the key CART_SESSION_KEY.
Structure::

    session['fruitcart'] = {
        '<fruit_id>': {
            'fruit_id'    : int,
            'name'        : str,
            'price'       : str,   # decimal stored as string for JSON safety
            'unit_display': str,   # e.g. '250 g', '1 kg', 'piece'
            'image_url'   : str,
            'quantity'    : int,
            'subtotal'    : str,   # price * quantity, stored as string
        },
        ...
    }

Nothing is saved to the database — the cart lives only in the session.
"""

from decimal import Decimal

CART_SESSION_KEY = 'fruitcart'


class Cart:
    """
    Wraps the session cart with add / update / remove helpers.

    Usage::

        cart = Cart(request)
        cart.add(fruit, quantity=2)
        cart.update(fruit_id, quantity=3)
        cart.remove(fruit_id)
        for item in cart:
            print(item['name'], item['quantity'])
        print(cart.total_price)
        print(cart.total_items)
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[CART_SESSION_KEY] = cart
        self._cart = cart

    # ── Internal helpers ────────────────────────────────────────────

    def _save(self):
        """Mark the session as modified so Django persists it."""
        self.session.modified = True

    @staticmethod
    def _key(fruit_id):
        return str(fruit_id)

    # ── Mutations ───────────────────────────────────────────────────

    def add(self, fruit, quantity=1):
        """
        Add *quantity* units of *fruit* to the cart.

        If the fruit is already in the cart, increments the quantity.
        Quantity is capped at the fruit's current stock level.

        Returns the final quantity stored (after capping).
        """
        key = self._key(fruit.pk)
        price = Decimal(str(fruit.price))

        if key not in self._cart:
            self._cart[key] = {
                'fruit_id'    : fruit.pk,
                'name'        : fruit.name,
                'slug'        : fruit.slug,
                'price'       : str(price),
                'unit_display': fruit.unit_display,   # e.g. '250 g' or 'piece'
                'image_url'   : fruit.image.url if fruit.image else '',
                'quantity'    : 0,
                'subtotal'    : '0.00',
            }

        # Cap at available stock
        new_qty = self._cart[key]['quantity'] + quantity
        new_qty = min(new_qty, fruit.stock)

        self._cart[key]['quantity'] = new_qty
        self._cart[key]['subtotal'] = str(price * new_qty)
        self._save()
        return new_qty


    def update(self, fruit, quantity):
        """
        Set the quantity of *fruit* to exactly *quantity*.

        Quantity is clamped to [0, fruit.stock].
        Passing 0 removes the item.

        Returns the final quantity (0 means removed).
        """
        key = self._key(fruit.pk)
        if key not in self._cart:
            return 0

        quantity = max(0, min(int(quantity), fruit.stock))

        if quantity == 0:
            self.remove(fruit.pk)
            return 0

        price = Decimal(self._cart[key]['price'])
        self._cart[key]['quantity'] = quantity
        self._cart[key]['subtotal'] = str(price * quantity)
        self._save()
        return quantity

    def remove(self, fruit_id):
        """Remove a fruit from the cart entirely."""
        key = self._key(fruit_id)
        if key in self._cart:
            del self._cart[key]
            self._save()

    def clear(self):
        """Empty the cart completely."""
        self.session[CART_SESSION_KEY] = {}
        self._cart = self.session[CART_SESSION_KEY]
        self._save()

    # ── Computed properties ─────────────────────────────────────────

    @property
    def total_price(self):
        """Grand total across all items as a Decimal."""
        return sum(Decimal(item['subtotal']) for item in self._cart.values())

    @property
    def total_items(self):
        """Total number of individual units in the cart."""
        return sum(item['quantity'] for item in self._cart.values())

    @property
    def is_empty(self):
        return len(self._cart) == 0

    # ── Iteration ───────────────────────────────────────────────────

    def __iter__(self):
        """
        Yield each cart item dict, with Decimal price/subtotal added for templates.
        """
        for item in self._cart.values():
            yield {
                **item,
                'price_dec'   : Decimal(item['price']),
                'subtotal_dec': Decimal(item['subtotal']),
            }

    def __len__(self):
        return len(self._cart)

    def __contains__(self, fruit_id):
        return self._key(fruit_id) in self._cart

    def get_quantity(self, fruit_id):
        """Return the current quantity for a fruit, or 0 if not in cart."""
        item = self._cart.get(self._key(fruit_id))
        return item['quantity'] if item else 0
