from rest_framework import serializers
from .models import Category, Product, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
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
