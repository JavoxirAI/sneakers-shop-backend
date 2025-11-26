from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from apps.products.models import *


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class SizeInline(admin.TabularInline):
    model = Size
    extra = 1


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['id', 'name', 'category', 'brand', 'price', 'gender', 'color_hex', 'rating', 'is_popular', 'is_new']
    list_filter = ['category', 'brand', 'gender', 'is_popular', 'is_new']
    search_fields = ['name', 'material']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, SizeInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'is_main', 'created_at']
    list_filter = ['is_main']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'size', 'stock']
    search_fields = ['product__name', 'size']