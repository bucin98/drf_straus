from django.db import transaction, IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order, Product
from .serializers import OrderSerializer, OrderListSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('products__category').all()
    serializer_class = OrderListSerializer

    def create(self, request, *args, **kwargs):
        customer_name = request.data.get('customer_name', None)
        product_names = request.data.get('products', [])

        if customer_name is None or not isinstance(product_names, list) or not product_names:
            return Response(
                {"error": "Both customer_name and products are required and should be in the correct format."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                products = Product.objects.select_related('category').filter(name__in=product_names)

                if len(product_names) != len(products):
                    missing = set(product_names) - {product.name for product in products}
                    raise Product.DoesNotExist(f"Products with names {missing} do not exist.")

                order = Order.objects.create(customer_name=customer_name)
                OrderProduct = Order.products.through
                order_products = [OrderProduct(order=order, product=product) for product in products]

                OrderProduct.objects.bulk_create(order_products)

        except Product.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"error": "An error occurred while creating the order. Please try again."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order_data = {
            'id': order.id,
            'customer_name': order.customer_name,
            'order_date': order.order_date,
            'products': [{'name': product.name, 'category': {'name': product.category.name}} for product in products]
        }

        return Response(order_data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.prefetch_related('products__category').all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        products_names = request.data.get('products', None)

        if not isinstance(products_names, list):
            return Response({"error": "The request should contain a list of products."},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_products = Product.objects.filter(name__in=products_names)

        if existing_products.count() != len(products_names):
            return Response({"error": "Some products do not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            Order.products.through.objects.filter(order_id=instance.id).delete()
            new_order_products = [Order.products.through(order_id=instance.id, product_id=product.id) for product in
                                  existing_products]

            Order.products.through.objects.bulk_create(new_order_products)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
