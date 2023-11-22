from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order, Product, Category

from django.test import TestCase
from django.db.models.signals import m2m_changed, pre_delete
from .signals import update_order_total_amount, update_product_sold_items_count, \
    update_product_sold_items_count_on_order_delete


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', category=self.category, price=10.0)
        self.order_data = {'customer_name': 'Test Customer', 'products': [self.product.name]}

    def test_create_order(self):
        url = '/api/v1/orders/'
        response = self.client.post(url, self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().customer_name, 'Test Customer')

    def test_retrieve_order(self):
        order = Order.objects.create(customer_name='Test Customer')
        url = f'/api/v1/orders/{order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['customer_name'], 'Test Customer')

    def test_update_order_products(self):
        initial_product = Product.objects.create(name='Initial Product', category=self.category, price=15.0)

        order = Order.objects.create(customer_name='Test Customer')
        order.products.add(initial_product)

        new_product = Product.objects.create(name='New Product', category=self.category, price=20.0)

        updated_data = {'products': [new_product.name]}
        url = f'/api/v1/orders/{order.id}/'
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_order = Order.objects.get(id=order.id)
        self.assertEqual(updated_order.products.count(), 1)
        self.assertEqual(updated_order.products.first().name, 'New Product')

        self.assertEqual(updated_order.customer_name, 'Test Customer')

    def test_delete_order(self):
        order = Order.objects.create(customer_name='Test Customer')
        url = f'/api/v1/orders/{order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_list_orders(self):
        Order.objects.create(customer_name='Test Customer')
        Order.objects.create(customer_name='Test Customer2')

        url = reverse('order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['customer_name'], 'Test Customer')
        self.assertEqual(response.data[1]['customer_name'], 'Test Customer2')


class SignalTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

        self.product1 = Product.objects.create(name='Product 1', category=self.category, price=10.00)
        self.product2 = Product.objects.create(name='Product 2', category=self.category, price=20.00)

        self.order = Order.objects.create(customer_name='John Doe')
        self.order.products.add(self.product1, self.product2)

    def test_update_order_total_amount_signal(self):
        m2m_changed.connect(update_order_total_amount, sender=Order.products.through)
        self.order.products.add(Product.objects.create(name='New Product', category=self.category, price=15.00))
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, self.order.products.count())

    def test_update_product_sold_items_count_signal(self):
        m2m_changed.connect(update_product_sold_items_count, sender=Order.products.through)
        initial_count_product1 = self.product1.sold_items_count
        initial_count_product2 = self.product2.sold_items_count

        new_product = Product.objects.create(name='New Product', category=self.category, price=15.00)
        self.order.products.add(new_product)

        self.product1.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product1.sold_items_count, initial_count_product1 + 1)
        self.assertEqual(self.product2.sold_items_count, initial_count_product2 + 1)

    def test_update_product_sold_items_count_on_order_delete_signal(self):
        # Trigger the pre_delete signal to update sold_items_count in Product model
        pre_delete.connect(update_product_sold_items_count_on_order_delete, sender=Order)
        self.product1.sold_items_count = 1
        self.product2.sold_items_count = 1

        self.order.delete()

        self.product1.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product1.sold_items_count, 0)
        self.assertEqual(self.product2.sold_items_count, 0)
