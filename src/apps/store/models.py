from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.category.models import Category
from core.utils import unique_slug_generator


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

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Product)
def pre_save_slug_generator(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
