from django.urls import path
from apps.orders.views.views import *

app_name = "orders"

urlpatterns = [
    path('', order_list, name='order-list'),
    path('create/', create_order, name='create-order'),
    path('<int:pk>/', order_detail, name='order-detail'),
    path('<int:pk>/cancel/', cancel_order, name='cancel-order'),
]