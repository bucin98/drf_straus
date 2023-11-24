from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Order, Product
from .serializers import OrderCreateUpdateSerializer, OrderListSerializer
from .utils import count_total_amount, validate_data, check_products_exist


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('products__category').all()
    serializer_class = OrderListSerializer

    def create(self, request, *args, **kwargs):
        validated_data = validate_data(request.data, 'create')
        if isinstance(validated_data, Response):
            return validated_data

        customer_name, products_ids = validated_data
        try:
            products = Product.objects.filter(id__in=products_ids)
            not_exist_response = check_products_exist(products, products_ids)
            if not_exist_response:
                return not_exist_response

            with transaction.atomic():
                total_amount = count_total_amount(products)
                order = Order.objects.create(customer_name=customer_name, total_amount=total_amount)

                order_product_m2m = Order.products.through
                order_products = [order_product_m2m(order=order, product=product) for product in products]
                order_product_m2m.objects.bulk_create(order_products)
                products.update(sold_items_count=F('sold_items_count') + 1)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order_serializer = OrderCreateUpdateSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order.objects.prefetch_related('products'), id=pk)

        validated_data = validate_data(request.data, 'update')
        if isinstance(validated_data, Response):
            return validated_data

        customer_name, new_products_ids = validated_data

        old_product_ids = Order.products.through.objects.filter(order_id=order.id).values_list('product_id', flat=True)

        products = Product.objects.filter(id__in=new_products_ids)
        not_exist_response = check_products_exist(products, new_products_ids)
        if not_exist_response:
            return not_exist_response

        with transaction.atomic():
            Product.objects.filter(id__in=old_product_ids).update(sold_items_count=F('sold_items_count') - 1)
            Product.objects.filter(id__in=new_products_ids).update(sold_items_count=F('sold_items_count') + 1)

            Order.products.through.objects.filter(order_id=order.id).delete()
            new_order_products = [Order.products.through(order_id=order.id, product_id=product.id) for product in
                                  products]
            Order.products.through.objects.bulk_create(new_order_products)

            order.total_amount = count_total_amount(products)
            order.save()

            order_serializer = OrderCreateUpdateSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order.objects.prefetch_related('products'), id=pk)

        try:

            with transaction.atomic():
                order.products.update(sold_items_count=F('sold_items_count') - 1)
                order.delete()

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)
