from django.db.models import F
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from .models import Order, Product


@receiver(m2m_changed, sender=Order.products.through)
def update_order_total_amount(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        total_amount = instance.products.all().count()
        if instance.total_amount != total_amount:
            instance.total_amount = total_amount
            instance.save()

            Order.objects.bulk_update([instance], ['total_amount'])


@receiver(m2m_changed, sender=Order.products.through)
def update_product_sold_items_count(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ['post_add', 'post_remove']:
        products = model.objects.filter(pk__in=pk_set)

        updates = []

        for product in products:
            if action == 'post_add':
                updates.append(Product(id=product.id, sold_items_count=F('sold_items_count') + 1))
            elif action == 'post_remove':
                updates.append(Product(id=product.id, sold_items_count=F('sold_items_count') - 1))

        Product.objects.bulk_update(updates, ['sold_items_count'])


@receiver(pre_delete, sender=Order)
def update_product_sold_items_count_on_order_delete(sender, instance, **kwargs):
    products = instance.products.all()
    updates = []
    for product in products:
        updates.append(Product(id=product.id, sold_items_count=F('sold_items_count') - 1))

    Product.objects.bulk_update(updates, ['sold_items_count'])
