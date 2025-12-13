from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.orders.models import Order, OrderItem
from apps.orders.serializers.serializers import OrderSerializer, CreateOrderSerializer
from apps.products.models import Product, Size


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    """
    Foydalanuvchi buyurtmalari ro'yxati
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product', 'items__size')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Buyurtma yaratish (items bilan)
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    items_data = serializer.validated_data.get('items', [])

    if not items_data:
        return Response({'error': 'items bo\'sh bo\'lishi mumkin emas'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Subtotal hisoblash va items tekshirish
            subtotal = 0
            order_items = []

            for item_data in items_data:
                product_id = item_data['product_id']
                size_name = item_data.get('size')  # ✅ size nomi (masalan: "42")
                quantity = item_data['quantity']

                # Product olish
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise Exception(f'Mahsulot topilmadi (ID: {product_id})')

                # Size olish (ixtiyoriy)
                size = None
                if size_name:
                    try:
                        size = Size.objects.get(product=product, size=size_name)
                    except Size.DoesNotExist:
                        raise Exception(f'{product.name} uchun "{size_name}" o\'lchami topilmadi')

                    # Stock tekshirish
                    if size.stock < quantity:
                        raise Exception(
                            f'{product.name} ({size_name}) uchun yetarli mahsulot yo\'q. Mavjud: {size.stock}')

                # Subtotal ga qo'shish
                item_subtotal = product.price * quantity
                subtotal += item_subtotal

                order_items.append({
                    'product': product,
                    'size': size,
                    'quantity': quantity,
                    'price': product.price
                })

            # Order yaratish
            delivery_price = serializer.validated_data.get('delivery_price', 0)
            total_price = subtotal + delivery_price

            order = Order.objects.create(
                user=request.user,
                full_name=serializer.validated_data['full_name'],
                phone=serializer.validated_data['phone'],
                address=serializer.validated_data['address'],
                city=serializer.validated_data['city'],
                region=serializer.validated_data.get('region', ''),
                postal_code=serializer.validated_data.get('postal_code', ''),
                payment_method=serializer.validated_data['payment_method'],
                subtotal=subtotal,
                delivery_price=delivery_price,
                total_price=total_price,
                note=serializer.validated_data.get('note', ''),
                status='pending'
            )

            # OrderItem yaratish va stock'dan ayirish
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    size=item['size'],
                    quantity=item['quantity'],
                    price=item['price']
                )

                # Stock'dan ayirish
                if item['size']:
                    item['size'].stock -= item['quantity']
                    item['size'].save()

            return Response({
                'message': 'Buyurtma muvaffaqiyatli yaratildi',
                'order': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    """
    Buyurtma tafsilotlari
    """
    try:
        order = Order.objects.prefetch_related('items__product', 'items__size').get(
            id=pk,
            user=request.user
        )
    except Order.DoesNotExist:
        return Response({'error': 'Buyurtma topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, pk):
    """
    Buyurtmani bekor qilish
    """
    try:
        order = Order.objects.get(id=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Buyurtma topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    # Faqat pending va confirmed holatdagi buyurtmalarni bekor qilish mumkin
    if order.status not in ['pending', 'confirmed']:
        return Response({
            'error': 'Faqat kutilayotgan yoki tasdiqlangan buyurtmalarni bekor qilish mumkin'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Stock'ni qaytarish
    with transaction.atomic():
        for item in order.items.all():
            if item.size:
                item.size.stock += item.quantity
                item.size.save()

        order.status = 'cancelled'
        order.save()

    return Response({
        'message': 'Buyurtma bekor qilindi',
        'order': OrderSerializer(order).data
    })