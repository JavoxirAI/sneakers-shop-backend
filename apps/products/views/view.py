from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from apps.products.models import Product
from apps.products.serializers.serializers import ProductListSerializer, ProductCreateUpdateSerializer


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category', 'brand').prefetch_related('images', 'sizes').all()

        search = request.GET.get('search')
        if search:
            products = products.filter(name__icontains=search)

        gender = request.GET.get('gender')
        brand = request.GET.get('brand')  # brand ID
        color = request.GET.get('color')  # HEX kod (masalan: #FF5733)
        size = request.GET.get('size')  # O'lcham (masalan: 42, M, L)
        material = request.GET.get('material')
        min_price = request.GET.get('minPrice')
        max_price = request.GET.get('maxPrice')

        if gender:
            products = products.filter(gender=gender)

        if brand:
            products = products.filter(brand_id=brand)

        if color:
            products = products.filter(color_hex__iexact=color)

        if size:
            products = products.filter(sizes__size__iexact=size).distinct()

        if material:
            products = products.filter(material__icontains=material)

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    """
    GET: Bitta mahsulotni olish
    PUT: Mahsulotni yangilash
    DELETE: Mahsulotni o'chirish
    """
    try:
        product = Product.objects.select_related('category', 'brand').prefetch_related('images', 'sizes').get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductListSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductCreateUpdateSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)