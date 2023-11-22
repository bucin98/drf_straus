from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order, Product, Category


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
