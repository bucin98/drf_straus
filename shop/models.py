from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sold_items_count = models.IntegerField(default=0, verbose_name='Количество проданных товаров')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    customer_name = models.CharField(max_length=100, verbose_name='Имя заказчика')
    products = models.ManyToManyField(Product, verbose_name='Товары в заказе')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Общая сумма заказа')
    order_date = models.DateField(auto_now_add=True, verbose_name='Дата заказа')

    def __str__(self):
        return f"{self.customer_name}_{self.order_date}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
