from rest_framework.test import APITestCase
from rest_framework import status
from .models import Order, Product, Category


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', category=self.category, price=10.0)
        self.order_data = {'customer_name': 'Test Customer', 'products': [self.product.id]}

    def test_create_order(self):
        url = '/api/v1/orders/'
        response = self.client.post(url, self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get()
        self.assertEqual(order.customer_name, 'Test Customer')

        product = order.products.first()
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.sold_items_count, 1)  # Assuming sold_items_count starts from 0
        self.assertEqual(order.total_amount, 10.0)

    def test_retrieve_order(self):
        order = Order.objects.create(customer_name='Test Customer')
        order.products.add(self.product)

        url = f'/api/v1/orders/{order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['customer_name'], 'Test Customer')

        product_data = response.data['products'][0]
        self.assertEqual(product_data['name'], 'Test Product')
        self.assertEqual(product_data['category']['name'], 'Test Category')

    def test_update_order_products(self):
        initial_product = Product.objects.create(name='Initial Product', category=self.category, price=15.0)

        order = Order.objects.create(customer_name='Test Customer')
        order.products.add(initial_product)

        new_product = Product.objects.create(name='New Product', category=self.category, price=20.0)

        updated_data = {'products': [new_product.id]}
        url = f'/api/v1/orders/{order.id}/'
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_order = Order.objects.get(id=order.id)

        self.assertEqual(updated_order.customer_name, 'Test Customer')

        updated_product = updated_order.products.first()
        self.assertEqual(updated_product.name, 'New Product')
        self.assertEqual(updated_product.sold_items_count, 1)  # Assuming sold_items_count starts from 0
        self.assertEqual(updated_order.total_amount, 20.0)

    def test_delete_order(self):
        order = Order.objects.create(customer_name='Test Customer')
        order.products.add(self.product)

        url = f'/api/v1/orders/{order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.sold_items_count, -1)

    def test_list_orders(self):
        order_1 = Order.objects.create(customer_name='Test Customer')
        order_1.products.add(self.product)

        Order.objects.create(customer_name='Test Customer2')

        url = '/api/v1/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_order_data = response.data[0]
        self.assertEqual(first_order_data['customer_name'], 'Test Customer')

        first_order_products = first_order_data['products']
        self.assertEqual(first_order_products[0]['name'], 'Test Product')
        self.assertEqual(first_order_products[0]['category']['name'], 'Test Category')
