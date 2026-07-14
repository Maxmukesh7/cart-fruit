from django.test import TestCase, Client
from django.urls import reverse
from store.models import Category, Fruit

class CartAJAXTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Citrus", slug="citrus")
        self.fruit = Fruit.objects.create(
            category=self.category,
            name="Orange",
            slug="orange",
            price=20.00,
            stock=10,
            is_available=True,
            unit="piece"
        )
        self.client = Client()

    def test_ajax_cart_update(self):
        # Add fruit to cart first
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 3})
        
        # Test AJAX update to quantity 5
        response = self.client.post(
            reverse('store:cart_update', args=[self.fruit.id]),
            {'quantity': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['quantity'], 5)
        self.assertFalse(data['removed'])
        self.assertEqual(data['cart_count'], 5)
        self.assertEqual(data['total_items'], 5)
        self.assertEqual(data['line_subtotal'], "₹100.00")
        self.assertEqual(data['subtotal'], "₹100.00")
        self.assertEqual(data['grand_total'], "₹100.00")
        
        # Test standard update (non-AJAX fallback redirects)
        response_non_ajax = self.client.post(
            reverse('store:cart_update', args=[self.fruit.id]),
            {'quantity': 4}
        )
        self.assertEqual(response_non_ajax.status_code, 302)
        self.assertEqual(response_non_ajax.url, reverse('store:cart'))

    def test_ajax_cart_update_capped(self):
        # Add fruit to cart first
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 3})
        
        # Test AJAX update exceeding stock level (10)
        response = self.client.post(
            reverse('store:cart_update', args=[self.fruit.id]),
            {'quantity': 15},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        # Capped to 10 stock
        self.assertEqual(data['quantity'], 10)
        self.assertIn("maximum stock", data['message'])
        self.assertEqual(data['msg_type'], 'warning')

    def test_ajax_cart_remove(self):
        # Add fruit to cart first
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 2})
        
        # Test AJAX remove
        response = self.client.post(
            reverse('store:cart_remove', args=[self.fruit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['removed'])
        self.assertEqual(data['quantity'], 0)
        self.assertEqual(data['cart_count'], 0)

        # Test standard remove fallback
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 2})
        response_non_ajax = self.client.post(reverse('store:cart_remove', args=[self.fruit.id]))
        self.assertEqual(response_non_ajax.status_code, 302)
        self.assertEqual(response_non_ajax.url, reverse('store:cart'))

    def test_ajax_cart_update_to_zero_removes_item(self):
        # Add fruit to cart first
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 2})
        
        # Test AJAX update to quantity 0
        response = self.client.post(
            reverse('store:cart_update', args=[self.fruit.id]),
            {'quantity': 0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['removed'])
        self.assertEqual(data['quantity'], 0)
        self.assertEqual(data['cart_count'], 0)


from django.core import mail
from django.contrib.auth.models import User

class CheckoutEmailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mukesh", email="mukesh@example.com", password="password")
        self.category = Category.objects.create(name="Berries", slug="berries")
        self.fruit = Fruit.objects.create(
            category=self.category,
            name="Kiwi",
            slug="kiwi",
            price=150.00,
            stock=10,
            is_available=True,
            unit="piece"
        )
        self.client = Client()
        self.client.login(username="mukesh", password="password")

    def test_checkout_sends_confirmation_email(self):
        # Add to cart
        self.client.post(reverse('store:cart_add', args=[self.fruit.id]), {'quantity': 2})
        
        # Post checkout form
        checkout_data = {
            'full_name': 'Mukesh Kumar',
            'phone': '9876543210',
            'address': 'Flat 402, Green Glen Layout',
            'city': 'Bengaluru',
            'pincode': '560103'
        }
        
        response = self.client.post(reverse('store:checkout'), checkout_data)
        
        # Verify redirect to order details
        self.assertEqual(response.status_code, 302)
        
        # Verify order was created
        from store.models import Order
        order = Order.objects.latest('id')
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 300.00)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertEqual(email.subject, "FruitCart - Order Confirmed 🍎")
        self.assertIn("Hi mukesh,", email.body)
        self.assertIn(f"Order ID: FC{1000 + order.pk}", email.body)
        self.assertIn("• Kiwi x2", email.body)
        self.assertIn("Total: ₹300", email.body)
        self.assertIn("Estimated Delivery:", email.body)


class WishlistTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.category = Category.objects.create(name="Citrus", slug="citrus")
        self.fruit = Fruit.objects.create(
            category=self.category,
            name="Lemon",
            slug="lemon",
            price=5.00,
            stock=100,
            is_available=True,
            unit="piece"
        )
        self.client = Client()

    def test_anonymous_redirect_on_wishlist_page(self):
        # Visiting wishlist page anonymous should redirect to login
        response = self.client.get(reverse('store:wishlist'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_anonymous_redirect_on_wishlist_toggle(self):
        # Toggling wishlist anonymous should return 401 with redirect url
        response = self.client.post(
            reverse('store:wishlist_toggle', args=[self.fruit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn(reverse('accounts:login'), data['redirect_url'])

    def test_logged_in_wishlist_toggle(self):
        self.client.login(username="testuser", password="password")

        # 1. Add to wishlist
        response = self.client.post(
            reverse('store:wishlist_toggle', args=[self.fruit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['added'])
        self.assertEqual(data['wishlist_count'], 1)

        # Verify in DB
        from store.models import Wishlist
        self.assertTrue(Wishlist.objects.filter(user=self.user, fruit=self.fruit).exists())

        # 2. View on wishlist page
        response = self.client.get(reverse('store:wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lemon")

        # 3. Remove from wishlist
        response = self.client.post(
            reverse('store:wishlist_toggle', args=[self.fruit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['added'])
        self.assertEqual(data['wishlist_count'], 0)

        # Verify deleted in DB
        self.assertFalse(Wishlist.objects.filter(user=self.user, fruit=self.fruit).exists())

    def test_wishlist_move_to_cart(self):
        self.client.login(username="testuser", password="password")

        # Add to wishlist first
        from store.models import Wishlist
        Wishlist.objects.create(user=self.user, fruit=self.fruit)

        # Move to cart
        response = self.client.post(
            reverse('store:wishlist_move_to_cart', args=[self.fruit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)
        self.assertEqual(data['wishlist_count'], 0)

        # Verify in DB
        self.assertFalse(Wishlist.objects.filter(user=self.user, fruit=self.fruit).exists())


