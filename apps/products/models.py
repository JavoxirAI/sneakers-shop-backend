from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from apps.brands.models import Brand
from apps.categories.models import Category


class Product(models.Model):
    GENDER_CHOICES = [
        ('male', _('Erkak')),
        ('female', _('Ayol')),
    ]

    name = models.CharField(_("Mahsulot nomi"), max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Kategoriya")
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Brand")
    )
    price = models.DecimalField(_("Narx"), max_digits=10, decimal_places=2)
    gender = models.CharField(_("Jins"), max_length=10, choices=GENDER_CHOICES)
    color_hex = models.CharField(_("Rang HEX kodi"), max_length=7, help_text="Masalan: #FF5733")
    material = models.CharField(_("Material"), max_length=100)
    is_popular = models.BooleanField(_("Mashhur"), default=False)
    is_new = models.BooleanField(_("Yangi"), default=False)
    rating = models.FloatField(_("Reyting"), default=0.0)
    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan sana"), auto_now=True)

    class Meta:
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Mahsulot")
    )
    image = models.ImageField(_("Rasm"), upload_to='products/')
    is_main = models.BooleanField(_("Asosiy rasm"), default=False)
    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)

    class Meta:
        verbose_name = _("Mahsulot rasmi")
        verbose_name_plural = _("Mahsulot rasmlari")
        ordering = ['-is_main', '-created_at']

    def __str__(self):
        return f"{self.product.name} - Image"


class Size(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sizes',
        verbose_name=_("Mahsulot")
    )
    size = models.CharField(_("O'lcham"), max_length=10)
    stock = models.PositiveIntegerField(_("Qoldiq"), default=0)
    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan sana"), auto_now=True)

    class Meta:
        verbose_name = _("O'lcham")
        verbose_name_plural = _("O'lchamlar")
        unique_together = ['product', 'size']

    def __str__(self):
        return f"{self.product.name} - {self.size}"