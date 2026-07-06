"""
Management command: seed_fruits
================================
Populates the database with 8 sample fruit categories and fruits.

Usage:
    python manage.py seed_fruits          # Add fruits (skip if already present)
    python manage.py seed_fruits --clear  # Delete ALL fruits & categories first, then re-seed

Run this ONCE after first migration to get sample data in the admin.
"""
from django.core.management.base import BaseCommand
from store.models import Category, Fruit


# ── Sample Data ───────────────────────────────────────────────────
# Structure:
#   category_name → list of fruit dicts
SEED_DATA = {
    "Tropical Fruits": [
        {
            "name":        "Mango",
            "description": (
                "Known as the 'King of Fruits', our Alphonso mangoes are hand-picked "
                "at peak ripeness. Exceptionally sweet, buttery, and rich in vitamins A & C."
            ),
            "price":  "80.00",
            "stock":  120,
        },
        {
            "name":        "Pineapple",
            "description": (
                "Juicy, tropical pineapples bursting with tangy sweetness. "
                "Rich in bromelain and vitamin C — great fresh or in smoothies."
            ),
            "price":  "60.00",
            "stock":  80,
        },
        {
            "name":        "Banana",
            "description": (
                "Farm-fresh Robusta bananas — naturally sweet, energy-packed, "
                "and a perfect on-the-go snack. High in potassium and B vitamins."
            ),
            "price":  "40.00",
            "stock":  200,
        },
    ],
    "Citrus & Berry": [
        {
            "name":        "Orange",
            "description": (
                "Seedless Nagpur oranges — thin-skinned, incredibly juicy, and packed "
                "with vitamin C. Perfect for fresh juice or eating out of hand."
            ),
            "price":  "50.00",
            "stock":  150,
        },
        {
            "name":        "Pomegranate",
            "description": (
                "Deep-red Bhagwa pomegranates with jewel-like arils that burst "
                "with antioxidant-rich, sweet-tart juice. A superfood powerhouse."
            ),
            "price":  "120.00",
            "stock":  60,
        },
    ],
    "Everyday Fruits": [
        {
            "name":        "Apple",
            "description": (
                "Crisp Shimla apples — perfectly balanced sweet-tart flavour with "
                "a satisfying crunch. Rich in dietary fibre and a daily wellness staple."
            ),
            "price":  "90.00",
            "stock":  180,
        },
        {
            "name":        "Grapes",
            "description": (
                "Plump, seedless green grapes with a delicate floral sweetness. "
                "Excellent source of resveratrol and natural antioxidants."
            ),
            "price":  "70.00",
            "stock":  100,
        },
        {
            "name":        "Watermelon",
            "description": (
                "Whole Kiran watermelons — over 90% water content, naturally sweet "
                "and deeply hydrating. Perfect summer refreshment for the whole family."
            ),
            "price":  "45.00",
            "stock":  50,
        },
    ],
}


class Command(BaseCommand):
    help = (
        "Seeds the database with 3 categories and 8 sample fruits.\n"
        "Use --clear to wipe existing data before seeding."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing Category and Fruit records before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("[!] Clearing all existing fruits and categories..."))
            Fruit.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Cleared."))

        created_cats   = 0
        created_fruits = 0
        skipped_fruits = 0

        for category_name, fruits in SEED_DATA.items():
            # Get or create the category
            category, cat_created = Category.objects.get_or_create(name=category_name)
            if cat_created:
                created_cats += 1
                self.stdout.write(f"  [+] Created category: {category_name}")
            else:
                self.stdout.write(f"  [=] Category already exists: {category_name}")

            for fruit_data in fruits:
                fruit_name = fruit_data["name"]

                if Fruit.objects.filter(name=fruit_name).exists():
                    self.stdout.write(
                        self.style.WARNING(f"     [skip] Already exists: {fruit_name}")
                    )
                    skipped_fruits += 1
                    continue

                Fruit.objects.create(
                    category    = category,
                    name        = fruit_name,
                    description = fruit_data["description"],
                    price       = fruit_data["price"],
                    stock       = fruit_data["stock"],
                    is_available= True,
                )
                self.stdout.write(self.style.SUCCESS(f"     [+] Added: {fruit_name}"))
                created_fruits += 1

        # Final summary
        self.stdout.write("\n" + "-" * 50)
        self.stdout.write(self.style.SUCCESS(
            f"[DONE] Seeding complete!\n"
            f"   Categories created : {created_cats}\n"
            f"   Fruits created     : {created_fruits}\n"
            f"   Fruits skipped     : {skipped_fruits}\n"
            f"\n   Visit http://127.0.0.1:8000/admin/ to manage your fruits."
        ))
