from django.urls import path
from .views import OrderListCreateView, OrderRetrieveUpdateDeleteView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderRetrieveUpdateDeleteView().as_view(), name='order_edit')
]
