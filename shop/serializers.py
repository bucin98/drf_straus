from rest_framework import serializers
from .models import Category, Product, Order


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer_name', 'total_amount', 'order_date']
        read_only_fields = ['total_amount']


class CatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ProdListSerializer(serializers.ModelSerializer):
    category = CatListSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'category']


class OrderListSerializer(serializers.ModelSerializer):
    products = ProdListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'order_date', 'products']
