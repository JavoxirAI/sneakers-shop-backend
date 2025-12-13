from django.urls import path, include

urlpatterns = [
    path('products/', include('apps.products.urls.v1', namespace='products')),
    path('categories/', include('apps.categories.urls.v1', namespace='categories')),
    path('brands/', include('apps.brands.urls.v1', namespace='brands')),
    path('users/', include('apps.users.urls.v1', namespace='users')),
    path('cart/', include('apps.cart.urls.v1', namespace='cart')),
    path('favorites/', include('apps.favorites.urls.v1', namespace='favorites')),
    path('orders/', include('apps.orders.urls.v1', namespace='orders')),
    path('shared/', include('apps.shared.urls', namespace='shared')),
]