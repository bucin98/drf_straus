import random
import os
import django

import sys
sys.path.append('/app')
from shop.models import Category, Product

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Straus.settings")
django.setup()

data = {
    "cloth": ["T-shirt", "Jeans", "Dress", "Sweater", "Jacket", "Skirt", "Shorts", "Hoodie"],
    "jewel": ["Necklace", "Ring", "Earrings", "Bracelet", "Brooch", "Watch", "Anklet", "Cufflinks"],
    "shoes": ["Sneakers", "Boots", "Sandals", "Flats", "Heels", "Loafers", "Oxfords", "Slippers"],
    "accessory": ["Handbag", "Hat", "Scarf", "Sunglasses", "Gloves", "Belt", "Wallet", "Umbrella"],
    "electronics": ["Smartphone", "Laptop", "Smartwatch", "Headphones", "Tablet", "Camera", "Fitness Tracker",
                    "Bluetooth Speaker"]
}


def fill_db():
    for category in data:
        cat_obj = Category.objects.create(name=category)
        for product in data[category]:
            Product.objects.create(name=product, category=cat_obj, price=random.randint(1, 100))


if __name__ == "__main__":
    fill_db()
