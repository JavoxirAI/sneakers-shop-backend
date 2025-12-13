from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.products.models import Product, Size


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Kutilmoqda')),
        ('confirmed', _('Tasdiqlangan')),
        ('processing', _('Tayyorlanmoqda')),
        ('shipped', _('Yetkazilmoqda')),
        ('delivered', _('Yetkazilgan')),
        ('cancelled', _('Bekor qilingan')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Naqd pul')),
        ('card', _('Karta')),
        ('payme', _('Payme')),
        ('click', _('Click')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Foydalanuvchi")
    )
    status = models.CharField(
        _("Holat"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Yetkazib berish ma'lumotlari
    full_name = models.CharField(_("To'liq ism"), max_length=255)
    phone = models.CharField(_("Telefon"), max_length=20)
    address = models.TextField(_("Manzil"))
    city = models.CharField(_("Shahar"), max_length=100)
    region = models.CharField(_("Viloyat"), max_length=100, blank=True)
    postal_code = models.CharField(_("Pochta indeksi"), max_length=20, blank=True)

    # To'lov ma'lumotlari
    payment_method = models.CharField(
        _("To'lov usuli"),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    is_paid = models.BooleanField(_("To'langan"), default=False)
    paid_at = models.DateTimeField(_("To'lov sanasi"), null=True, blank=True)

    # Narx ma'lumotlari
    subtotal = models.DecimalField(_("Mahsulotlar narxi"), max_digits=10, decimal_places=2)
    delivery_price = models.DecimalField(_("Yetkazib berish narxi"), max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(_("Umumiy narx"), max_digits=10, decimal_places=2)

    # Qo'shimcha
    note = models.TextField(_("Izoh"), blank=True)

    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan sana"), auto_now=True)

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Buyurtma")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Mahsulot")
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("O'lcham")
    )
    quantity = models.PositiveIntegerField(_("Miqdor"))
    price = models.DecimalField(_("Narx"), max_digits=10, decimal_places=2)  # Buyurtma vaqtidagi narx

    created_at = models.DateTimeField(_("Yaratilgan sana"), auto_now_add=True)

    class Meta:
        verbose_name = _("Buyurtma mahsuloti")
        verbose_name_plural = _("Buyurtma mahsulotlari")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        """Har bir item uchun umumiy narx"""
        return self.price * self.quantity