from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from django.utils import timezone
from slugger import AutoSlugField


def upload_location_customer(instance, filename):
    return f'images/customer/{instance.user.username}/{filename}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=40, default='unknown')
    mobile = models.CharField(max_length=20, null=False, default='unknown')
    profile_img = models.ImageField(upload_to=upload_location_customer,
                                    null=True, blank=True,
                                    height_field='height_field',
                                    width_field='width_field')
    height_field = models.IntegerField(blank=False,
                                       null=True,
                                       default=0)
    width_field = models.IntegerField(blank=False,
                                      null=True,
                                      default=0)

    def img_preview(self):
        if self.profile_img and hasattr(self.profile_img, 'url'):
            return mark_safe(f'<img src = "{self.profile_img.url}" width = "75"/>')
        else:
            return "img"

    class Meta:
        ordering = ('user',)
        verbose_name = 'Customer'
        verbose_name_plural = "Customers"

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name


def upload_location_category(instance, filename):
    return f'images/category/{instance.name}/{filename}'


class Category(models.Model):
    name = models.CharField(max_length=200, blank=False, db_index=True)
    description = models.TextField(max_length=600, blank=False, null=True)
    slug = AutoSlugField(populate_from='name', unique=True, null=True)
    category_img = models.ImageField(
        upload_to=upload_location_category,
        blank=True,
        null=True,
        height_field='height_field',
        width_field='width_field'
    )
    height_field = models.IntegerField(blank=False,
                                       null=True,
                                       default=0)
    width_field = models.IntegerField(blank=False, null=True, default=0)

    def img_preview(self):
        if self.category_img and hasattr(self.category_img, 'url'):
            return mark_safe(f'<img src = "{self.category_img.url}" width = "75"/>')
        else:
            return "img"

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = "Categories"

    def get_absolute_url(self):
        return reverse('New_Shop:product',
                       args=[self.slug])

    def __str__(self):
        return self.name


def upload_location_product(instance, filename):
    return f'images/{instance.category}/{instance.name}/{filename}'


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=1, blank=False, null=True,
        on_delete=models.SET_NULL,

    )
    name = models.CharField(max_length=200, blank=False, db_index=True)
    slug = AutoSlugField(populate_from='name', unique=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=00.00)
    description = models.TextField(max_length=600, blank=False)
    url = models.URLField(max_length=200, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    product_img = models.ImageField(
        upload_to=upload_location_product,
        blank=True, null=True,
        height_field='height_field',
        width_field='width_field'
    )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    stock = models.PositiveIntegerField(null=True, default=0)  # Поле для зберігання залишків продукта
    available = models.BooleanField(default=True)  # Покаже чи доступний чи ні продукт
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def img_preview(self):
        if self.product_img and hasattr(self.product_img, 'url'):
            return mark_safe(f'<img src = "{self.product_img.url}" width = "75"/>')
        else:
            return "img"

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def get_absolute_url(self):
        return reverse('New_Shop:detail',
                       args=[self.id, self.slug])

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ManyToManyField('Product', blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100, null=True)
    house = models.CharField(max_length=100, null=True)
    apartment = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    quantity = models.PositiveIntegerField(null=True, default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Order'
        verbose_name_plural = "Orders"

    def customer_username(self):
        return self.customer.user.username

    def __str__(self):
        return self.customer.user.username


class SubscribedUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=100)
    created_date = models.DateTimeField('Date created', default=timezone.now)

    def __str__(self):
        return self.email


class PromoCode(models.Model):
    promo_code = models.CharField(max_length=20, unique=True, default='code')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=00.00)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    max_use = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.promo_code

    def is_valid(self):
        return self.used_count < self.max_use

    def is_expired(self):
        return timezone.now() > self.end_date


class AppliedPromoCode(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.order} - {self.promo_code}"

