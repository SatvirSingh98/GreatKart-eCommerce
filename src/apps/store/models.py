from django.conf import settings
from django.db import models
from django.db.models.aggregates import Avg, Count
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

from apps.category.models import Category
from core.utils import unique_slug_generator

User = settings.AUTH_USER_MODEL


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

    def average_rating(self):
        reviews = ReviewModel.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def count_reviews(self):
        reviews = ReviewModel.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = float(reviews['count'])
        return count


@receiver(pre_save, sender=Product)
def pre_save_slug_generator(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


VARIATION_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size')
)


class VariationManager(models.Manager):
    def colors(self):
        return super().filter(variation_category='color', is_active=True)

    def sizes(self):
        return super().filter(variation_category='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices=VARIATION_CHOICES)
    variation_value = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=False)
    is_active = models.BooleanField(default=True)

    objects = VariationManager()

    def __str__(self):
        return f'{self.product.name} - ({self.variation_category}: {self.variation_value})'


class ReviewModel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField(blank=True, max_length=500)
    rating = models.FloatField()
    ip = models.CharField(blank=True, max_length=20)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to='store/products', max_length=255)

    class Meta:
        verbose_name_plural = 'Product gallery'

    def __str__(self):
        return self.product.name
