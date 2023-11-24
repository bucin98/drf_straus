from rest_framework import status
from rest_framework.response import Response

from shop.models import Product


def count_total_amount(products: list[Product]) -> float:
    total_amount = sum([product.price for product in products])
    return float(total_amount)


def validate_data(data: dict, method) -> tuple | Response:
    customer_name = data.get('customer_name', None)
    products_ids = data.get('products', [])

    if not products_ids or not isinstance(products_ids, list) or not all(isinstance(x, int) for x in products_ids):
        return Response(
            {"error": "Field products should be a non empy list of ids"},
            status=status.HTTP_400_BAD_REQUEST)

    if method == 'create' and not customer_name:
        return Response(
            {"error": "Field customer_name not provided"},
            status=status.HTTP_400_BAD_REQUEST)

    return customer_name, products_ids


def check_products_exist(existing_products: list[Product], requested_products_ids: list[int]) -> Response | None:
    if len(existing_products) != len(requested_products_ids):
        existing_ids = {product.id for product in existing_products}
        missing = set(requested_products_ids) - existing_ids
        return Response(data={"error": f"Products with ids {missing} do not exist."},
                        status=status.HTTP_404_NOT_FOUND)
    return None
