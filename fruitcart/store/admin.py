"""
Admin configuration for the store app.

Provides a richly customised Django admin interface for
Category and Fruit models — with list displays, filters,
search, inline editing, and image previews.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Fruit, Order, OrderItem, Wishlist


# ── Category Admin ────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display  = ("name", "slug", "fruit_count")

    # Fields that become clickable links to the detail page
    list_display_links = ("name",)

    # Pre-populate slug from name in the change form
    prepopulated_fields = {"slug": ("name",)}

    # Quicksearch
    search_fields = ("name",)

    def fruit_count(self, obj):
        """Show how many fruits belong to this category."""
        count = obj.fruits.count()
        return format_html('<b>{}</b>', count)
    fruit_count.short_description = "# Fruits"


# ── Fruit Admin ───────────────────────────────────────────────────
@admin.register(Fruit)
class FruitAdmin(admin.ModelAdmin):
    # ── List view ────────────────────────────────────────────────
    list_display = (
        "image_preview",   # Thumbnail on the left
        "name",
        "category",
        "price_display",
        "unit",
        "weight",
        "stock",
        "is_available",    # Editable toggle directly in the list
        "created_at",
    )
    list_display_links = ("name",)

    # Enable in-line editing of these columns without opening a detail page
    list_editable = ("stock", "is_available")

    # Sidebar filter panel
    list_filter = ("is_available", "category", "created_at")

    # Columns to sort on click
    ordering = ("name",)

    # Quick text search across these fields
    search_fields = ("name", "description", "category__name")

    # Pre-populate slug from name
    prepopulated_fields = {"slug": ("name",)}

    # Show 20 items per page
    list_per_page = 20

    # Date hierarchy drilldown at the top
    date_hierarchy = "created_at"

    # ── Detail / change form layout ──────────────────────────────
    fieldsets = (
        ("Basic Information", {
            "fields": ("category", "name", "slug", "description"),
            "description": "Core details about the fruit.",
        }),
        ("Pricing & Stock", {
            "fields": ("price", "unit", "weight", "stock", "is_available"),
            "description": (
                "Set the selling price, unit type (kg / g / piece / box / basket), "
                "optional numeric weight (for g/kg units), and stock quantity."
            ),
        }),
        ("Media", {
            "fields": ("image", "image_preview_large"),
            "description": "Upload a product photo (JPG/PNG recommended).",
        }),
        ("Timestamps (read-only)", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),  # Collapsible section
        }),
    )

    # These are auto-managed — show them as read-only
    readonly_fields = ("created_at", "updated_at", "image_preview_large")

    # ── Custom display methods ───────────────────────────────────
    def image_preview(self, obj):
        """Small thumbnail shown in the list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;'
                'border-radius:8px;border:1px solid #e5e7eb;" />',
                obj.image.url,
            )
        return format_html(
            '<span style="font-size:1.6rem;line-height:1;">{}</span>',
            _fruit_emoji(obj.name),
        )
    image_preview.short_description = "Photo"

    def image_preview_large(self, obj):
        """Larger preview inside the detail form."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:200px;'
                'object-fit:cover;border-radius:12px;border:1px solid #e5e7eb;" />',
                obj.image.url,
            )
        return "No image uploaded yet."
    image_preview_large.short_description = "Current Image"

    def price_display(self, obj):
        """Format price with ₹ symbol, bold, and unit label."""
        return format_html('<b>₹ {}</b> <span style="color:#6b7280;font-size:0.8em">/ {}</span>',
                           obj.price, obj.unit_display)
    price_display.short_description = "Price / Unit"
    price_display.admin_order_field = "price"


def _fruit_emoji(name: str) -> str:
    """Return a matching emoji for common fruit names (fallback display)."""
    mapping = {
        "apple":        "🍎",
        "banana":       "🍌",
        "orange":       "🍊",
        "mango":        "🥭",
        "grapes":       "🍇",
        "watermelon":   "🍉",
        "pineapple":    "🍍",
        "pomegranate":  "❤️",
        "strawberry":   "🍓",
        "pear":         "🍐",
        "cherry":       "🍒",
        "peach":        "🍑",
        "lemon":        "🍋",
    }
    return mapping.get(name.lower(), "🍑")


# ── Stage 6: Order Admin ──────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('fruit', 'fruit_name', 'unit_display', 'price', 'quantity', 'subtotal')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'total_amount', 'status', 'created_at', 'download_invoice_link')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'full_name', 'phone')
    readonly_fields = ('user', 'full_name', 'phone', 'address', 'city', 'pincode', 'total_amount', 'created_at', 'download_invoice_link')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ("Customer Info", {
            "fields": ('user', 'full_name', 'phone')
        }),
        ("Shipping Address", {
            "fields": ('address', 'city', 'pincode')
        }),
        ("Order Details", {
            "fields": ('total_amount', 'status', 'created_at', 'download_invoice_link')
        })
    )

    def download_invoice_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('store:download_invoice', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank" style="padding: 4px 8px; background: var(--color-primary, #2E7D32); color: white; border-radius: 4px; text-decoration: none;">Download PDF</a>', url)
    download_invoice_link.short_description = "Invoice"


    def has_add_permission(self, request):
        return False  # Orders should only be created via checkout


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fruit', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'fruit__name')


# ── Admin Site Branding ───────────────────────────────────────────
admin.site.site_header  = "🍊 FruitCart Admin"
admin.site.site_title   = "FruitCart Admin"
admin.site.index_title  = "Store Management Dashboard"

