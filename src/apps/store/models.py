from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

from apps.category.models import Category
from core.utils import unique_slug_generator


class ProductManager(models.Manager):
    def all(self):
        return super().filter(is_available=True)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=65, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='images/products/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product-detail',
                       kwargs={'product_slug': self.slug, 'category_slug': self.category.slug})


@receiver(pre_save, sender=Product)
def pre_save_slug_generator(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


VARIATION_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size')
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices=VARIATION_CHOICES)
    variation_value = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product.name
