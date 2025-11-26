from rest_framework import serializers

from apps.brands.serializers.serializers import BrandSerializer
from apps.categories.serializers.serializers import CategorySerializer
from apps.products.models import ProductImage, Size, Product


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'created_at']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size', 'stock']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'brand', 'price',
            'gender', 'gender_display', 'color_hex', 'material',
            'is_popular', 'is_new', 'rating', 'images', 'sizes',
            'created_at', 'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'brand', 'price',
            'gender', 'color_hex', 'material', 'is_popular', 'is_new',
            'rating', 'sizes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        sizes_data = validated_data.pop('sizes', [])
        product = Product.objects.create(**validated_data)

        for size_data in sizes_data:
            Size.objects.create(product=product, **size_data)

        return product

    def update(self, instance, validated_data):
        sizes_data = validated_data.pop('sizes', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sizes_data is not None:
            instance.sizes.all().delete()
            for size_data in sizes_data:
                Size.objects.create(product=instance, **size_data)

        return instance