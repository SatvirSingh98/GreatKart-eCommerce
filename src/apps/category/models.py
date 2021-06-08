from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

from core.utils import unique_slug_generator


class Category(models.Model):
    name = models.CharField(unique=True, max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/categories/', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:products-by-category', kwargs={'category_slug': self.slug})


@receiver(pre_save, sender=Category)
def pre_save_slug_generator(instance, sender, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
