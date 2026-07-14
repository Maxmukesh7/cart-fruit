"""
Models for the store app.

Category  — groups fruits (e.g. Tropical, Berries, Citrus)
Fruit     — individual product with price, stock, image, etc.
"""
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Organises fruits into groups."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category display name, e.g. 'Tropical Fruits'",
    )
    slug = models.SlugField(
        max_length=110,
        unique=True,
        blank=True,
        help_text="URL-safe identifier auto-generated from name.",
    )

    class Meta:
        verbose_name        = "Category"
        verbose_name_plural = "Categories"
        ordering            = ["name"]

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Fruit(models.Model):
    """Represents a fruit product available in the store."""

    # ── Unit / weight choices ─────────────────────────────────────
    UNIT_KG     = 'kg'
    UNIT_G      = 'g'
    UNIT_PIECE  = 'piece'
    UNIT_BOX    = 'box'
    UNIT_BASKET = 'basket'

    UNIT_CHOICES = [
        (UNIT_KG,     'kg'),
        (UNIT_G,      'g'),
        (UNIT_PIECE,  'piece'),
        (UNIT_BOX,    'box'),
        (UNIT_BASKET, 'basket'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fruits",
        help_text="The category this fruit belongs to.",
    )
    name = models.CharField(
        max_length=150,
        help_text="Name of the fruit, e.g. 'Red Apple'",
    )
    slug = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        help_text="URL-safe identifier auto-generated from name.",
    )
    description = models.TextField(
        blank=True,
        help_text="Short description shown on the product page.",
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Price per unit in INR (₹).",
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default=UNIT_PIECE,
        help_text=(
            "The selling unit for this fruit. "
            "Use 'g' or 'kg' with the Weight field; "
            "'piece', 'box', or 'basket' for count-based items."
        ),
    )
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Numeric weight/quantity. "
            "Only used when Unit is 'g' or 'kg'. "
            "E.g. enter 250 for '250 g', or 1 for '1 kg'. "
            "Leave blank for piece/box/basket units."
        ),
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Number of units currently in stock.",
    )
    image = models.ImageField(
        upload_to="fruits/",   # Saved to MEDIA_ROOT/fruits/
        null=True,
        blank=True,
        help_text="Product image (optional). Upload via admin.",
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this fruit from the store.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Fruit"
        verbose_name_plural = "Fruits"
        ordering            = ["name"]

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        """True if the fruit is available and has stock > 0."""
        return self.is_available and self.stock > 0

    @property
    def unit_display(self):
        """
        Human-readable unit label for display next to the price.

        Examples:
            unit='kg',  weight=1    → '1 kg'
            unit='kg',  weight=None → 'kg'
            unit='g',   weight=250  → '250 g'
            unit='g',   weight=None → 'g'
            unit='piece'            → 'piece'
            unit='box'              → 'box'
            unit='basket'           → 'basket'
        """
        if self.unit in (self.UNIT_KG, self.UNIT_G) and self.weight:
            return f"{self.weight} {self.unit}"
        return self.unit


# ── Stage 6: Orders ────────────────────────────────────────────────────────

class Order(models.Model):
    """Represents a customer's placed order."""

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The customer who placed this order."
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Grand total of the order at the time of purchase."
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username} ({self.status})"


class OrderItem(models.Model):
    """Represents a single line item within an Order."""
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    fruit = models.ForeignKey(
        Fruit, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    # Store name historically in case the fruit is deleted or renamed later
    fruit_name = models.CharField(max_length=150)

    # Store the unit display string historically (e.g. '250 g', '1 kg', 'piece')
    unit_display = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="Unit label at the time of purchase, e.g. '250 g' or 'piece'.",
    )

    # Store price historically
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.fruit_name} (Order #{self.order.pk})"


class Wishlist(models.Model):
    """Represents a fruit wishlisted/favorited by a user."""

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        help_text="The customer who wishlisted this fruit."
    )
    fruit = models.ForeignKey(
        Fruit,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        help_text="The fruit that is wishlisted."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'fruit')
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.fruit.name}"

