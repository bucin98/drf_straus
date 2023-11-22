from django.db import transaction, IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Order, Product
from .serializers import OrderSerializer, OrderListSerializer, OrderCreateUpdateSerializer


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

        order_serializer = OrderCreateUpdateSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderCreateUpdateSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        if self.request.method == 'DELETE':
            return Order.objects.prefetch_related('products').all()
        elif self.request.method in ['PUT', 'PATCH']:
            return Order.objects.all()
        else:
            return Order.objects.prefetch_related('products__category').all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        products_names = request.data.get('products', None)

        if not isinstance(products_names, list):
            return Response({"error": "The request should contain a list of products."},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_products = Product.objects.filter(name__in=products_names)

        if len(existing_products) != len(products_names):
            missing = set(products_names) - {product.name for product in existing_products}
            return Response({"error": f"Products {missing} do not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            Order.products.through.objects.filter(order_id=instance.id).delete()
            new_order_products = [Order.products.through(order_id=instance.id, product_id=product.id) for product in
                                  existing_products]

            Order.products.through.objects.bulk_create(new_order_products)

        serializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)
